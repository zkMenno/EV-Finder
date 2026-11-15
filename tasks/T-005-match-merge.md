# T-005 Match merge
Role: builder   Lane: pipeline/ev_pipeline/merge   Wave: 2
Status: review

## Goal
Map source records to variants, merge with priority/majority/recency, confidence.

## Acceptance criteria
- [x] Rules-first matching
- [x] Unmatched rows → data/review/unmatched.csv
- [x] Tests for each merge rule
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

**Done (builder, 2026-11-15).** Code: `pipeline/ev_pipeline/match/` (normalise, seed, matcher,
review) and `pipeline/ev_pipeline/merge/` (merge, policy). Tests: `tests/test_match.py`,
`tests/test_merge.py`; fixtures `tests/fixtures/release/`.
- Matching: accent/case/punctuation-free keys, longest whole-token prefix against seed name +
  `name_aliases` (with or without the make name), tiny `MAKE_ALIASES` (VW, Mercedes-Benz,
  Vauxhall...). Generation by year; shared boundary year goes to the newer generation (Q-014).
  Variant id `<generation>-<slug(name or 'base')>`; a seed-manual variant with the same
  normalised name lends its id. Units normalised (Wh/km, miles, currencies); bad units go to
  validation.csv. Registration counts aggregate per generation (model-level only for
  single-generation models, never double counted).
- unmatched.csv: 1412 rows tonight (seed makes in detail, other makes as one summary row each).
  3908 records of seed makes are unmatched, almost all long-tail models (EQB, iX, Ariya...) plus
  registration-style names the seed lacks (Q-021).
- Merge: `data/field_sources.yaml` drives priority order, tolerance and mode (priority / median
  as a real low-median value / newest); unlisted fields keep majority(3+) → priority → recency at
  3%. Confidence high on 2+ independent agreeing sources; seed-manual and model-estimate never
  count as independent (Q-015). Conflicts → data/review/conflicts.csv (489 tonight), never
  averaged.
- Surprise: EEA rows have no variant name, so they sit on `-base` variants and never agree with
  OpenEV's named variants; only 1 WLTP value tonight has 2 agreeing sources (Q-019).

Release 1 published from real staging (openev 1229, rdw 3124, eea 3430 records) + seed: 210 rows,
56 generations, 6554 facts, catalogue.json 1.96 MB raw / 96 KB gzipped. Run: see pipeline/README.md
"Run the pipeline". Checks green: `uv run pytest` (154), `ruff check .`, `ruff format --check .`.
Includes coordinator addenda: Decision 009 (field_sources policy, conflicts.csv, licence gate,
coverage.md, charge curves) and Decision 010 (platforms, packs, voltage, taxonomy).
Open questions raised: Q-014 to Q-023 in QUESTIONS.md.

## Review

**Reviewer (fresh agent), 2026-11-15. Verdict: changes needed (matching correctness).**

All four boxes hold as written: rules-first matching, `data/review/unmatched.csv` (1,411 rows), per-rule tests in `tests/test_match.py` / `tests/test_merge.py`, offline. Merge never averages. That is now also checked on the real release: every non-derived number equals one of the facts it cites (`tests/test_real_release.py::test_merged_values_are_never_averages`). conflicts.csv has 489 rows.

Spot check: 10 random release rows (seed 20261115) traced back to `data/staging/*.jsonl` and seed. Units were right in all 10 (Wh/km→kWh/100km, kWh, km, mm, counts). Mismatches:
1. **Wrong model: Audi e-tron GT counted as e-tron / Q8 e-tron (high).** `match/matcher.py:131-157` accepts the longest *prefix* and ignores trailing tokens. So RDW `E-TRON GT` (2021-25), `AUDI E-TRON GT`, `e-tron GT` and `E-TRON GT QUATTRO` all land on `audi-e-tron`, and their counts go into `audi-e-tron-ge` (15,088) and `audi-e-tron-q8` (425). The seed even says "Do not confuse with e-tron GT" (`data/seed/models.yaml:549`), and `RS E-TRON GT` *is* rejected, so behaviour is inconsistent. Fix: a per-model `exclude_tokens`/negative-alias list (GT, plus Q4/Q6/A6 for e-tron), or require that leftover tokens are known trim words.
2. **Wrong generation: Nissan Leaf gen3 gets ZE1 data (high).** The EEA and RDW records `NISSAN LEAF 40KWH|2025` go to `nissan-leaf-gen3`, because the shared boundary year goes to the newer generation (`matcher.py:167`, Q-014). The "40KWH" marks it as a ZE1 (gen3 has other packs). So `nissan-leaf-gen3-base` ships WLTP 278 / 16.8 kWh/100km / 1,580 kg / count 385, all ZE1 figures. In a shared year, prefer a generation whose variant names or pack sizes match tokens in the record, and send the rest to review instead of picking the newer one.
3. **Kona Electric OS count = 1.** Bare `KONA` isn't an alias (see T-003 review), so the real NL fleet is unmatched. A count built from a near-empty match should be suppressed or flagged, not published.
4. **Old variants take the newest model-year specs (medium).** `merge/merge.py:78` ranks by priority, then retrieved_at, then *record year*. A variant spanning many years merges OpenEV 2024/2025 records and the newest wins. Example: `volkswagen-id3-gen1-pro` (year_start 2020) shows dc_peak 135 kW and WLTP 428 from the 2024/2025 OpenEV files. A 2020-21 ID.3 Pro charged at about 100-120 kW. For a used-car finder this is the wrong default. Split variants at change markers, or keep per-model-year values and show a range.
5. Correct in the sample: Q8 e-tron 55 Sportback (OpenEV 2024/25 → `audi-e-tron-q8`, right generation; the 100 kWh net is what the source says), Tesla Model S 85 / Model 3 SR+ LFP / Kia EV6 58 / Ioniq 6 77 / Zoe R90 (seed-manual, right generation), Model S Plaid (OpenEV 2025 + seed), Dacia Spring (EEA 2025 → gen1; per-variant values are averages, see T-004).
