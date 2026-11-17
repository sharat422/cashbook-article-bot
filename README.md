# Cashbook Article Bot — separate learning project

**Workflow and operating guide:** [PDF](output/pdf/Bolcash_Article_Bot_Workflow.pdf)
or [browser edition](output/Bolcash_Article_Bot_Workflow.html). Includes the workflow
diagram, step-by-step commands, review/approval, scheduling, recovery and current UI status.

**Current live setup: OpenAI + Claude paid APIs.** Follow [API_SETUP.md](API_SETUP.md).
OpenAI prepares evidence and reviews articles; Claude writes drafts and revisions.
The Sarvam account/API instructions in the original tutorial are historical.

**Weekly Windows tasks are enabled:** Tuesday guide and Friday explainer, both at
9:00 AM Eastern. See [SCHEDULING.md](SCHEDULING.md) for logs, recovery and the
12-topic backlog. Every guide now has its own file under `notes/`.

**Do not add these files to `ai-cashbook-ind`.** This is a separate project folder for your marketing article workflow.

Start with `START_HERE.html` in a browser, or `START_HERE.md` in VS Code. The guide contains setup, plain-English explanations, exact commands, learning exercises, source configuration, review, publishing and scheduling.

Quick start on Windows PowerShell, from this folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m cashbot doctor
.\.venv\Scripts\python.exe -m lessons.chain_basics
.\.venv\Scripts\python.exe -m lessons.graph_basics
.\.venv\Scripts\python.exe -m cashbot demo --job demo-001
```

The demo is offline and uses fixture model responses. Live OpenAI and Claude calls require your keys and credit. Full-page extraction is opt-in per source. Publishing to your website remains manual in this version.

See `VERIFICATION.md` for what was and was not executed. No files in your mobile-app repository were changed or pushed.

Recovery: new job reservations save their starting inputs atomically. If execution stops
before the first checkpoint, run `python -m cashbot retry --job YOUR_JOB_ID` using
this project's Python environment. Existing job/source duplicate protection stays in place.
Older reservations created before this recovery data was stored retain their duplicate
protection but cannot be reconstructed by `retry` without a checkpoint.

Scheduled reruns leave existing jobs untouched and print their saved status and next
command. Failed or interrupted jobs point to `retry`; blocked drafts point to
`check-edits`; drafts awaiting review still require your decision. AI revision requests
include the previous checked draft along with your feedback.
