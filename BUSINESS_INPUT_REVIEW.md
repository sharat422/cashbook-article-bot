# Business input review — 6 November 2026

Status: approved for drafting within the limits in `app_facts.json`.
The owner confirmed the public name, planned release date, tested features and
absence of a marketing URL in this chat on 6 November 2026. `owner_verified` is
now true on that basis, rather than a new independent device test or launch sign-off.

## Approved product facts

- Public name: **Bolcash**.
- Release: **planned for 20 November 2026**, interpreting the owner's "NOV 20" as
  the upcoming date. The app remains pre-launch. Do not guarantee the date or
  automatically announce availability when it passes.
- Owner-approved features: income, expenses, customer records, receipt scanning
  with OCR and display of extracted details, recurring expenses, reports,
  adding expenses by speaking and requesting business details by speaking.
- No landing-page or waitlist URL is approved. `marketing_url` stays empty;
  omit download/registration CTAs. Do not substitute the domain configured in
  the neighbouring website repository.

The owner's "no more manual" is represented as voice-assisted entry and queries,
not a promise that all work is automatic. Review receipt extraction and financial
entries. Do not claim perfect recognition, guaranteed savings, automatic UPI
confirmation or automatic bank reconciliation. No additional features, supported
languages, report formats, pricing, store listings or customer outcomes were approved.

## Editorial material approved for drafting

Codex reviewed `editorial_notes.md` against the four topics in `guide_topics.json`:

- The example is explicitly fictional, with no customer identity or claimed results.
- Arithmetic is correct: Rs 18,500 - Rs 7,000 - Rs 1,500 = Rs 10,000.
- Money received and an accepted goods-return adjustment are described separately.
- The checklist and reminder checks are suggestions, not legal requirements or
  promises of improved collections.
- The four topics have supporting material, but share one example. Each guide
  should answer its distinct question rather than repeat the other articles.
- The goods-return example is educational material, not an approved app feature.

These notes support educational guides, not news, tax rules, eligibility claims
or business statistics. Every generated article still requires review and approval.

## Evidence and follow-up

Neighbouring repositories were inspected read-only. The app's `app.json` displays
`Bolcash`; website documentation describes an unlaunched app. The app test plan
contains an unchecked production sign-off. Tests in those repositories were not run
and were not treated as completed device testing. Owner confirmation above
supplies the approval for this bot's feature list.

Reconfirm availability before announcing launch. Add a marketing URL only after
the owner supplies one and the destination is checked. Re-review approved features
and limitations after product changes. Existing saved jobs retain their original
product-facts snapshot; these updated facts apply to new jobs.
