# T-063 Optional on-board charger field
Role: coordinator (schema) + WS1 + WS2   Lane: packages/schema, pipeline, apps/web   Wave: proposed by overnight 1
Status: review (WS1 pipeline part, 2026-11-17, 4th WS1 session); web part → WS2

## Goal
Decision 034: `ac_kw` = standard on-board charger; add `ac_kw_optional`. Route source values to the right field (field_sources rules per source), cite both where official sources give both, show "7.4 kW (11 kW optional)" in the web app.

## Acceptance criteria
- [x] Additive schema field `ac_kw_optional` (coordinator; FactField enum entry added by WS1 under WS0's 15 Nov delegation)
- [x] Per-source routing rules in field_sources.yaml; cited standard values win under Decision 028/031 (Decision 046, merge/ac_route.py)
- [ ] Web shows both through `Num` with provenance, EN + NL
- [x] Tests cover it (fixtures, no live network calls): tests/test_t063_ac_optional.py, 12 tests incl. one release build

## Inputs
DECISIONS.md 034, audits/A-06 follow-up table.

## Out of scope
Anything not named above.

## Handoff notes
- 2026-11-17 WS1: pipeline part done (Decision 046). `ac_kw_optional` is a FactField (kW), merges with its own policy row in data/field_sources.yaml, ships in rows with provenance, in the open data bundle, range 2–43 kW, and must be above `ac_kw` (rows drop it, QA flags it).
- Routing is citation-driven only: OpenEV/KilowattApp carry no option signal. No citation for `ac_kw_optional` exists yet, so **release values don't change until WS3 adds them** (verified: `grep -rn ac_kw_optional data/seed data/manual` = 0).
- WS3 ask (INBOX): cite standard + optional for e-208 / e-2008 (7.4 / 11, Stellantis 04-05-2023), Megane EV40 (7.4 / 22), MG4 Standard (6.6 / 11), I-Pace (year split). data/manual works today; seed `cited:` needs `ac_kw_optional` in validate_variants.py SPEC_RANGES (WS3 lane).
- WS2 ask (INBOX): show "7.4 kW (11 kW optional)" through `Num`, EN + NL.
- Dry run on real rows (G-10): 0 citations → 0 moves; check-release on release 1 passes. The fixture build test shows a routed row: option 11 shipped, standard empty, manual fact not shipped.

## Review

### Fresh review — WS1 5th chat (no build context), 2026-11-17 10:30 UTC
Reviewed head **0d168ce** (= PR head ee14201 with origin/main merged in, no conflicts). REVIEW.md read from origin/main.

| Item | Verdict | Evidence |
|---|---|---|
| R0 | pass | All checks green on ee14201 (pipeline, schema, web, e2e, data-qa, audit, gate-guard, repo-checks). Locally on 0d168ce: `ruff check` clean, `ruff format --check` 186 files ok, `pytest -q` **1434 passed**. CI re-dispatched on the new head. |
| R1 | pass | `git diff origin/main...HEAD \| grep -E '^\+(<{7}\|={7}\|>{7})'` → nothing. |
| R2 | pass | PR body has commands + counts + a mutation result + G-10 dry run. |
| R3 | pass | Only test change is the new `tests/test_t063_ac_optional.py` (+258); no thresholds loosened; RANGES adds a row, removes none. |
| D3 | pass | Dry run: `grep -rl ac_kw_optional data/seed data/manual` = 0 files → 0 moves, release values unchanged. |
| D5 | pass | Schema: one additive enum value in ev.schema.json, generated TS + Python regenerated (1 line each). Older releases have no such field, so they still load. |
| D12 | pass | Decision 046 is inside WS1's block (040–049); main has 040–044, #49 holds 045; no duplicate. |
| D13 | pass | New tests use fixtures and tmp_path only. |

**Findings**
1. **should-fix** — the rows guard (`derive/rows.py`: drop `ac_kw_optional` when not above `ac_kw`) has no test. Mutation: replacing the condition with `if False:` → T-063 tests still 12/12 pass. Reachable case: source A 22 kW (matches no citation, stays standard) + source B 11 kW routed to optional. Add one `build_rows` test.
2. **should-fix** — the open-data bundle label for `ac_kw` now says "standard on-board charger", but until citations land most rows still carry the source's max-AC (often the option, per A-06). Label it "standard on-board charger where known, else the source's maximum AC" until WS3's citations cover the A-06 cars.
3. **nit** — removing the "no cited standard agrees" condition in `ac_route.py` also survives the tests; it only matters when cited standard and optional are within ~4 % of each other (practically never), so fine as is.

**Verdict: pass, no must-fix.** Findings 1–2 go into a small follow-up PR by WS1 after merge (before the bundle goes public).

