# Verification record

## Weekly scheduling and backlog — 6 November 2026

Enabled and tested the actual Windows tasks: Tuesday guide and Friday explainer at
09:00 Eastern. Both finished with LastTaskResult 0, complete per-slot logs and correct
skips for existing weekly jobs. Missed-start catch-up, wake request and per-task overlap
protection are enabled; the current user must remain signed in. Expanded the guide
backlog to 12 distinct note files, preserving existing IDs (11 unused). Fixed shared-log
contention and exit-code log redirection. **43 tests passed** on Python 3.12.10.
See `SCHEDULING.md` for exact settings, logs, recovery, limits and backlog maintenance.

## First approved article public — 6 November 2026

Published the approved guide through Sites static hosting after the owner confirmed
there was no existing host. Prepared and validated its Next.js static-export route
in the marketing repository: lint/type-check passed, 24 tests passed and build succeeded.
Sites deployment succeeded with public access; anonymous HTTP returned 200 for the
article and guide index. Internal editorial notes were excluded. Browser opening
timed out, so visual QA is not claimed. See `PUBLICATION_RECORD.md` for the public
URL, exact deployment/source identity, content handling and checks.

## News-source path proved — 6 November 2026

Added a permitted official GOV.UK India-news feed. Live collection saved five dated
sources; the selected 12 October JETCO release supplied 4,843 characters of verified
original text. PIB/RBI remain blocked and skipped. The source-backed explainer
`explainer-2026-w45` is persisted at `awaiting_review`, with no blocking issues or
exports. Exact-quote failures required a reviewer-curated brief, validated by the
unchanged guard. Fixed publication-date preservation during page enrichment.
Regression result: **40 passed** on Python 3.12.10. See `NEWS_SOURCE_VALIDATION.md`
for permission evidence, source and draft hashes, review details and limitations.

## Real guide accepted — 6 November 2026

Both OpenAI and Claude live lessons succeeded after the owner corrected the Claude
key. A real guide was drafted, revised by Claude, reviewed against its evidence and
approved for export. All four exports and the exact approval hash were verified.
Live use exposed and fixed literal-JSON prompt formatting and long citation-ID checks.
Regression result: **39 passed** on Python 3.12.10.
See `LIVE_GUIDE_REVIEW.md` for the article, review evidence, execution details and limits.
No website publication occurred. Earlier sections describe historical verification states.

## OpenAI and Claude migration — 6 November 2026

Replaced the Sarvam adapter with OpenAI Responses (evidence/review) and Claude
Messages (drafts/revisions), using the existing HTTP dependency. Added per-provider
live lessons, key-presence reporting and checks before reserving a new live job.
The CLI, SQLite state, shared request guard and approval/export flow remain.
`API_SETUP.md` supersedes the original tutorial's Sarvam instructions.

Python 3.12.10: `python -m pytest -q --basetemp=.pytest_cache/openai-claude-final`
via the project `.venv` completed with **38 passed in 19.29 seconds**.
Mocked requests cover both API contracts, provider routing, retry accounting,
missing keys, incomplete/refused/malformed responses and sanitized HTTP errors.
The offline chain lesson also passed. `doctor` reports both provider keys missing.
No paid API call or real article validation has occurred in this migration run.
The earlier offline baseline and approved demo remain historical verification.

## Windows Python 3.12 baseline — 6 November 2026

**Complete.** Installed Python 3.12.10 for the Windows user account and created a
fresh project `.venv` with that interpreter. The former Python 3.11 environment is
preserved at `.pytest_cache/venv-python311-backup`; do not use it as the active environment.
Installed `requirements.txt`, verified every direct dependency matches its pin, and
ran `pip check`: **No broken requirements found.** The installed package snapshot is
saved locally in `logs/windows312-packages.txt`.

Executed successfully from the project directory:

```powershell
.\.venv\Scripts\python.exe -m cashbot doctor
.\.venv\Scripts\python.exe -m lessons.chain_basics
.\.venv\Scripts\python.exe -m lessons.graph_basics
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_cache/windows312-baseline
.\.venv\Scripts\python.exe -m pip check
```

- `doctor`: correct project path, Python **3.12.10**, no Sarvam key, app facts unverified.
- Chain lesson: offline response, two messages passed to the model fixture.
- Graph lesson: revised the fictional example and finished with `needs_revision: False`.
- Tests: **28 passed in 21.56 seconds**, without an UTF-8 command-line override.
- Workspace-local pytest temporary files avoid the previously observed sandbox rename restriction.

