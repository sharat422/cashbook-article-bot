# News-source path validation — 6 November 2026

**Update — 8 November 2026:** The explainer was independently re-reviewed against the live GOV.UK source, approved at the recorded hash, exported and published. See PUBLICATION_RECORD.md for the live URL and deployment checks. The remaining text records the original 6 November validation state.

Result: one relevant, dated, evidence-backed explainer reached **awaiting_review**.
It is not approved, exported or published. This validates a reviewed source workflow,
not unattended model extraction or automatic weekly topic selection.

## Publisher access and permission

- PIB robots returned HTTP 403; RBI robots returned HTTP 418. Both remain skipped by
  the unchanged fail-closed access checks. Their full-page extraction stays disabled.
- Added the official GOV.UK India-news Atom feed to `sources.json`:
  <https://www.gov.uk/search/news-and-communications.atom?world_locations%5B%5D=india>.
- GOV.UK robots rules were accessible and allowed the feed and selected article for
  `CashbookResearchBot/0.1`. The existing URL, DNS, size, redirect and robots checks ran.
- [GOV.UK terms](https://www.gov.uk/help/terms-conditions) explicitly describe feeds
  and permit reuse of covered content under the Open Government Licence. The selected
  page displays the OGL v3.0 notice. Use attribution; exclude third-party material and
  images; do not imply government endorsement. Only article text was extracted.

## Usable collection and selected evidence

`python -m cashbot collect` saved **five dated sources**, while logging PIB/RBI warnings.
The collector extracted two pages within its existing per-source bound. The selected
third item was enriched with `add-url` through the guarded page-extraction tool.

Selected source:

- ID: `0d641ebfca7a`.
- Publisher: GOV.UK India news.
- [Joint Statement of 16th Meeting of the India–UK JETCO](https://www.gov.uk/government/news/joint-statement-of-16th-meeting-of-the-india-uk-jetco).
- Feed timestamp retained: `2026-10-12T13:08:12+00:00`.
- The original page says Published 12 October 2026 and dates the statement New Delhi,
  12 October 2026. This confirms the calendar date independently of the feed metadata.
- Extracted text: **4,843 characters / 730 words**, not a headline-only summary.
- Original-text SHA256:
  `0e2c2d5a79bac2631544d10024aa9e06c4b0f7d55c6376ec050da3baff797614`.
- Local source snapshot: `data/news-validation-source.json`; the source is also
  embedded in the persisted checkpoint and article review JSON.

The relevant material concerns announced usage-data exchange, small and medium-sized
businesses, feedback on implementation issues, and the next JETCO in 2027. Relevance
is limited to Indian agencies/distributors with UK-linked trade; it is not a general
claim that every Indian shop qualifies for treaty benefits.

## Evidence extraction and review intervention

Two OpenAI evidence-brief attempts proposed quotes that failed the exact-substring
validator. Both stopped before drafting. The validator was not relaxed or bypassed.
Codex then prepared a six-claim brief from verbatim passages checked on the original
page. Every quote passed the same `Brief` schema and `validate_brief` checks before
resuming the graph at drafting. The curated brief is saved in
`data/news-validation-brief.json` and the article review report.

This intervention is a limitation of the model's evidence extraction. Do not treat
this run as proof that the full pipeline can operate without editorial oversight.

Claude drafted from that brief; OpenAI checked the article. Codex separately reviewed
the evidence, dates, relevance and product claims, then edited and rechecked clarity:

- Government announcements are distinguished from optional record-keeping suggestions.
- No tariff rates, eligibility, filing obligations or calendar commencement dates
  are inferred from the statement. No savings or preferential treatment are promised.
- CETA is expanded and the publication date is distinguished from announced plans.
- The order-record example is explicitly fictional, not evidence of business results.
  Its arithmetic checks: 40 + 25 + 35 = 100 cartons; at Rs 1,200 each, invoice values
  are Rs 48,000, Rs 30,000 and Rs 42,000, totalling Rs 1,20,000.
- Bolcash wording stays within the owner-approved pre-launch facts, without a CTA.
- Unsupported comparisons between software and spreadsheets were removed.

## Final saved job

- Job: `explainer-2026-w45`.
- Draft: `drafts/explainer-2026-w45.md`.
- Evidence/review: `drafts/explainer-2026-w45.review.json`.
- Status: `awaiting_review`; next node: `human_review`.
- Automated blocking issues: **none**. All source citations and six evidence quotes checked.
- SHA256: `932a08863c83750f9b961c5b9347f49cd42fc58666e7950b2bb4b3337f6fe234`.
- No `approved/explainer-2026-w45*` files exist.

## Code correction and tests

`add-url` previously discarded a known publication date when replacing a feed summary
with extracted text. It now retains the exact matching URL's existing publication
date and publisher, and records extraction time. It does not invent a date for an
unknown URL. A regression test verifies preservation and deduplication.

Python 3.12.10: **40 passed in 18.19 seconds**, using:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_cache/news-source-path
```

Feed availability, terms and relevance need ongoing review. Five collected items do
not establish a sustainable supply of weekly stories. This run does not establish
PIB/RBI access, scheduled ranking quality or website publication.
