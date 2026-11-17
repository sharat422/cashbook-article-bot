# First approved article published — 6 November 2026

Public article:
<https://bolcash-practical-guides.berryfennel2.chatgpt.site/guides/recording-partial-payments/>

Public guide index:
<https://bolcash-practical-guides.berryfennel2.chatgpt.site/guides/>

## Platform and scope

The existing marketing project at `../bolcash-website` is Next.js 15.5.28 App Router,
configured with `output: "export"`, pnpm and static HTML output. It had no guide
routes or deployment configuration. The owner confirmed no hosting had been set up.
`bolcash.in` was not reachable and has not been connected or changed.

Added the article JSON and two Next.js routes to that repository:

- `content/articles/recording-partial-payments.json`
- `web/app/guides/page.tsx`
- `web/app/guides/recording-partial-payments/page.tsx`

Formatting, article-route ESLint, type-checking and all **24 website unit tests** passed.
The Next.js production build succeeded and statically exported the guide and index.
It reported an existing multiple-lockfile workspace-root warning. Existing unrelated
files were left in place; no bulk commit/push of that unfinished repository occurred.

For public hosting, created a small Sites static project containing only the approved
HTML article and guide index. The unfinished homepage, other marketing content,
backend files, secrets and internal editorial notes were not deployed. This is the
approved HTML publishing route, alongside the prepared Next.js integration.

## Content handling

Approved job: `guide-2026-w45`.
Original checked SHA256:
`c82052e3b07be13fe3fd04dee0fe53c26b8d3969475660cd1485b4a2dde81402`.

The published body comes from its sanitized approved HTML. Publication changes are
presentation only: page title/description, navigation, update date, responsive table
styling and linked source markers. Source attribution identifies the original
fictional teaching material; it does not expose internal notes or claim an official
legal source. There are no download/signup calls to action.

Automatic approval review rejected the first package because it included the full
internal editorial notes. That package was revised before copying or publishing:
the notes were removed, leaving the approved article and short public source credit.

## Deployment and checks

- Site project: `appgprj_6aee6bc0239c81918185217c3ca05613`.
- Saved version: `appgprj_6aee6bc0239c81918185217c3ca05613~appgver_18902f2cb9ac8191b46d3c61991fc42e`.
- Source commit: `5f2a5ced22fb3c9ff3369b664a1541e513782b82`.
- Deployment: `appgdep_6aee6cde2c1081918eb58050b7d52961`, **succeeded**.
- Audience: public.
- Local publication source: `publication/bolcash-guides-site`; preserve its
  `.openai/hosting.json` project identity for future updates.
- Anonymous HTTP checks returned **200** for `/`, `/guides/` and the article route.
- Checked article title, one H1, two tables, update/release dates, guide navigation,
  working source-credit anchor, and absence of internal source paths/notes.
- The visible browser-opening attempt timed out. Public availability and HTML
  structure were verified by anonymous HTTP; no screenshot/mobile visual QA is claimed.

`approved/guide-2026-w45.approval.json` now records `publicly_published: true`,
the public URL and publication timestamp, preserving the approved content hash.
The news explainer remains unapproved and was not published. The app marketing URL
in `app_facts.json` was not changed automatically.


# Second article published — 8 November 2026

- Article: https://bolcash-practical-guides.berryfennel2.chatgpt.site/guides/india-uk-jetco-record-keeping/
- Job: `explainer-2026-w45`; status approved/finished.
- Approved SHA256: `932a08863c83750f9b961c5b9347f49cd42fc58666e7950b2bb4b3337f6fe234`.
- Re-read the live GOV.UK statement: publication/statement date 12 October 2026, annual exchange relative to CETA entry into force, business feedback and next JETCO in 2027 match. All six brief quotes match the saved source verbatim.
- Verified fictional order arithmetic: 100 cartons; Rs 48,000 + Rs 30,000 + Rs 42,000 = Rs 1,20,000.
- Reviewed Bolcash claims against owner-approved facts; pre-launch status retained. No tariff eligibility, legal requirement, guaranteed savings or customs functionality inferred. No blocking review issues.
- Exact-hash CLI approval preceded all four exports and website publication. No paid model calls needed for this final review.
- Public presentation preserves approved article wording, changes citation markers into linked references, adds publication/source dates, navigation and OGL attribution. No internal source snapshots or notes deployed.
- Added article to both root and /guides/ indexes. Prior article preserved.
- Existing public Site reused: `appgprj_6aee6bc0239c81918185217c3ca05613`.
- Source commit: `b9e74437c777eb06848228bd1dcea556001e95a2`.
- Saved version: `appgprj_6aee6bc0239c81918185217c3ca05613~appgver_79985d4baf74819198595d3b1e9d0aa4`.
- Deployment: `appgdep_6af0c353675c8191844554c36ad97eed`, succeeded.
- Anonymous HTTP 200: root, guide index, prior guide and new explainer. Checked new title, table, source anchor, attribution, worked total and index links. Browser opening queued; no visual screenshot QA claimed.
- Publication metadata updated in the explainer approval JSON. App marketing URL remains unchanged.
