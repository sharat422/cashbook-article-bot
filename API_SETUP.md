# OpenAI and Claude live setup

This replaces the original tutorial's Sarvam setup. Muse is not used.
The CLI, SQLite jobs/checkpoints, offline demo and approval/export commands remain.
The existing `httpx` dependency calls both providers directly; no SDK installation is needed.

## Configure privately

Edit `.env` locally. Do not paste API keys into chat or commit them.
Use `.env.example` as a reference; do not overwrite an existing `.env` containing keys.

```dotenv
OPENAI_API_KEY=paste_your_key_here
ANTHROPIC_API_KEY=paste_your_key_here
OPENAI_MODEL=gpt-4.1-mini
ANTHROPIC_MODEL=claude-sonnet-5-5
LLM_PROVIDER=openai
DRAFT_PROVIDER=anthropic
MAX_API_CALLS_PER_DAY=30
LANGSMITH_TRACING=false
```

`LLM_PROVIDER` selects evidence extraction and review. `DRAFT_PROVIDER` selects
initial drafting and all revisions. Each accepts `openai` or `anthropic`.
The defaults above use both services. Model IDs can be changed to models available
to your accounts that support the respective text API. These are starting models,
not a claim that they are the newest or that live article quality has been verified.

Create keys in the [OpenAI API platform](https://platform.openai.com/api-keys) and
[Claude Console](https://platform.claude.com/settings/keys). Verify billing and model
access in each account. `doctor` reports key presence, not successful authentication.

## Validate each provider

From this project folder in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m cashbot doctor
.\.venv\Scripts\python.exe -m lessons.chain_basics --live --provider openai
.\.venv\Scripts\python.exe -m lessons.chain_basics --live --provider anthropic
```

These consume API credit. The shared SQLite guard counts request attempts across
both providers, including retries. It is not a currency spending cap. A normal guide
uses three requests (evidence, draft, review); each revision normally adds two.
The two live lessons add one request each. Transient retries add attempts.
There is no automatic cross-provider fallback.

New live jobs check both configured providers for missing keys before reserving a
topic. Authentication failures, incomplete/truncated output and refusals stop the
job. Provider response/error bodies and keys are not printed by the adapter.
Sources, product facts, feedback and drafts are sent to the selected providers.
OpenAI Responses requests use `store: false`; LangSmith tracing remains disabled.

## Generate and review a practical guide

```powershell
.\.venv\Scripts\python.exe -m cashbot scheduled --slot guide
```

This selects the next unused guide topic and creates the current weekly job.
Use its printed ID for `status`, `revise`, `check-edits` and `approve` as described
in the original tutorial. Review evidence, arithmetic, app claims and release wording.
Bolcash is pre-launch with an owner-planned release date of 20 November 2026, and
has no approved marketing URL. Every article still pauses for approval before export.
For a failed job, resolve the cause and use `retry`; do not reserve another topic
just to bypass a failure. Saved jobs keep their product-facts snapshot; provider
selection is read from the environment at each call.

## API references

- [OpenAI text generation and Responses](https://developers.openai.com/api/docs/guides/text)
- [OpenAI GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
- [Claude Messages](https://platform.claude.com/docs/en/api/messages/create)
- [Claude model IDs](https://platform.claude.com/docs/en/models/overview)

The adapter uses OpenAI `/v1/responses` with bearer authentication and Claude
`/v1/messages` with `x-api-key` and API version `2026-10-21`.