Offline demo job: `windows312-baseline-20261106`.

1. Ran `demo --job windows312-baseline-20261106`; it stopped at `awaiting_review` /
   `human_review`. Confirmed `approved` was empty.
2. After that process exited, ran `status` in a new process. The same draft, status
   and hash were recovered from SQLite; `approved` remained empty.
3. Codex reviewed the generated fixture draft and review report against the fictional
   editorial source. The calculation `18500 - 7000 - 1500 = 10000` is correct, citations
   identify `demo_source`, checks contain no issues, and the draft makes no live
   product claims. This is an offline fixture review, not owner verification of app facts.
4. Tried approval with an incorrect hash. It exited with code 1 and created no exports.
5. Approved the reviewed fixture with its exact checked hash. Status became `approved`.
6. Verified a further process recovered `approved`, and all four nonempty exports exist:
   `.md`, `.html`, `.wp.html`, and `.approval.json` in `approved/` under the job name.
   All article exports include `NOT FOR PUBLICATION` and sources; the WordPress fragment
   excludes the title. The approval record matches the checked hash, marks `demo: true`,
   and records `publicly_published: false`.

Checked SHA256: `71fe70a0ebada4a79d6081e38658ad886abd676cef9f82c12bc9d9af87411d56`.

The demo source is now reserved in this project. Inspect this job with `status` rather
than starting another demo against the same source. No live API call, feed collection,
website publication or scheduled trigger was part of this offline baseline.

## Recovery and revision fixes — 6 November 2026

Executed on Windows with the available Python 3.11.0 interpreter in a local `.venv`:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest -q --basetemp=.pytest_cache/workflow-regression
```

Result: **28 passed**. New cases cover recovery after reservation but before the
first checkpoint, preserved duplicate protection, upgrading an existing reservations
database, previous-draft context for human and automatic revisions, and scheduled
reruns for approved, awaiting-review, failed, blocked, rejected and uncheckpointed jobs.

The default sandbox temporary directory denied atomic file renames; a workspace-local
test directory allowed the suite to run without changing application file writes.
The main requirements now explicitly include `lxml_html_clean==0.4.6`, already present
in the tested Linux snapshot, because the Windows extraction imports required it.
Python 3.12, live provider calls and actual scheduled triggers were not tested in this run.
Pre-upgrade reservations without checkpoints lack starting inputs and cannot be
automatically reconstructed; their duplicate protection is preserved.

## Original starter verification

Date: 5 November 2026. Environment: Linux, Python 3.12.14.

## Executed successfully

- Installed the pinned direct dependencies in a dedicated Python environment.
- Ran `python -m cashbot doctor`.
- Ran `python -m lessons.chain_basics` with the offline model fixture.
- Ran `python -m lessons.graph_basics`, including its conditional revision route.
- Ran the CLI demo, observed a persisted `awaiting_review` interrupt, reopened the checkpoint with a separate command, and approved the exact checked hash.
- Ran `python -m pytest -q`: **18 passed**. Tests include checkpoint recovery, approval/edit binding, blocked citations, bounded revisions, duplicate job/source reservations, malformed model JSON, guarded extraction, mocked feed handling, the mocked Sarvam HTTP contract, the request guard and HTML sanitization.
- Verified the ZIP includes no `.env`, credentials, generated job databases, generated articles, Python cache files or virtual environment.

## Attempted but not established

- Real feed collection returned zero sources. PIB and RBI were safely skipped because access rules could not be verified or denied access in this environment. This is not a successful real-world feed/scraping test.

## Not executed

- Live Sarvam calls: no user key/credit was provided.
- Real model output quality and factual accuracy.
- Publisher permission/terms review for any full-page extraction.
- Windows installation, Command Prompt wrapper and Task Scheduler.
- E2E/Zoho deployment or live weekly scheduling.
- Uploading or publishing an article on the user's website.

The mocked HTTP test verifies the adapter's expected request and response handling, not delivery to Sarvam. The offline model fixture verifies workflow behavior, not AI article quality. Human approval remains required, and website publication is manual.

## Repository boundary

All starter files were authored in a separate project folder. The existing `sharat422/ai-cashbook-ind` repository was inspected read-only earlier in the conversation; no file, branch, commit or pull request was created or changed there for this task.
