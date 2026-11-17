# Weekly schedule and backlog

Enabled and tested on **6 November 2026** using Windows Task Scheduler.

| Windows task | Trigger in Eastern time | Next scheduled run at verification |
|---|---|---|
| Cashbook Weekly Guide | Tuesday, 09:00 | 10 November 2026, 09:00 EST |
| Cashbook Weekly Explainer | Friday, 09:00 | 13 November 2026, 09:00 EST |

Windows timezone is `Eastern Standard Time` (America/New_York, with automatic
daylight-saving adjustments). Trigger times follow that Windows timezone. The bot
still uses `Asia/Kolkata` and ISO weeks to name jobs such as `guide-2026-w46`.
The India setting names jobs; it does not set the Windows trigger clock.

## Execution and limits

- Both tasks are enabled under the current Windows user's interactive token,
  with limited privileges. No account password is stored by this setup.
- **Stay signed in.** A locked session is fine; a signed-out session cannot run
  these tasks. The computer needs network access and usable provider credit.
- Missed starts are configured to catch up when available. Wake timers are requested,
  but actual waking depends on Windows power settings and hardware.
- Battery operation is allowed. Another instance of the same task is ignored while
  one is running. Each run has a 45-minute execution limit.
- Tasks invoke the absolute project `run_slot.cmd` and `.venv` Python paths, with
  UTF-8 output and the correct working directory. Keys are loaded locally from `.env`.
- Tasks prepare drafts only. They never approve, export or publish an article.
- A catch-up run prepares the current weekly slot, not every missed historical week.
- A news slot may stop without an article when evidence, relevance, date or access
  checks fail. Do not weaken checks or invent a story to fill the slot.

## Actual task tests

Both registered Windows tasks were started manually, rather than just executing
their Python commands. Final test: **6 November 2026, 21:27:54 EST**.

- Both returned to `Ready`, enabled, with `LastTaskResult: 0`.
- Guide found the approved `guide-2026-w45` and skipped it.
- Explainer found `explainer-2026-w45` awaiting review and skipped it.
- Both per-slot logs contain a timestamped START, saved status/recovery command,
  and END with `exit=0`. No duplicate articles or paid model calls were needed.
- This tests real scheduler invocation, working directory, environment loading,
  duplicate protection, logging and exit propagation on the successful path.
  Fresh article generation was established in the earlier live validations, not
  repeated by these scheduler smoke tests.
- The first simultaneous test exposed shared-log contention. Logs are now separated
  by slot. A CMD redirection issue on the numeric exit-code line was also corrected.
- Task results are saved locally in `logs/windows-task-results.json`.

Inspect from PowerShell in the project folder:

```powershell
Get-ScheduledTask -TaskName 'Cashbook Weekly Guide','Cashbook Weekly Explainer'
Get-ScheduledTaskInfo -TaskName 'Cashbook Weekly Guide'
Get-ScheduledTaskInfo -TaskName 'Cashbook Weekly Explainer'
Get-Content .\logs\guide.log -Tail 40
Get-Content .\logs\explainer.log -Tail 40
```

`logs/scheduler.log` is historical output from the older shared-log wrapper. Normal
scheduled output now goes to **guide.log** and **explainer.log**. An exit code of 0
means the command finished; it may have skipped an existing slot. Read its status.
Exit 1 indicates execution/check failure; invalid wrapper slots return 2. Windows
task startup errors can have other codes and may leave no START record.

## Recovery

1. Read the relevant log and note the job ID. If no START appears, check Task
   Scheduler history, the action path, signed-in account and folder access.
2. Inspect the saved job before rerunning anything:

   ```powershell
   .\.venv\Scripts\python.exe -m cashbot status --job JOB_ID_FROM_LOG
   ```

