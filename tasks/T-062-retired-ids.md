# T-062 Retired ids map
Role: coordinator (schema) + WS2   Lane: packages/schema, pipeline/release, apps/web   Wave: proposed by overnight 1
Status: todo

## Goal
Stable ids never 404. When a release merges or removes a variant (Decision 033), the catalogue carries `retired_ids: {old_id: successor_id | null}` and the web app redirects (308) old variant URLs and keeps old ids in compare links working.

## Acceptance criteria
- [ ] Schema: additive `Catalogue.retired_ids` (coordinator)
- [ ] Pipeline: `ev release` computes it against the previous release plus a hand-kept `data/seed/retired_ids.yaml`; it never shrinks between releases
- [ ] Web: old variant URL → 308 to successor; removed with no successor → 410 page with a link to the generation; compare `?ids=` maps old ids
- [ ] Tests cover it (fixtures, no live network calls)

## Inputs
DECISIONS.md 033, the 19 ids removed on 2026-11-15 (git log), release diff.json.

## Out of scope
Anything not named above.

## Handoff notes

## Review
