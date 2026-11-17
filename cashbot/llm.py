"""LangChain Runnable adapters for OpenAI Responses and Claude Messages."""
import json
import os
import sqlite3
import time
from datetime import datetime, timezone

import httpx
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from .settings import ROOT

PROVIDERS = {
    "openai": ("OPENAI_API_KEY", "OPENAI_MODEL", "gpt-4.1-mini", "https://api.openai.com/v1/responses"),
    "anthropic": ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "claude-sonnet-5-5", "https://api.anthropic.com/v1/messages"),
}


def configured_provider(task="review"):
    return os.getenv("DRAFT_PROVIDER" if task == "draft" else "LLM_PROVIDER",
                     "anthropic" if task == "draft" else "openai").strip().lower()


def provider_config(provider):
    if provider not in PROVIDERS:
        raise ValueError("Provider must be openai or anthropic.")
    key_name, model_name, default_model, url = PROVIDERS[provider]
    key = os.getenv(key_name, "").strip()
    if not key or key == "paste_your_key_here":
        raise ValueError(f"Set {key_name} privately in .env. Demo mode needs no key.")
    return key, os.getenv(model_name, default_model).strip(), url


def validate_config():
    for provider in {configured_provider(), configured_provider("draft")}:
        provider_config(provider)


def reserve_call():
    # A request-count guard, not a rupee spending guarantee. Includes failed attempts.
    today = datetime.now(timezone.utc).date().isoformat()
    limit = int(os.getenv("MAX_API_CALLS_PER_DAY", "30"))
    with sqlite3.connect(ROOT / "data/budget.sqlite") as db:
        db.execute("CREATE TABLE IF NOT EXISTS calls(day TEXT PRIMARY KEY, n INTEGER NOT NULL)")
        db.execute("BEGIN IMMEDIATE")
        current = db.execute("SELECT n FROM calls WHERE day=?", (today,)).fetchone()
        if current and current[0] >= limit:
            raise ValueError("Daily API request limit reached. Wait or review your budget settings.")
        db.execute("INSERT INTO calls VALUES(?,1) ON CONFLICT(day) DO UPDATE SET n=n+1", (today,))


def complete(prompt_value, provider=None):
    provider = provider or configured_provider()
    key, model, url = provider_config(provider)
    roles = {"human": "user", "ai": "assistant", "system": "system"}
    messages = [{"role": roles[m.type], "content": m.content}
                for m in prompt_value.to_messages()]
    if provider == "openai":
        headers = {"Authorization": f"Bearer {key}"}
        body = {"model": model, "input": messages, "max_output_tokens": 4000, "store": False}
    else:
        headers = {"x-api-key": key, "anthropic-version": "2026-10-21"}
        body = {"model": model, "max_tokens": 6000,
                "system": "\n\n".join(m["content"] for m in messages if m["role"] == "system"),
                "messages": [m for m in messages if m["role"] != "system"]}
    for attempt in range(2):
        reserve_call()
        with httpx.Client(timeout=90, follow_redirects=False) as client:
            response = client.post(url, headers=headers, json=body)
        if response.status_code in (429, 502, 503, 504, 529) and attempt == 0:
            time.sleep(3)
            continue
        if not response.is_success:
            raise ValueError(f"{provider} HTTP {response.status_code}. Check model access, credit and key.")
        try:
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("Provider returned an invalid response; no draft accepted.")
            if provider == "openai":
                if payload.get("status") != "completed":
                    raise ValueError("OpenAI response incomplete or failed; no draft accepted.")
                blocks = [block for item in payload["output"] if item.get("type") == "message"
                          for block in item.get("content", [])]
                text = "\n".join(b["text"] for b in blocks if b.get("type") == "output_text")
                refused = any(b.get("type") == "refusal" for b in blocks)
            else:
                if payload.get("stop_reason") not in ("end_turn", "stop_sequence"):
                    raise ValueError("Claude response truncated, refused or unfinished; no draft accepted.")
                text = "\n".join(b["text"] for b in payload["content"] if b.get("type") == "text")
                refused = False
            if refused or not isinstance(text, str) or not text.strip():
                raise ValueError("Provider returned no usable text or refused the request.")
        except (KeyError, TypeError, AttributeError, json.JSONDecodeError):
            raise ValueError("Provider returned an invalid response; no draft accepted.") from None
        return AIMessage(content=text)
    raise ValueError("Provider temporarily unavailable.")


def ask(system, payload, task="review"):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system), ("human", "{payload}")
    ])
    model = RunnableLambda(lambda value: complete(value, configured_provider(task)))
    chain = prompt | model | StrOutputParser()
    return chain.invoke({"payload": json.dumps(payload, ensure_ascii=False)})


def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)
