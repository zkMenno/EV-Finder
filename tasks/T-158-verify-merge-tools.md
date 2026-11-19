# T-158 Verify and merge tools: `ev verify --keep`, approved_changes warning, merge_ready.sh
Role: builder   Lane: pipeline/ (WS1); scripts/merge_ready.sh (WS0-owned, built here, flag it)   Wave: launch
Status: review (batch: data T-161 + T-158, 2026-11-19)

## Goal
The merge and verify tools stop the misses the 19 Nov batches hit by hand.

## Acceptance criteria
- [x] **G-53:** `ev verify --keep <dir>` keeps its scratch build so a builder can trace where a value came from.
- [x] **G-54:** approved_changes validation warns when an entry's `release` is ≤ the latest published release when its PR merges.
- [x] **G-52:** `scripts/merge_ready.sh <pr>` exits non-zero when the PR branch is behind main (`compare main...head`, behind_by > 0) or CI on the head isn't green, with a plain message. Merge batches run it as its own step, before the merge command. Cross-lane (WS0 file), flagged in the PR.
- [x] **G-56:** `ev verify --base-release-from <ref>` builds the base ref on the same staging and diffs against it (T-154 retro: diffing a fresh staging against committed release 3 gave ~10k blocking lines).
- [x] **G-57:** `data_qa.sh` runs `load_config` on `data/review/approved_changes.yaml`, so a bad `approved_by` fails there, not in the loader.
- [x] `ev verify` lists `pipeline/ev_pipeline/qa/value_guard.py` (and the other rule globs in T-155 Handoff notes) as changed rules.
- [x] **Refresh-lock nits** (T-153 follow-up 5, #185 review): a refused `ev refresh` prints its own wording (not verify's); a short refresh inside a verify rebuild is detected.
- [x] Tests with fixtures (no network: the script's GitHub calls are mocked or it takes JSON on stdin in tests); docs/process/README.md merge steps mention the script (one line, flagged).

## Inputs
WS0 INBOX 2026-11-19 03:32 UTC (batch: T-151, retro 4); rules G-52–G-54.

## Out of scope
Data changes (T-155). Branch protection settings (Menno's account).

## Handoff notes
- **`ev verify --keep <dir>`** (G-53): copies the whole scratch tree (`data/` with the built release, `review/` incl. release_diff.csv and validation.csv; staging stays a symlink) to a new or empty folder; refuses a non-empty one before building. Report line "Scratch build kept in …".
- **`ev verify --base-release-from <ref>`** (G-56): `git archive <ref>` (minus release folders, apps/, _archive/) into the scratch dir, then a child process builds it with **the ref's own code** (its `pipeline/` first on sys.path; the venv's editable install is a plain .pth entry, the child asserts it imported the ref's copy) on this checkout's staging, as release latest+1 with no N-1 of its own (so no release diff can block the base; retired ids / review-only carry-overs aren't compared). That folder then stands in for release N-1 in the head build, so release numbers and approvals scope as usual. Measured: main vs T-161 on the 2026-11-19 staging, both builds ~30 s each. Fixture test: a staging change under the committed release blocks plain verify (1) and gives 0 with `--base-release-from HEAD`.
- **`ev release approvals`** (G-57 + G-54, `release/approvals.py`): loads `config/approved_changes.yaml` with the build's `load_config` (error → exit 1) and warns on entries this branch adds (exact-entry diff vs `--base`, default origin/main, or `--base-file`) whose `release` is ≤ the latest published release; `--strict` makes a warning exit 1. `data/seed/data_qa.sh` runs it (WS3 file, cross-lane). 🟡 rules.md G-57 says `data/review/approved_changes.yaml`; the file is `config/approved_changes.yaml`.
- **`scripts/merge_ready.sh <pr>`** (G-52 / G-59 / G-54; WS0 file, cross-lane): stdlib Python behind a sh wrapper, GitHub REST via `gh api`. Not ready when: PR not open; `compare main...head` behind_by > 0 unless every file main is ahead by is INBOX / HANDOFF / CHATS.md **and** `mergeable_state` is clean (G-59); no check run on the head; the newest run per check name isn't completed success / neutral / skipped; a commit status isn't success; the PR touches approved_changes.yaml and an added entry is scoped to a release main already published (runs `uv run ev release approvals --strict` on the head / base file contents). Exit 0 ready, 1 not ready (reasons printed), 2 GitHub error. `--from-json` for tests / dry runs. Live: #190 → NOT READY (45 behind, real files); #193 → not open.
- **Changed-rule globs**: + `qa/value_guard.py`, `backtest/*`, `data/manual/*`, `data/sources.yaml`, `data/field_sources.yaml`, `config/popularity.yaml`.
- **Refresh-lock nits**: a refused `ev refresh` says "another ev refresh is already writing data/staging …" (`busy_message(.., "refresh")`), verify keeps its wording. Every refresh that takes the lock writes `data/staging/.refresh.last` (kept after the run); verify compares it before / after the rebuild, so a short refresh that started and finished meanwhile fails the run.
- **Docs**: docs/process/README.md §6 one line (WS0 file, cross-lane); the verify skill mentions `--base-release-from` and `--keep`.
- Review round 1 (#195 at 9dd6ee8, PASS WITH NITS): fixed should-fix 1 (verify reads the `.refresh.last` stamp before the busy check, test) and nits 2 (`--keep` refuses a file and a folder inside data/), 3 (base-build failure shows the exception headline), 4 (`--base-file` that isn't YAML → ERROR, exit 1; unreadable git base → every entry counts as new), 6a (PR files paged). Left: data_qa.sh reads the branch's own `data/releases/latest` (merge_ready reads main's: that is the merge-time check); CI doesn't run the approvals step (ci.yml, gate change for WS0); `latest_runs` keys on job name (a dispatch re-run must replace the PR run); G-59 judges the net compare diff.
- Follow-ups for WS0: rules.md G-52 / G-53 / G-54 / G-56 / G-57 / G-59 "Enforced by" columns can now name the tools (gate file, WS0); G-57's path.

## Review
