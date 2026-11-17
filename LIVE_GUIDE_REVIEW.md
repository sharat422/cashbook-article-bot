# Live guide validation — 6 November 2026

Result: **passed and approved for local export**. Nothing was published to a website.

Article: **Recording a Partial Payment and a Goods Return Without Muddling the Balance**.
Job: `guide-2026-w45`. This is a real API-generated educational guide (`demo: false`)
using an explicitly fictional worked example, not a news article or customer case study.

## Live execution

- OpenAI live chain lesson succeeded with `gpt-4.1-mini`.
- The initial Claude lesson returned HTTP 401. After the owner replaced the key
  locally, the Claude lesson succeeded with `claude-sonnet-5-5`.
- OpenAI produced the evidence brief, initial draft and model-assisted review while
  the Claude key was being corrected. This was a process-only draft-provider override.
- Claude revised the existing draft with specific reviewer feedback; OpenAI reviewed
  the revision. Saved provider settings remain OpenAI evidence/review and Claude drafts.
- Codex reviewed the source, draft, revision and final edited text. A final manual
  edit clarified that a disputed ledger balance is not a customer-agreed amount;
  `check-edits` then rechecked the exact final text before approval.

## Content checks

- Every brief quote matches the reviewed editorial source `guide_partial`.
- The source is original fictional teaching material, not external legal authority.
- Arithmetic: 18,500 - 7,000 = 11,500; 11,500 - 1,500 = 10,000.
- A disputed Rs 1,500 return leaves the illustrative ledger balance at Rs 11,500
  pending acceptance; the guide does not label it an agreed or undisputed total.
- App claims are limited to approved income/expense records, customers and receipt
  OCR with review. No goods-return support or automatic payment confirmation is claimed.
- Bolcash is described as pre-launch, with an owner-planned date of 20 November 2026,
  not guaranteed availability. There is no marketing URL or registration/download CTA.
- Unsupported benefit claims, a fabricated product-facts citation and unsupported
  LaTeX formatting from the initial draft were removed during revision.
- Final article: 944 whitespace-separated words; final automated issues: none.

## Approval and exports

The guide had no exports before approval. The final SHA256 is:

`c82052e3b07be13fe3fd04dee0fe53c26b8d3969475660cd1485b4a2dde81402`

Approved with that exact checked hash after Codex's review. Verified nonempty exports:

- `approved/guide-2026-w45.md`
- `approved/guide-2026-w45.html`
- `approved/guide-2026-w45.wp.html`
- `approved/guide-2026-w45.approval.json`

Markdown preserves the checked draft and adds sources. Both HTML exports contain
two tables and source references. The preview includes one title; the WordPress
fragment excludes it. The approval record has `demo: false`, the checked hash and
`publicly_published: false`. Export structure was checked programmatically; this
was not a mobile-browser visual inspection or a plagiarism-database search.

## Fixes discovered through live use

1. LangChain interpreted literal JSON braces in system instructions as template
   fields. System instructions now use a literal `SystemMessage`. The saved job
   resumed through `retry` without losing its reservation.
2. The citation checker ignored unknown IDs longer than 20 characters, including
   `[approved_product_facts]`. It now checks those IDs too.

Regression checks: **39 passed in 11.82 seconds**, Python 3.12.10, using:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_cache/live-guide-final-checks
```

This validates one guide and the exercised API paths. It does not verify every
future model response, app functionality, news-feed access or website publishing.
