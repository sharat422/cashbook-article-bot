import json
import sqlite3

import httpx
import pytest
from langchain_core.prompts import ChatPromptTemplate

from cashbot import llm


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "ROOT", tmp_path)
    (tmp_path / "data").mkdir()
    for name, value in {"OPENAI_API_KEY": "fixture-openai", "ANTHROPIC_API_KEY": "fixture-claude",
                        "OPENAI_MODEL": "fixture-gpt", "ANTHROPIC_MODEL": "fixture-sonnet",
                        "LLM_PROVIDER": "openai", "DRAFT_PROVIDER": "anthropic",
                        "MAX_API_CALLS_PER_DAY": "30"}.items():
        monkeypatch.setenv(name, value)
    return tmp_path


def response(provider, text="A fixture answer"):
    if provider == "openai":
        return {"status": "completed", "output": [{"type": "reasoning"},
                {"type": "message", "content": [{"type": "output_text", "text": text}]}]}
    return {"stop_reason": "end_turn", "content": [{"type": "thinking", "thinking": "hidden"},
            {"type": "text", "text": text}]}


def mock_client(monkeypatch, handle):
    actual = httpx.Client
    monkeypatch.setattr(llm.httpx, "Client", lambda **kw: actual(transport=httpx.MockTransport(handle), **kw))


@pytest.mark.parametrize("task,provider", [("review", "openai"), ("draft", "anthropic")])
def test_provider_contract_and_routing(api, monkeypatch, task, provider):
    system = 'Return JSON {"issues": [], "notes": []}.'
    def handle(request):
        body = json.loads(request.content)
        assert body["model"] == ("fixture-gpt" if provider == "openai" else "fixture-sonnet")
        assert "SARVAM" not in str(body)
        if provider == "openai":
            assert str(request.url) == "https://api.openai.com/v1/responses"
            assert request.headers["Authorization"] == "Bearer fixture-openai"
            assert "x-api-key" not in request.headers
            assert body["store"] is False
            assert body["input"][0] == {"role": "system", "content": system}
            assert body["max_output_tokens"] == 4000
        else:
            assert str(request.url) == "https://api.anthropic.com/v1/messages"
            assert request.headers["x-api-key"] == "fixture-claude"
            assert request.headers["anthropic-version"] == "2026-10-21"
            assert "Authorization" not in request.headers
            assert body["system"] == system
            assert [m["role"] for m in body["messages"]] == ["user"]
            assert body["max_tokens"] == 6000
        return httpx.Response(200, json=response(provider))
    mock_client(monkeypatch, handle)
    assert llm.ask(system, {"topic": "ledger"}, task=task) == "A fixture answer"


@pytest.mark.parametrize("provider,payload", [
    ("openai", {"status": "incomplete", "output": []}),
    ("openai", {"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal"}]}]}),
    ("openai", {"status": "completed", "output": []}),
    ("openai", {"status": "completed"}),
    ("anthropic", {"stop_reason": "max_tokens", "content": [{"type": "text", "text": "Partial"}]}),
    ("anthropic", {"stop_reason": "refusal", "content": []}),
    ("anthropic", {"stop_reason": "end_turn", "content": []}),
])
def test_incomplete_refused_and_malformed_responses_stop(api, monkeypatch, provider, payload):
    mock_client(monkeypatch, lambda request: httpx.Response(200, json=payload))
    prompt = ChatPromptTemplate.from_messages([("human", "hello")]).invoke({})
    with pytest.raises(ValueError):
        llm.complete(prompt, provider)


def test_missing_key_stops_before_spending(api, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "paste_your_key_here")
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        llm.validate_config()
    assert not (api / "data/budget.sqlite").exists()


def test_retry_counts_each_attempt_and_does_not_leak_errors(api, monkeypatch):
    statuses = iter([503, 200, 401])
    def handle(request):
        status = next(statuses)
        if status == 401:
            return httpx.Response(status, text="fixture-openai secret-provider-error")
        return httpx.Response(status, json=response("openai"))
    mock_client(monkeypatch, handle)
    monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)
    assert llm.ask("Be factual.", {}) == "A fixture answer"
    with sqlite3.connect(api / "data/budget.sqlite") as db:
        assert db.execute("SELECT n FROM calls").fetchone()[0] == 2
    with pytest.raises(ValueError, match="openai HTTP 401") as exc:
        llm.ask("Be factual.", {})
    assert "fixture-openai" not in str(exc.value)
    assert "secret-provider-error" not in str(exc.value)
