# Build your Cashbook Article Bot

> Updated live provider setup: use `API_SETUP.md` for OpenAI and Claude paid APIs.
> The Sarvam setup, adapter names and provider examples below describe the original
> starter and have been superseded. Offline workflow, review and export commands remain applicable.
> Weekly tasks, per-slot logs and topic notes are now documented in `SCHEDULING.md`;
> use that runbook instead of the original scheduling/backlog instructions below.

## A beginner's guide to Python, LangChain, LangGraph and Sarvam AI

Prepared for your AI Smart Cashbook marketing project · 5 November 2026

**Start with the downloadable starter project. You do not have to type every Python file yourself.** This guide explains how to run it, how the important code works, and how to change it safely. Windows PowerShell is the main path because your earlier development setup used Windows. Mac/Linux alternatives are included.

## 1. What you will build

Your bot will prepare two article slots per week for small agencies and distributors in India:

- **Guide slot:** an original practical guide using your reviewed editorial notes and approved app facts.
- **Explainer slot:** an article about a relevant announcement discovered through approved RSS feeds.

It will collect sources, extract evidence, write a draft, check the draft, save progress, wait for your review, and export an approved article. An unsuitable source or unresolved problem stops the article. A weekly slot is a target, not a reason to invent news or publish weak content.

**This version exports files. Uploading the approved article to your website is manual.** The scheduled job never publishes to the public internet. Step 19 explains the complete manual WordPress path. If your marketing site is Next.js or another system, use the Markdown export instead and arrange the site's integration separately. Your marketing website technology has not yet been confirmed.

You will keep this project separate from ai-cashbook-ind. It does not connect to customer transactions or change your mobile app. It needs no GPU.

**Your first milestone:** run the free demo, see `Status: awaiting_review`, review a file, and approve its export. Do this before buying hosting or connecting an AI account.

## 2. Understand the names first

| Term | Plain-English meaning | Example in this project |
|---|---|---|
| Python | The programming language | Runs the bot's instructions |
| Terminal / PowerShell | A window where you type commands | `python -m cashbot doctor` |
| Package | Reusable code installed from a package registry | `langgraph` |
| Virtual environment | A private set of Python packages for this project | `.venv` folder |
| API | A way for one program to talk to another service | Sending a prompt to Sarvam |
| API key | A secret credential for that service | Stored only in `.env` |
| Model | The AI that generates text | A Sarvam model your account can access |
| LangChain | Reusable components for prompts, model calls, tools and outputs | The prompt → model → text chain |
| LangGraph | The workflow controller | Decides when to revise, stop or wait for approval |
| State | The current job's shared information | Topic, sources, draft and check results |
| Node | One step in the workflow | Write the draft |
| Edge | The connection to the next step | Draft → Check |
| Conditional edge | A route selected from a result | Problems found → Revise |
| Checkpoint | A saved position and job state | Resume after closing PowerShell |
| Thread ID | The name of one saved workflow | `demo-001` |
| RSS feed | A machine-readable list of website updates | PIB press-release feed |
| Markdown | Plain text with simple formatting | `# Title`, `## Subheading`, `- Bullet` |

The tutorial installs **langchain-core**, the official modular core of LangChain. You do not need the larger `langchain` package or a paid LangSmith deployment to run this project. LangSmith tracing is disabled in the starter.

## 3. Install Python and an editor