3. For a failed/interrupted job, resolve the key, credit, network, provider or source
   problem, then resume the **same** job:

   ```powershell
   .\.venv\Scripts\python.exe -m cashbot retry --job JOB_ID_FROM_LOG
   ```

   This also recovers new reservations that lack a first checkpoint. Older reservations
   from before starting inputs were saved cannot be reconstructed automatically.
   Quote-validation failures may need editorial intervention: inspect the original
   source, keep the validator strict, and request a verified brief if retries still fail.

4. For `awaiting_review`, read the draft and source report, then approve, revise or
   reject through the existing CLI. A scheduled rerun intentionally leaves it alone.
5. For `blocked`, edit the draft and recheck it:

   ```powershell
   .\.venv\Scripts\python.exe -m cashbot check-edits --job JOB_ID_FROM_LOG
   ```

   Re-review and use the new hash if later approving. Approved/rejected work is not
   silently overwritten. Do not delete databases or rename source IDs to force a run.
6. If no job was created (for example, empty guide backlog or no relevant news), fix
   the inputs and start that Windows task again. This will still target the current week.

Tasks do not automatically retry a saved failure or send notifications. Inspect logs
after weekly runs and clear outstanding reviews. Back up `data/`, `drafts/` and
`approved/` together while the bot is stopped; keep private backups and `.env` secure.

## Maintain the guide backlog

There are **12 topics and 12 distinct supporting note files**, with **11 unused** at
verification. The existing four IDs were preserved, so duplicate history still applies.
The offline demo retains `editorial_notes.md`; scheduled guides no longer share it.

| Topic ID | Supporting notes |
|---|---|
| guide_partial (used) | notes/partial-payments.md |
| guide_returns | notes/goods-returns.md |
| guide_closing | notes/daily-close.md |
| guide_reminder | notes/payment-reminders.md |
| guide_receipt_review | notes/receipt-review.md |
| guide_expense_categories | notes/expense-descriptions.md |
| guide_recurring | notes/recurring-expenses.md |
| guide_voice_expense | notes/voice-expense-review.md |
| guide_voice_queries | notes/voice-query-checks.md |
| guide_customer_identity | notes/customer-identity.md |
| guide_payment_evidence | notes/payment-confirmation.md |
| guide_report_review | notes/report-review.md |

Each contains a distinct reader problem, explicitly fictional figures, checked
arithmetic, a practical checklist or review method, and limits on product claims.
These are Codex-reviewed editorial exercises, not new owner-verified app features
or legal/tax authority. Product claims remain confined to `app_facts.json`.

To add a topic, create a new Markdown notes file inside the project and add a unique
`id`, `topic` and `notes_file` to `guide_topics.json`. Use a new question and supporting
material; do not relabel a used topic. The first unused ID is selected in list order.
Do not delete a note file after its topic is reserved; saved jobs retain their source
snapshot, and the backlog remains the audit trail. No external notes paths are allowed.

## Change, reinstall or disable tasks

Edit the `windows` section in `schedule.json`, then run:

```powershell
& .\scripts\install_windows_tasks.ps1
```

Use the same Windows account. The installer verifies the configured Windows timezone,
updates these two task definitions, and refuses a conflicting task action. It does
not change the system timezone or store a password. If script execution policy blocks
it, use a process-only invocation; do not change machine-wide policy:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_windows_tasks.ps1
```

After moving the project, rerun the installer only after reviewing/removing the old
task actions, which intentionally fail the conflicting-path check. Avoid two active
project copies with independent databases. To disable scheduling without deleting history:

```powershell
Disable-ScheduledTask -TaskName 'Cashbook Weekly Guide'
Disable-ScheduledTask -TaskName 'Cashbook Weekly Explainer'
```

## Regression verification

Python 3.12.10: **43 passed in 14.84 seconds**. New tests cover distinct notes for every
topic, selecting the next unused topic's own notes, and rejecting paths outside the
project. All illustrative arithmetic was checked separately. Future weekly execution,
wake behaviour and signed-out operation were not simulated; signed-out runs are not
supported by this password-free setup.
