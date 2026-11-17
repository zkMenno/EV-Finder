# CI budget: do the work in the session, let CI confirm

Owner: WS0. Rule P-21. Source: GardenLayer handoff #813 (17 Nov 2026), adapted.

## Why this repo is different from GardenLayer
- EV-Finder is **public**. Standard GitHub-hosted runners (`ubuntu-latest`, `ubuntu-24.04-arm`) are free and unmetered on public repos, so this repo does not draw from the account's 2,000 free minutes.
- GardenLayer is **private**. Its runs are the ones that use up the shared 2,000 minutes (2,865 billed minutes 1–17 Nov, 95% Arm).
- So the rules below are about speed and keeping CI honest here, and about money only if this repo ever goes private or uses larger runners.

## Never without WS0 + Menno
- Larger runners (`*-4-core`, `*-8-core`, GPU…): billed per minute even on public repos.
- Making the repo private: every run then counts against the 2,000-minute account budget shared with GardenLayer.

## How every chat works
1. **Local gate first.** Before opening or pushing to a PR, run in the session what CI would run for the lanes you touched: web (`pnpm lint`, `typecheck`, `test`, `build`), pipeline (`ruff check`, `ruff format --check`, `pytest`), schema and data checks. Open the PR only when green. A session machine is free and usually faster than a 2-core runner.
2. **One PR per batch.** A branch push starts nothing (CI runs on PRs and on `main`). Push work to branches freely; open the PR when the batch is ready, not as a draft to "see if CI passes".
3. **Fix locally, push once.** Red CI: reproduce and fix in the session, then push one fix commit. Each push re-runs the whole PR.
4. **No "just to check" dispatches.** `workflow_dispatch` only for P-10 (session pushes that don't trigger CI) or one named job you need.
5. **Keep path filters and `cancel-in-progress`.** `ci.yml` only runs the lanes that exist and changed; `images.yml` only builds on PRs that touch app or Docker files. New workflows copy that pattern.
6. **Never replace CI with "it passed locally".** CI is the independent check (P-15). Local runs cut the red reruns, they don't skip the green one.

## Ideas parked until the repo goes private
- Path checks per job (skip pipeline tests when only `apps/web/**` changed) on PRs too.
- Weekly instead of per-PR heavy suites; data-refresh stays weekly.
- A `scripts/local-ci.sh` that mirrors `ci.yml` exactly, so every chat runs the same gate.
