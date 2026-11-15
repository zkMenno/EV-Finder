# T-002 Repo plumbing
Role: builder   Lane: root config, .github, pipeline/pyproject.toml   Wave: 1
Status: review (builder, 2026-11-15)

## Goal
pnpm workspace, uv project, lint/format/typecheck, CI job per lane.

## Acceptance criteria
- [x] `pnpm install` works at root
- [x] `uv sync` works in pipeline/
- [x] CI runs schema, web, pipeline jobs; auto-detect kept
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

**What I did**
- Root: `package.json` (private, `packageManager: pnpm@10.28.0`, engines node >=22; scripts `lint`/`typecheck`/`test`/`build` = `pnpm -r --if-present <x>`, `format` / `format:check` = prettier at root), `pnpm-workspace.yaml` (`apps/*`, `packages/*`, `onlyBuiltDependencies: [esbuild]`), `.npmrc` (engine-strict, auto-install-peers), `.nvmrc` (22), `.prettierrc.json` (printWidth 100), `.prettierignore`, `eslint.config.mjs` (flat base config: @eslint/js + typescript-eslint + eslint-config-prettier; exported `ignores` so packages can extend it), `tsconfig.base.json` (strict, ES2022, Bundler resolution, noUncheckedIndexedAccess). Root devDeps: eslint 9, @eslint/js, typescript-eslint 8, eslint-config-prettier, prettier 3, typescript 5. `pnpm-lock.yaml` updated (also covers `packages/schema`).
- `pipeline/`: uv project `ev-pipeline` (package `ev_pipeline`, hatchling build, Python >=3.12, `.python-version` 3.12), deps pydantic>=2, duckdb, pyarrow, pyyaml, httpx, jsonschema; pytest + ruff in BOTH `[project.optional-dependencies].dev` and `[dependency-groups].dev`; ruff line-length 100 (rules E,F,W,I,B,UP,SIM); `ev = "ev_pipeline.cli:main"` with an argparse `version` subcommand only; `tests/test_smoke.py` (9 tests: version, CLI, required subcommand, core deps importable); `tests/fixtures/.gitkeep`; `uv.lock`; `pipeline/AGENTS.md` lane rules.
- CI: kept detect / repo-checks / ci-ok. Added `schema` detect output + job (`pnpm --filter ./packages/schema test`). Web job now installs at repo root (`corepack enable` + `pnpm install --frozen-lockfile`, Node from `.nvmrc`) and runs `pnpm --filter ./apps/web run --if-present <lint|typecheck|test|build>`. Pipeline job uses `astral-sh/setup-uv@v7`, `uv sync --all-extras --dev`, then `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest`. `ci-ok` needs `[repo-checks, web, schema, pipeline]`.
- `.gitignore`: added `data/local/`, `pipeline/.venv/`, `apps/web/test-results/`, `apps/web/playwright-report/` (`data/cache/` was already there).

**Commands that pass (2026-11-15)**
- Root: `pnpm install --frozen-lockfile`, `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm --filter ./packages/schema test` (4 passed)
- Pipeline: `cd pipeline && uv sync && uv run pytest && uv run ruff check . && uv run ruff format --check .` (9 passed); `uv sync --all-extras --dev`; `uv run ev version` → `0.0.1`
- pip fallback: `pip install -e ".[dev]"` in a fresh venv, then `pytest` (9 passed) and `ev version`

**Defaults chosen (unattended run)**
- pnpm via corepack (already in the old CI) instead of `pnpm/action-setup`, so no new action version had to be guessed. `astral-sh/setup-uv@v7` is new to the file; v7 is its latest major tag (checked with `git ls-remote` on the public repo).
- Kept the `--if-present` flag before the script name (`pnpm --filter ./apps/web run --if-present lint`); after the name pnpm would pass it to the script. Tested in a scratch workspace.
- Licence field `AGPL-3.0-only` (DECISIONS 002 says "AGPL-3.0" with no "or later").
- ESLint pinned to 9 (not 10) for compatibility with eslint-config-next and typescript-eslint 8.
- `pipeline/ev_pipeline/schema_models.py` showed up mid-run from the schema generator (datamodel-codegen) with E501 errors. I excluded it from ruff in `pyproject.toml` rather than editing generated code.
- `pnpm-workspace.yaml` allows the esbuild postinstall (pnpm 10 blocks it by default; vitest in packages/schema needs it).

**For the coordinator / other lanes**
- Root `AGENTS.md` says source adapters go in `pipeline/sources/<name>/`; per this brief they go in `pipeline/ev_pipeline/sources/<name>/` with fixtures in `pipeline/tests/fixtures/<name>/`. `pipeline/AGENTS.md` says it overrides the root, but the root file (coordinator lane) should be updated to match.
- `pnpm format:check` currently flags 6 files in `packages/schema` (coordinator lane). I left them alone. Root prettier is not run in CI.
- Web builder: run `pnpm install` at the repo ROOT after adding `apps/web` deps so `pnpm-lock.yaml` covers it; CI uses `--frozen-lockfile`. `apps/web/eslint.config.mjs` can `import base from "../../eslint.config.mjs"`, and tsconfig can extend `../../tsconfig.base.json`.
- Pipeline builders: add subcommands in `ev_pipeline/cli.py::build_parser`; when adding a dev tool, add it to both the dev extra and the dev group.

## Review

**Reviewer (fresh agent), 2026-11-15. Verdict: pass, with notes.**

Ran every CI command locally; all green: `pnpm install --frozen-lockfile`, `pnpm --filter @ev/schema test` (8), `uv sync --all-extras --dev`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest` (179 passed + 1 xfail including the reviewer tests), the three `python3 -I` validators (0 errors; 7 unused-platform/pack warnings from validate_taxonomy). Re-ran pytest on a copy of the repo **without** the git-ignored `data/raw`, `data/staging` and `data/local`: still green, so CI doesn't depend on local-only data. Auto-detect (`detect` job, `.github/workflows/ci.yml:23-27`) and `ci-ok` are kept.

Notes
1. `actions/checkout@v7` and `actions/setup-node@v7` (`ci.yml:22,32,...`) couldn't be checked from here (no GitHub API access). They came from the earlier CI. If those major tags don't exist, every job fails. Confirm on the first run.
2. CI doesn't run `pnpm format:check` (root) or `pnpm --filter @ev/schema typecheck`. The handoff says format:check flags 6 schema files. Either fix and add them, or note that they're deliberately out.
3. Concurrent work: during this review, another agent was editing `apps/web` (`src/app/staff/review/page.tsx` appeared at 00:24 UTC), and `pnpm --filter ./apps/web build` then failed on i18n key types. Out of scope here, but the web job won't be green until that lane finishes.
4. Root AGENTS.md still says `pipeline/sources/<name>/` (handoff note). Coordinator to update.