1. Open [Python's Windows downloads](https://www.python.org/downloads/windows/).
2. Install a **Python 3.12** release appropriate to your computer. This tutorial was tested with Python 3.12 on Linux. Python 3.12.10 has a traditional Windows installer at [its release page](https://www.python.org/downloads/release/python-31210/); later security releases may not provide that installer.
3. If the installer offers **Add python.exe to PATH**, select it. Finish the installation.
4. Install [Visual Studio Code](https://code.visualstudio.com/). You will use it to open and edit the configuration files.
5. Close and reopen PowerShell so it can see Python.
6. Type this command:

```powershell
py -3.12 --version
```

**Checkpoint:** the output starts with `Python 3.12`. If `py` is unavailable, try `python --version`; use `python -m venv .venv` in step 5 only if it reports the intended Python version.

You do not need Node.js, Android Studio, LangSmith, a cloud account or your app database for this tutorial.

## 4. Extract and open the starter project

1. Download `Cashbook_Article_Bot_Starter.zip` from the ChatGPT response.
2. In File Explorer, right-click the ZIP and choose **Extract All**.
3. Place the resulting `cashbook-article-bot` folder in your Windows user folder. For example: `C:\Users\YourWindowsName\cashbook-article-bot`.
4. Open that folder. You should immediately see `requirements.txt`, `app_facts.json`, `START_HERE.md`, and a folder called `cashbot`. If you see another `cashbook-article-bot` folder inside, use the inner folder.
5. In VS Code choose **File → Open Folder**, then select that project folder.
6. Open PowerShell and enter:

```powershell
Set-Location "$env:USERPROFILE\cashbook-article-bot"
Get-ChildItem
```

**Checkpoint:** `requirements.txt` and `cashbot` appear in the list. If you extracted elsewhere, change the path to that actual folder before continuing.

## 5. Create the project's Python environment

Run these commands one at a time in PowerShell, from the project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m cashbot doctor
```

The installation may take a few minutes. `requirements.txt` pins the main dependencies used in the verified build. `requirements-tested-linux.txt` records all packages from the test environment; use the simpler `requirements.txt` for your first installation.

**Checkpoint:** `doctor` prints the project path and Python version. It is normal to see `Sarvam key configured: False` and `Owner verified app facts: False` at this point.

We call `.venv\Scripts\python.exe` directly. You do not need to activate the environment or change PowerShell's execution policy.

**Mac/Linux equivalent:**

```bash
cd ~/cashbook-article-bot
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m cashbot doctor
```

For the remaining examples, replace `.\.venv\Scripts\python.exe` with `.venv/bin/python` on Mac/Linux.

## 6. Run the free, offline demonstration

```powershell
.\.venv\Scripts\python.exe -m cashbot demo --job demo-001
```

**Expected result:**

```text
Job: demo-001
Status: awaiting_review
Next: human_review
Draft: ...drafts/demo-001.md
Review: ...drafts/demo-001.review.json
SHA256: a long sequence of letters and numbers
```

The demo uses a fictional retailer ledger and fixed model responses. It runs the real LangGraph workflow and SQLite persistence, but does **not** call Sarvam or fetch news. It demonstrates behavior, not writing quality.

Open `drafts/demo-001.md` in VS Code. Use **Ctrl+Shift+V** to preview Markdown. Then open `drafts/demo-001.review.json`. This review file contains the supporting source material, the evidence brief and the checks.

**Checkpoint:** the `approved` folder is empty. A generated draft is not an approved article.

If you run the same demo command twice, the bot stops because the job/source is reserved. Use `status` to inspect it rather than creating duplicates. To repeat the lesson later with a fresh job, use `demo --job demo-002`; that demo intentionally shares its source, so the tutorial's source-duplicate guard will still prevent a second draft in the same project. For repeat practice, use a fresh copy of the starter folder. Do not delete your real job history to repeat a demo.

## 7. See how LangGraph remembers your work

Close PowerShell. Open a new PowerShell window and run:

```powershell
Set-Location "$env:USERPROFILE\cashbook-article-bot"
.\.venv\Scripts\python.exe -m cashbot status --job demo-001
```

You should still see `awaiting_review`. The checkpoint is saved in `data/checkpoints.sqlite`, not just in the old process's memory.

Think of it as a saved game: `demo-001` identifies the saved game and the checkpoint records where it stopped. Every real article gets its own job ID.

## 8. Review and approve the demo export

Read the demo article and its source. Run `status` again and copy the complete value following `SHA256:`.

Replace `PASTE_HASH_FROM_STATUS` below with that actual value, without adding spaces inside the value:

```powershell
.\.venv\Scripts\python.exe -m cashbot approve --job demo-001 --reviewed --sha256 PASTE_HASH_FROM_STATUS
```

`--reviewed` means you personally checked the content. The hash identifies the exact draft you checked. It does not prove the draft's facts are correct.

**Checkpoint:** the status becomes `approved`. Open these files:

| File | What it contains |
|---|---|
| `approved/demo-001.md` | Approved Markdown plus source references |
| `approved/demo-001.html` | A readable, sanitized browser preview |
| `approved/demo-001.wp.html` | An HTML fragment for WordPress, without the article title |
| `approved/demo-001.approval.json` | The approval record and draft hash |

The demo export is visibly labelled **NOT FOR PUBLICATION**. Do not put it on your marketing site. Approval in this project means approval to export files; it does not publish to a website.

## 9. Learn LangChain with the first small exercise

Run:

```powershell
.\.venv\Scripts\python.exe -m lessons.chain_basics
```

Open `lessons/chain_basics.py`. The important line is:

```python
chain = prompt | model | StrOutputParser()
print(chain.invoke({"topic": "a partial customer payment"}))
```

Read it from left to right:

1. `prompt` inserts your topic into a reusable message template.
2. `model` receives those messages and produces a response.
3. `StrOutputParser()` turns the response into ordinary text.
4. `invoke()` starts the chain with your chosen input.

The `|` character joins components. It is Python's pipe operator as implemented by LangChain's Runnable interface here; it is not a shell command.

The exercise uses `RunnableLambda` to wrap a small Python function. By default that function returns a fixed answer. Later, `--live` changes the function to the Sarvam adapter while keeping the rest of the chain the same.

**Try this:** change the topic string, save the file, and run it again. The offline answer stays fixed because it is a fixture. In live mode the model receives your changed topic.

## 10. Learn LangGraph with the second small exercise

```powershell
.\.venv\Scripts\python.exe -m lessons.graph_basics
```

Open `lessons/graph_basics.py`. There are three nodes: `write`, `check`, and `revise`.

- The first draft does not label its example as fictional.
- The checker sets `needs_revision=True`.
- A conditional edge sends the draft to `revise`.
- The revised draft is checked again, then the graph finishes.

The output contains `Fictional example:` and `needs_revision: False`.

This code defines the shared notebook passed between the nodes:

```python
class State(TypedDict, total=False):
    topic: str
    draft: str
    needs_revision: bool
```

This code defines a route:

```python
builder.add_conditional_edges(
    "check",
    lambda state: "revise" if state["needs_revision"] else "done",
    {"revise": "revise", "done": END},
)
```

The small lesson's checker is a simple string rule, not AI. This is intentional: learn graph mechanics before connecting expensive or unpredictable operations.

## 11. Understand the complete article graph

Open `cashbot/workflow.py`. Read these functions in order:

| Function | What to look for |
|---|---|
| `make_brief` | Extracts claims with short supporting quotes; validates quotes against source text |
| `write_draft` | Uses evidence and approved product facts to request an original article |
| `check_draft` | Performs programmatic checks plus a model-assisted review in live mode |
| `route_checks` | Sends a bad draft back for revision; stops after three drafts total |
| `save_review` | Saves the reviewable draft and source report |
| `human_review` | Calls LangGraph's `interrupt()` and waits for your decision |
| `export_approved` | Verifies approval matches the checked text and exports local files |
| `build_graph` | Connects all the nodes and routes |

The `Brief` and `Review` classes use Pydantic to check the model's JSON shape. A valid JSON shape does not establish factual truth. Exact source quotations help identify invented evidence, but a human must still check interpretation and applicability.

The Sarvam integration is in `cashbot/llm.py`. We use a LangChain Runnable around a direct HTTP call to Sarvam's documented `/v2/chat/completions` endpoint. This avoids assuming that Sarvam implements every feature of a different provider's LangChain integration. We do not rely on native tool calling or native JSON-schema mode for the starter.

The scraper is also wrapped as a LangChain tool, `fetch_approved_page`, in `cashbot/research.py`. The program explicitly calls this tool through `.invoke()`. The model does not choose arbitrary websites or execute source-page instructions.

## 12. Create your Sarvam account and configure the key

Only do this after the offline exercises work.

1. Read the official [Sarvam developer quickstart](https://docs.sarvam.ai/api/getting-started/quickstart).
2. Follow its link to the current dashboard and create/sign in to your account.
3. Create an API key. Dashboard labels may change; use the current official quickstart rather than an old video.
4. Check model availability and credit/billing in your account. The starter proposes `sarvam-105b`; use it only if your account supports that model on the documented `/v2` API.
5. Back in the project folder, create a local configuration file:

```powershell
Copy-Item .env.example .env
notepad .env
```

Replace the placeholder after `SARVAM_API_KEY=` with your real key. Save the file and close Notepad.

```text
SARVAM_API_KEY=your_actual_key_goes_here
SARVAM_MODEL=sarvam-105b
MAX_API_CALLS_PER_DAY=30
LANGSMITH_TRACING=false
```

Do not put your key into a Python file, an article, a screenshot, GitHub or a chat message. `.gitignore` excludes `.env`, job databases and generated articles. It does not protect secrets if you force-add files or share the whole working folder.

Run:

```powershell
.\.venv\Scripts\python.exe -m cashbot doctor
.\.venv\Scripts\python.exe -m lessons.chain_basics --live
```

**Checkpoint:** `doctor` says the key is configured, then the live lesson prints a model response. The key-configured flag only checks presence; the live response is the actual connectivity check.

This live lesson can consume API credit. The starter limits request attempts per UTC day and output tokens per request. The request-count limit is **not a rupee spending cap**. Use any spending controls offered by your provider and review current [Sarvam pricing](https://docs.sarvam.ai/api/getting-started/pricing). A normal successful draft needs three model requests: evidence, draft and review. Revisions and transient-error retries use additional requests.

## 13. Approve the facts the bot can say about your app

Open `app_facts.json` in VS Code. Initially it contains `owner_verified: false`, no approved features and no marketing URL. That blocks live drafting until you review the file.

1. Check your current app build yourself.
2. List only the features you have tested and want to advertise in `approved_features`.
3. Correct the release status. Do not claim the app is publicly available if it is still in testing.
4. Add a real landing-page or pilot-registration URL to `marketing_url`, or leave it empty to omit the CTA.
5. Keep material limitations accurate.
6. Change `owner_verified` to `true` after the review.
7. Review `editorial_notes.md` too; it is the source material for practical guides. Its example is fictional and makes no claims about supported app features.

Example feature entry **only after you have verified it**:

```json
"approved_features": [
  "Customer ledger with customer credit and payment entries"
]
```

Do not copy this example as evidence that your released build works. The repository inspection found implementation code, not device-test results. In particular, do not advertise automatic UPI confirmation, automatic reconciliation or guaranteed faster collections without establishing those capabilities.

JSON needs double quotes and commas between items. It does not allow trailing commas or comments. If you see a JSON error, use VS Code's highlighted error location and correct the punctuation.

## 14. Generate your first real practical guide

This is the easiest first live article because it uses your reviewed original material rather than depending on an external feed.

```powershell
.\.venv\Scripts\python.exe -m cashbot scheduled --slot guide
```

The bot selects an unused topic from `guide_topics.json`, reads your original notes, generates the article and checks it. It creates a weekly job ID such as `guide-2026-w45`; the actual ID depends on the run date in `schedule.json`'s timezone.

**Checkpoint:** copy the actual job ID from the output. Open its `.md` and `.review.json` files in `drafts`. A successful check ends at `awaiting_review`. If issues remain after two automatic revisions, it ends at `blocked` and shows the problems.

This guide article is not scraped news. Its original teaching material is identified as local editorial material in the source report. The second weekly slot uses online discovery in the next steps.

## 15. Collect real online sources

Run:

```powershell
.\.venv\Scripts\python.exe -m cashbot collect
.\.venv\Scripts\python.exe -m cashbot sources
```

The first command checks the configured feeds and saves `data/inbox.json`. The second prints source IDs, titles and available publication dates. IDs look like `a12b34c56d78`; use the ID actually printed on your computer.

Default sources are PIB and RBI. The bot uses public feed summaries initially, not unrestricted full-page extraction. It keeps publication and retrieval dates separate. Unknown dates remain unknown. The automated news selector will not call an undated source current news.

**If you see `Saved sources: 0`:** read the warnings. The bot may be unable to retrieve robots rules, reach a feed, or find entries. It stops rather than bypassing access restrictions. Check the original website in your browser and current official feed documentation. Update `sources.json` only with an approved, working URL. You can continue learning and producing reviewed practical guides from your own material while resolving feed access.

The development environment could not verify live access to the default feeds. Both were safely skipped because their access rules could not be verified or denied access. Mocked collection tests passed; real feed availability must be checked from your machine.

## 16. Enable actual page extraction where permitted

Use this step only after you review a source site's terms and the intended use. Public visibility and an RSS feed do not automatically authorize full-page reuse.

In `sources.json`, each source has exact permitted hostnames and this setting:

```json
"full_text_allowed": false
```

For a source where you have established that your collection is permitted, change that setting to `true`. Keep a useful note in `permission_note` describing the basis and the date you checked it. The bot still checks robots rules, validates URLs, follows only approved-host redirects and respects a small extraction limit. It will not bypass logins, paywalls, CAPTCHA or anti-bot restrictions.

Run `collect` again. It attempts extraction for at most two entries per enabled source, waiting between page requests. If extraction fails, it keeps the feed summary and records a warning.

To extract one specific permitted HTML page, replace the URL and title below with a real approved source page:

```powershell
.\.venv\Scripts\python.exe -m cashbot add-url --url "https://YOUR_APPROVED_HOST/ACTUAL_ARTICLE" --title "Actual source title"
```

The hostname must exactly match one in the enabled source's `hosts` list. For example, `example.com` and `www.example.com` are different hostnames. Add a redirected hostname only after reviewing it. The tutorial does not include a PDF extractor, a JavaScript browser crawler or an unrestricted web-search API.

Extraction uses Trafilatura to separate the page's main text from navigation and other material. The model receives bounded extracts as evidence. Articles should contribute original explanation, examples and tools; they should not rewrite and republish someone else's reporting.

## 17. Draft an article from a selected online source

First run `sources` and copy an ID. Replace `ACTUAL_SOURCE_ID` below with it:

```powershell
.\.venv\Scripts\python.exe -m cashbot start --job first-online-article --source ACTUAL_SOURCE_ID --topic "Explain this announcement for small Indian distributors and identify the practical recordkeeping questions it raises"
```

Use a topic that actually fits the source you selected. A UPI announcement does not establish GST rules or prove that distributors save time with your app.

The bot stops if the evidence is too thin, a quote cannot be found in the source, the model returns invalid JSON, or the provider fails. It may still produce a weak draft from a marginal source; the review step is essential. It does not perform investigative reporting or guarantee claim correctness.

For automatic selection of the news slot:

```powershell
.\.venv\Scripts\python.exe -m cashbot scheduled --slot explainer
```

This fetches sources, scores dated stories against the keywords in `schedule.json`, excludes already reserved source IDs, and selects a candidate. This relevance score is a simple starting heuristic, not a guarantee of editorial quality. You can improve it with a model-based classifier after learning the basic version. If no worthwhile unused candidate exists, it stops; choose a reviewed guide instead.

## 18. Review, revise and approve a real draft

Use your actual job ID instead of `YOUR_JOB_ID` in every command below.

Read both the draft and review file. Check:

- Does the article answer a real question an agency or distributor owner has?
- Does every material external claim match its cited original source?
- Are the announcement date, event date and effective date correctly distinguished?
- Are the example numbers correct and clearly fictional?
- Are the app features, pricing and availability supported by your verified facts?
- Does the article add original explanation, a checklist or a tested walkthrough?
- Are quotations and assets used appropriately, with sources attributed?
- Is the CTA relevant and linked to the right page?

For legal, tax or regulatory interpretations, obtain an appropriately qualified review before publication.

**Ask for an AI revision while the job is awaiting review:**

```powershell
.\.venv\Scripts\python.exe -m cashbot revise --job YOUR_JOB_ID --feedback "Make the opening concrete, keep the example fictional and remove the unsupported claim about faster collections."
```

This performs another drafting/checking cycle and can use API credit. It returns to review or stops with blockers.

**Or edit the Markdown yourself** in VS Code, save it, and run:

```powershell
.\.venv\Scripts\python.exe -m cashbot check-edits --job YOUR_JOB_ID
```

This also works for a blocked draft. It checks the edited text again without silently approving it. Review the latest result, copy the new SHA256 shown by `status`, then run:

```powershell
.\.venv\Scripts\python.exe -m cashbot status --job YOUR_JOB_ID
.\.venv\Scripts\python.exe -m cashbot approve --job YOUR_JOB_ID --reviewed --sha256 PASTE_NEW_HASH_FROM_STATUS
```

An unchecked edit or old hash blocks approval. Do not calculate the hash with Windows `Get-FileHash`; Windows line endings can differ from the normalized text the bot checks. Copy the value printed by the bot.

**Reject an awaiting-review article:**

```powershell
.\.venv\Scripts\python.exe -m cashbot reject --job YOUR_JOB_ID
```

**Retry a job that failed during execution**, after fixing its key/network/provider issue:

```powershell
.\.venv\Scripts\python.exe -m cashbot retry --job YOUR_JOB_ID
```

Use `retry` for interrupted failures. Use `check-edits` for an article that finished with blockers. After an article is approved or rejected, start a new editorial job to change it; this starter does not maintain website revisions.

## 19. Publish an approved article manually

If you already have WordPress:

1. Open the real article's `approved/YOUR_JOB_ID.html` in a browser and read the preview.
2. Sign in to your own WordPress dashboard.
3. Choose **Posts → Add New** or the equivalent label in your version.
4. Enter the article title in the title field.
5. Add a **Custom HTML** block to the article body.
6. In VS Code open `approved/YOUR_JOB_ID.wp.html`. Copy the entire file into that Custom HTML block. It excludes the first article title to avoid repeating it.
7. Preview the post. Check headings, source references, mobile readability and the app link. Replace raw citation IDs with readable footnotes or linked source references as needed.
8. Add a real product screenshot only if it matches the article and contains no customer data. Add useful image alt text.
9. Set the author/reviewer accurately, the URL slug and the relevant category. Do not claim someone reviewed it unless they did.
10. Save as a draft first. Recheck the page, then choose Publish when ready.
11. Open the public URL in a separate browser window and test its links.
12. Record the article URL and any resulting pilot registrations in your marketing tracker.

Your site may use a different editor or restrict custom HTML. If so, paste the Markdown/text into its supported editor and apply the headings and links there. No WordPress account or hosting purchase is required to complete the local learning stages.

For Next.js or another Git-backed site, use the `.md` export as input to that site's actual article system. An MDX site may require frontmatter or a different folder structure. That adapter depends on the website repository and is outside this starter. Do not assume that copying a file into the mobile repository creates a public blog.

## 20. Schedule the two weekly slots on Windows

First verify both live commands manually. A scheduled command behaves exactly like the command you ran yourself.

Use **Windows Task Scheduler** to create two tasks. The shipped `run_slot.cmd` handles the project working directory and writes logs.

### Task A: weekly practical guide

1. Open Start and search for **Task Scheduler**.
2. Choose **Create Basic Task**.
3. Name it `Cashbook Weekly Guide`.
4. Choose a **Weekly** trigger, select **Tuesday**, and choose a time when your computer will be awake and online.
5. Choose **Start a program**.
6. In Program/script, enter the full path to Windows Command Prompt, normally `C:\Windows\System32\cmd.exe`.
7. In Add arguments, enter the following, replacing `YourWindowsName` with your actual Windows user-folder name:

```text
/c ""C:\Users\YourWindowsName\cashbook-article-bot\run_slot.cmd" guide"
```

8. In Start in, enter your actual project folder, without the executable filename.
9. Finish. Select the task and choose **Run** to test it.
10. Open `logs/scheduler.log`. Confirm the job was created or that the existing weekly slot was correctly skipped.

### Task B: weekly explainer

Repeat the same steps with the name `Cashbook Weekly Explainer`, a **Friday** trigger, and this argument:

```text
/c ""C:\Users\YourWindowsName\cashbook-article-bot\run_slot.cmd" explainer"
```

Task Scheduler uses your Windows computer's timezone and settings. `schedule.json` uses `Asia/Kolkata` to name the weekly article slots; it does not change the Windows task's trigger timezone. As you are in the USA, choose trigger times in the timezone shown by Windows. Publication remains a separate manual action.

In each task's Properties → Settings, consider **Run task as soon as possible after a scheduled start is missed**. Review Conditions if a laptop is skipping runs on battery power. During initial testing, run while logged in. If you later configure unattended execution, use the same Windows account and verify its folder permissions and credentials.

The computer must be available to execute the job. Check Windows' reported task result and `scheduler.log`; completion without a draft may mean the source check stopped it. A sleeping/offline laptop is a reason to move to an always-on host after the local workflow is reliable.

## 21. Keep the topic backlog and sources useful

The starter includes four distinct guide topics. A used topic/source ID is reserved to prevent accidental repetition. After those four guide topics are consumed, add new reviewed topics with new IDs to `guide_topics.json`.

Do not merely rename an old ID to generate the same article again. Add new editorial material and a new reader question. For example, add a specific tested app walkthrough after verifying that workflow yourself.

Keep `editorial_notes.md` focused on material you can support. For a larger backlog, the next useful improvement is a separate notes file per guide topic. Add Hindi or Telugu only after the English version works, and have a fluent reviewer check business and financial terminology. Translation produces additional pages and should be planned explicitly rather than silently multiplying the two-article target.

Review `app_facts.json` after every app release. Review source access rules and feed health regularly. Updating your article facts file does not update an already approved article automatically.

## 22. Optional: move to an Indian cloud host

Do this after several successful local drafts. [E2E Networks](https://www.e2enetworks.com/compute-products) is an Indian provider with CPU virtual machines. Choose a small CPU VM appropriate to current package requirements and the provider's available plans; no GPU is required for hosted API calls. Confirm current costs before buying.

The following assumes you have created an **Ubuntu 24.04** VM and can log in with the SSH details provided by your host. Server account names and console screens vary; use the provider's actual instructions. You do not need to expose a public web port for this command-line bot.

1. Copy the starter ZIP to the server using the provider's upload facility or `scp` with your actual SSH user and host.
2. Connect using the SSH command provided for your VM.
3. Install Python environment support and unzip the project in your user's home directory:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip unzip tzdata
unzip Cashbook_Article_Bot_Starter.zip
cd ~/cashbook-article-bot
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
nano .env
```

4. Enter your key privately in `.env`, review `app_facts.json` and the editorial notes, and repeat the live tests. Do not put the key in a public shell command or upload it to GitHub.
5. If migrating existing work, securely copy `data`, `drafts` and `approved` after stopping all local runs. Those folders are not in the starter ZIP. Keep a private backup. Do not run the Windows and cloud schedules simultaneously against separate copies of the same editorial backlog.
6. To use India time consistently on this dedicated VM, set the server timezone and inspect it:

```bash
sudo timedatectl set-timezone Asia/Kolkata
date
```

7. Run `pwd` inside your project and copy its actual absolute path. Then run `crontab -e` and add these two lines, replacing `/home/YOUR_USER/cashbook-article-bot` with that actual path:

```cron
7 18 * * 2 cd /home/YOUR_USER/cashbook-article-bot && .venv/bin/python -m cashbot scheduled --slot guide >> logs/scheduler.log 2>&1
7 18 * * 5 cd /home/YOUR_USER/cashbook-article-bot && .venv/bin/python -m cashbot scheduled --slot explainer >> logs/scheduler.log 2>&1
```

These triggers target Tuesday and Friday at 18:07 in the VM's timezone. Confirm that your cron service uses that timezone after changing it. Test each command manually, inspect `crontab -l`, and inspect the log after the next trigger. Windows scheduling and this cloud deployment were documented but not executed in the development environment.

SQLite is suitable for this small, single-machine tutorial. Keep the database on persistent disk. If you later run several workers, migrate checkpointing and job reservations to a shared durable database and add a proper work queue and concurrency controls.

Zoho Catalyst Job Scheduling is another Indian-provider option for managed triggers. It needs its own deployment adapter and durable state configuration; it is not a drop-in replacement for a local SQLite file. Do not follow tutorials for the older CloudScale Cron service. Zoho Mail notifications and Sarvam translation are future additions, not included integrations in this starter.

## 23. Troubleshooting

| What you see | What it means | What to do |
|---|---|---|
| `py` not recognized | Python launcher is missing | Reopen PowerShell; check the installer or use a verified Python executable |
| `No module named cashbot` | Wrong working folder or executable | Change to the folder containing `cashbot`; use this project's `.venv` Python |
| Package installation fails | Version/platform/network issue | Confirm Python 3.12 and copy the exact error for diagnosis; do not randomly upgrade all packages |
| `owner_verified` error | Live marketing facts have not been reviewed | Complete step 13 |
| Sarvam HTTP 401/403 | Key, account or permission problem | Check the key and access in the current dashboard without sharing the key |
| Sarvam HTTP 400/404 | Model or request contract may differ | Verify the model ID and `/v2` API access against current docs |
| Sarvam HTTP 429 | Rate or credit limit | Check account limits; wait rather than repeatedly restarting |
| Model output truncated | Token allowance was exhausted | Shorten the requested article or carefully review the token setting in `llm.py` |
| Daily request limit reached | Local request-attempt guard stopped calls | Review usage and wait for the next UTC day, or intentionally adjust the guard |
| `Saved sources: 0` | No permitted, accessible feed material was collected | Read warnings; verify feed URLs and access; use original reviewed guide material meanwhile |
| No useful page text | Page might need JavaScript, be blocked or be a PDF | Use another permitted HTML source or manual research; do not bypass protections |
| Evidence quote not found | Model's proposed quote is not in the source | Inspect source/brief quality; retry only after resolving the cause |
| Invalid model JSON | Response did not meet the schema | Inspect the model's suitability/prompt; the job stopped rather than trusting malformed output |
| Job/source already reserved | Duplicate protection worked | Use `status`, `retry` or the existing job rather than new IDs for the same story |
| `awaiting_review` | Normal approval pause | Read the draft and sources, then approve, revise or reject |
| `blocked` | Checks still found problems | Edit the draft and use `check-edits` |
| Draft/hash changed | Approval would apply to unchecked text | Run `check-edits`, review again and copy the new status hash |
| Scheduler creates no article | Task failed, slot exists, backlog empty or evidence unsuitable | Check `logs/scheduler.log` and the task result |

If asking Codex for help, share the command, the non-secret error and relevant source file. Never include `.env`, provider keys or customer bookkeeping data.

## 24. Check the project yourself

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Automated tests cover real graph execution with fixture model responses, pause/resume across SQLite connections, approval tied to checked content, blocked edits, bounded revisions, duplicate reservations, URL restrictions, opt-in extraction, robots denial, feed deduplication, malformed model output and a mocked Sarvam request contract.

The tests do not establish real Sarvam quality, actual publisher permission, live feed availability, Windows Task Scheduler behavior, cloud deployment success or public-site publishing. Complete those checkpoints on your own account/machine. The development verification record is in `VERIFICATION.md`.

## 25. Official learning links, in a useful order

| Order | Resource | What to focus on |
|---|---|---|
| 1 | [Python tutorial](https://docs.python.org/3/tutorial/) | Variables, lists, dictionaries, functions and imports |
| 2 | [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview) | Models, tools and the component approach |
| 3 | [LangGraph quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) | State, nodes and edges |
| 4 | [LangChain Academy: Introduction to LangGraph](https://academy.langchain.com/courses/intro-to-langgraph) | Start with setup, simple graph, router and state; enrollment may be required |
| 5 | [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | Why saved state matters |
| 6 | [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) | Pause and resume for human review |
| 7 | [Sarvam developer quickstart](https://docs.sarvam.ai/api/getting-started/quickstart) | Account, key and first real call |
| 8 | [Sarvam Token Factory](https://docs.sarvam.ai/api/token-factory) | The current `/v2` model API |
| 9 | [Trafilatura Python usage](https://trafilatura.readthedocs.io/en/latest/usage-python.html) | Main-text extraction and metadata |
| 10 | [Google guidance on generative AI content](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content) | Accuracy, originality and user value |
| 11 | [PIB RSS directory](https://www.pib.gov.in/ViewRss.aspx?lang=1&reg=1) | Official feed discovery |
| 12 | [Microsoft scheduled-task documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create) | Scheduling terminology and options |

Links and API design were checked against official documentation while preparing this guide. Provider interfaces and available models can change. Code is pinned to the packages actually installed for this starter, with the verification limits stated above.

## 26. Your completion checklist

- [ ] Python 3.12 works and dependencies install.
- [ ] `doctor` prints the intended project folder.
- [ ] Both offline LangChain/LangGraph lessons run.
- [ ] The demo pauses, survives a restart and exports only after approval.
- [ ] The live Sarvam lesson succeeds using your own key.
- [ ] Your app facts and original editorial notes are reviewed.
- [ ] A real guide is drafted and checked.
- [ ] A permitted online source is collected or extracted, with its limitations understood.
- [ ] A real source-based article is drafted and reviewed.
- [ ] An edited draft is rechecked before approval.
- [ ] Your first real article is previewed and published through your website.
- [ ] Both weekly triggers are tested, with logs inspected.
- [ ] Your backlog, source health, API usage and article results are reviewed regularly.

**Begin with steps 3–8. You will have a working local workflow before connecting a paid service.**
