# T-149 Publish popularity, used-price source licences and photo licence templates
Role: builder   Lane: pipeline (WS1)   Wave: launch
Status: review (batch chat https://claude.ai/code/session_01JuyZETPZUUpdfhHpfB9Pef, 2026-11-19)

## Goal
Fill the three fields WS0 added to the schema (PR "WS0: release 3 schema fields"): `Generation.popularity`, `UsedPriceSourceRef.licence`, `GenerationImage.licence_template` + `licence_checked_at`.

## Acceptance criteria
- [ ] `Generation.popularity` is computed in the pipeline with the weights in `config/popularity.yaml` (registrations from the release's registration facts, owner picks from `data/editorial/menno-picks.yaml`), `rank` 1 = most popular, `as_of` = newest registration data used, `source_ids` = the release source ids actually used. Absent when no registrations matched.
- [ ] Same ranking as today's web build (`apps/web/scripts/popularity.mjs`) on release 3 inputs, or every difference explained in the PR (the release field replaces the top40 registration input, so some moves are expected; list the top 20 before / after).
- [ ] Every `UsedPriceSourceRef` carries `licence` (SPDX id where one exists); the licence comes from the source registry, never typed per row.
- [ ] Commons photos record `licence_template` and `licence_checked_at` from the file-page check `ev images check` already does (Decision 083). Press photos leave them out.
- [ ] Release QA: a Commons photo without `licence_template` is blocking; a photo whose template doesn't match its `licence` (the "CC BY photo with a stray template" case) is blocking.
- [ ] `PD-old` (and `PD-old-70`, `PD-old-100`, worldwide variants only) added to the template allowlist, per Decision 083.
- [ ] Tests with fixtures; `ev verify --base main` output in the PR; the data diff of the next refresh shows only the new fields.

## Inputs
Decision 038 (popularity blend), 081, 083; WS0 INBOX 2026-11-18 19:14 UTC (batch: data / release 3); T-130.

## Out of scope
Web changes: WS2 switches `popularity.mjs` to the release field in a follow-up once a release carries it. Photo bundling (T-150).

## Handoff notes
- **Popularity** (`pipeline/ev_pipeline/derive/popularity.py`, attached in `build_release`): reg share per ranking source of the top-40 method (`qa.top40.RANK_SOURCES`: RDW NL fleet, DfT UK fleet) against the catalogue's total for that source, averaged; model-level counts split over the model's generations by RDW generation counts (evenly without them), same rule as `apps/web/src/lib/popularity.ts`. Weights, pick values and favourite bonus from `config/popularity.yaml`; picks from `data/editorial/menno-picks.yaml`. `registrations` = attributed counts summed over the sources used (display figure); `as_of` = end of the newest period (RDW date, DfT quarter end). No count → no field (schema), so 10 pick-only generations get none (listed in the run log `popularity.picks_without_registrations`). A scratch data dir (ev verify) reads the repo's `config/` (`build.config_dir`).
- **Ranking vs the web build on release 3 inputs:** Spearman 0.964 over the 83 generations both rank; the release field ranks 138 (every generation with a fleet count, not only top-40 models). Moves come from the release's RDW count being the whole fleet (top-40 used the 2018–2024 first-admission window): newer cars rise (Elroq 46→13, Polestar 4 24→15, ID.7, EX30), older facelift splits fall (EV6 gen1 16→28). Top 20 before/after in the PR body.
- **Used-price licences:** `attach_source_licences` sets `source.licence` on every band from `data/sources.yaml` (sample band: its `source_id`; model band: `model-estimate`). SPDX id when the entry names a licence, else the entry's own words (`none (site terms of service)` for Marktplaats / 2dehands, aggregates only, Decision 060). Run log: `used_prices.source_licences`.
- **Commons templates:** `ev images fetch` (and the nightly `fetch_images`) reads each Commons file page once (`commons.wikimedia.org`, `action=raw`, host added to `data/sources.yaml`) and caches the page text next to the original, so a better parser needs no re-read and the field (and its date) stays stable. The build keeps a Commons photo only when a licence template on the page grants its licence (`template_matches`: `self|…`, GFDL combos, `cc-by-sa-3.0,2.5,…`, `2.0+` = or later, `{{YouTube CC-BY}}` = CC BY 3.0) and no deletion/copyvio/FoP template; photos.yaml templates (WS3's CC0/PD check) take precedence. Release QA `images` blocks a Commons photo without template or with a stray one from release 4 on (1–3 predate the rule: listed under `template_rule_not_applied`).
- Real run (2026-11-19): 116 pages read, **119 of 120 photos pass**; `byd-atto-3-gen1` goes to review: its page only has a user template (`{{User:VulcanSphere/CC-BY-photos}}`). WS3 can expand it and record the template in photos.yaml (INBOX line).
- `PD-old`, `PD-old-70` added (PD-old-100 was there); US variants like `PD-old-70-1923` stay out. Mirror in `data/images/tools/check_templates.py` (WS3 file, one-line cross-lane change, test keeps both equal).
- Same-data rebuild (fresh staging, main code vs this branch): rows, sources and every other generation field identical; generations gain `popularity` (142) and image templates (118 photos); `byd-atto-3-gen1` photo dropped; used_prices identical apart from `source.licence` (2461 CC-BY-4.0, 422 site terms, 0 missing). The 2 blocking release-diff lines (Elroq base NL list price cleared) appear with main's code too: new staging, not this PR.
- Web follow-up (out of scope, WS2): switch `apps/web/scripts/popularity.mjs` to `generations[].popularity` once a release carries it.

## Review
