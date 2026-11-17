# T-003 Seed models
Role: builder   Lane: data/seed   Wave: 1
Status: merged (PR #1); fresh review via QA A-35; earlier note: builder, overnight run 2026-11-15

## Goal
data/seed/models.yaml with the used-EV favourites and generations.

## Acceptance criteria
- [x] All models from the brief, with generations and year spans (brief lists 40, not 44: see notes)
- [x] Uncertain boundaries marked `uncertain: true` with a note
- [x] Validated by a test
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes
**Done**
- `data/seed/models.yaml` (schema `seed-models/v1`): 25 makes, 40 models, 56 generations. 44 of 56 generations are `uncertain: true` (36 of 40 models have at least one), each with a `notes` line saying what is in doubt.
- `data/seed/validate_seed.py` (stdlib + PyYAML): unique ids; ids lowercase a-z0-9 with hyphens; child ids prefixed by parent id; years in range and ordered; generations in one model share at most 1 calendar year (open-ended spans count as infinite); change-marker years inside their generation and in order; `uncertain: true` needs notes; segment/body enums; every brief model present (hard-coded list of 40 model ids) plus key generations (Leaf ZE0/ZE1, Highland, Juniper). `--self-test` runs inline mutated fixtures against each rule. Both pass: `python3 -I data/seed/validate_seed.py data/seed/models.yaml` and `... --self-test`. `ruff check` and `ruff format` clean.
- `data/seed/README.md`.

**Defaults picked without asking (overnight run)**
- Acceptance criteria say 44 models; the brief lists 40. I used the 40 listed. If 4 are missing from the brief, add them and extend `REQUIRED_MODEL_IDS`.
- `name_aliases` sits at model level (the brief's "top-level ... per model"). Some models also have a model-level `notes` field (not in the brief's sketch); the validator allows it.
- Generation ids must start with the model id, so the renamed generations are `kia-niro-ev-de`, `audi-e-tron-q8`, `volvo-xc40-recharge-ex40`, `smart-eq-fortwo-451`/`-453`. Make id for Mercedes-Benz is `mercedes`.
- Splits the brief lists as separate generations were kept as such, including the two that are really renames (Audi e-tron → Q8 e-tron, XC40 Recharge → EX40), flagged uncertain for that reason.
- Added a third Leaf generation (2025+, crossover) beyond the brief's ZE0/ZE1 so ZE1 gets an end year; marked uncertain. Remove it if it is not wanted.
- Leaf ZE0 starts in 2011 (first European deliveries), not 2010 as in the brief's example. AZE0 (2013) is a change marker.
- Model S Palladium starts in 2022 (European deliveries) and ends in 2026 (production end announced early 2026), both flagged.
- Fiat 500e gen 1 years are US model years (never officially sold in Europe), noted.

**Left / for the reviewer**
- The data was written from model knowledge, with no fetched sources, so nothing here meets data rule 1 (traceability) yet. Every `uncertain: true` row needs a hand-check before it feeds published data.
- Segment classes (especially J-small / J-medium / J-large) are judgment calls and are not flagged as uncertain.
- No pytest wrapper: `pipeline/tests/` is outside this lane. The pipeline lane can call `validate()` from `data/seed/validate_seed.py` or run the script.

## Review

**Reviewer (fresh agent), 2026-11-15. Verdict: pass for the prototype; changes needed before any public release.**

`python3 -I data/seed/validate_seed.py data/seed/models.yaml` OK (25 makes / 40 models / 56 generations), `validate_variants.py` OK (123 variants; 7 generations without variants), `validate_taxonomy.py` 0 errors.

Findings
1. **Seed-manual numbers dominate release 1.** 1,706 of 3,642 provenance entries in `data/releases/1/catalogue.json` rest only on `seed-manual` (hand-entered from model knowledge, never checked), and 107 of 210 rows have nothing except seed-manual and RDW counts. The gate passes them, because `data/sources.yaml:13` gives seed-manual `status: active` with a self-assigned CC-BY-4.0 licence. That meets the letter of Decision 009, but not data rule 1 (traceable to a real source). Menno needs to decide whether unchecked seed values may appear in a *public* release, or must stay behind "estimate" styling / a hand-check flag.
2. **Missing alias drops almost all Kona Electric registrations.** `models.yaml:240` has `[Kona EV, KONA Electric, Kauai Electric]` but not bare `Kona`/`KONA, KAUAI`. RDW lists the BEV Kona as `KONA` (the query is BEV-only), so those rows go to unmatched.csv ("model not in seed", 9x and 12x), and `hyundai-kona-electric-os` ships `registered_count_nl = 1`. Add the aliases (bare "Kona" is safe because the RDW and EEA queries are BEV-only), or publish null rather than an undercount.
3. The 40 vs 44 model count is still open (handoff). 44 of 56 generations are `uncertain: true`. That is fine for tonight, but each one must be hand-checked before release (handoff says the same).
