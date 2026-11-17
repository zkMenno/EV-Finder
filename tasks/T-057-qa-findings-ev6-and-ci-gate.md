# T-057 Qa findings ev6 and ci gate
Role: WS1   Lane: pipeline/ev_pipeline/qa, .github   Wave: proposed by overnight 1
Status: merged (PR #1); fresh review via QA A-35; earlier note: pipeline builder, 2026-11-15

## Goal
Fix the QA finding (Kia EV6 77 kWh AWD usable 80 kWh > pack gross 77.4) and run the release QA in CI on every PR that touches data.

## Acceptance criteria
- [x] EV6 row fixed via pack link or source review
- [x] CI job runs `ev release --dry-run` + QA and fails on blocking checks (QA on the committed release; see notes)
- [x] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes
- **Cause:** KilowattApp records "EV6 Long Range AWD" MY2024 and "EV6 GT" MY2025 (80 kWh usable, 263 kW) are the 2024 facelift (84 kWh pack, egmp-84). The matcher put them on the 2021 variants (no year band: band thresholds are WLTP 5 % / DC 10 % only), and `battery_kwh_net` merges by source rank first, so KilowattApp's 80 beat the seed's 77.4.
- **Fix (rule, no number edited):** `pipeline/ev_pipeline/qa/pack_guard.py`. A `battery_kwh_net` fact above the linked pack's `gross_kwh` (+0.05 rounding) is kept out of the merge and written to `data/review/conflicts.csv` with tolerance `> pack <id> gross <g> kWh`. If every usable fact is too big, nothing is removed (then the link is the likely error, and QA `usable_gt_gross` flags it). Hook: 4 lines in `release/build.py` (`guard_usable_vs_pack` before the merge, `fill_winning_values` after, rows added to `conflicts`). With it, EV6 AWD and GT show 77.4 and the QA has no `usable_gt_gross` items. Six other already-conflicting facts (Audi e-tron 50/55, Model 3 SR+ LFP, Model S 85, ID.3 Pure) now carry the pack reason.
- `data/seed/variant_links.yaml`: notes on the EV6 AWD and GT links record the evidence. Links unchanged (2021 rows really use egmp-77-4).
- **CI:** new `data-qa` job in `.github/workflows/ci.yml`. `detect` gets a `data` output (git diff vs PR base / push-before on `data/`, `config/`, `pipeline/`; manual runs and unknown bases always run it). Steps: `uv sync --locked`, the three validators, then `uv run python -m ev_pipeline.qa check-release ../data/releases/latest`. It's in `ci-ok`. Read-only token, SHA-pinned actions as before. `ev release --dry-run` can't run in CI (staging is git-ignored), so the job re-checks the committed release instead.
- **Entry point:** `pipeline/ev_pipeline/qa/check_release.py` + `qa/__main__.py`. Takes a release folder or the `latest` pointer, plus `--data-dir` and `--json`. Re-runs provenance + licence gate (blocking); impossible values are only reported. Exit 0 pass, 1 blocking fail, 2 bad input.
- **Tests:** `tests/test_pack_guard.py` (EV6 regression with the real seed links, edges) and `tests/test_qa_check_release.py` (fixture release, failure paths, bad input, and the real committed release).
- **Open:** (a) `validate_taxonomy.py` fails today on 25 new T-051 generations without links, so `data-qa` is red until those are added. (b) `test_real_release.py::test_registrations_are_never_summed_across_sources_or_periods` fails on the rebuilt release (EEA history, T-053; reported in Q-083). Neither is from this task. (c) The facelift needs its own variant or year band (Q-084).

## Review
