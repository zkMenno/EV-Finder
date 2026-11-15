# T-062 Retired ids map
Role: coordinator (schema) + WS2   Lane: packages/schema, pipeline/release, apps/web   Wave: proposed by overnight 1
Status: review, pipeline part (WS1, 2026-11-15); schema + web parts open

## Goal
Stable ids never 404. When a release merges or removes a variant (Decision 033), the catalogue carries `retired_ids: {old_id: successor_id | null}` and the web app redirects (308) old variant URLs and keeps old ids in compare links working.

## Acceptance criteria
- [ ] Schema: additive `Catalogue.retired_ids` (coordinator)
- [x] Pipeline: `ev release` computes it against the previous release plus a hand-kept `data/seed/retired_ids.yaml`; it never shrinks between releases
- [ ] Web: old variant URL → 308 to successor; removed with no successor → 410 page with a link to the generation; compare `?ids=` maps old ids
- [ ] Tests cover it (fixtures, no live network calls)

## Inputs
DECISIONS.md 033, the 19 ids removed on 2026-11-15 (git log), release diff.json.

## Out of scope
Anything not named above.

## Handoff notes
**WS1, 2026-11-15 (PR `t-062-retired-ids`, pipeline part).**
- `release/retired.py`: map = previous map ∪ ids gone since the previous release ∪
  `data/seed/retired_ids.yaml` (WS3, `schema: retired-ids/v1`, `ids: {old: new|null}`).
  Never shrinks, except an id that is live again (logged as `live_again`); chains resolve
  to the last live id; a dead successor becomes null (logged).
- Until `Catalogue.retired_ids` is in the schema it ships as `retired_ids.json`
  (`{release, generated_at, retired_ids}`, kept in git like the QA files). When WS0 adds the
  field, the same map goes into catalogue.json automatically (`has_catalogue_field`).
- Release 1 → 2 will retire nothing unless rows vanish (release 1 was never public).
- WS2: 308 to the successor, 410 page for null (shape in WS2's INBOX).

## Review
