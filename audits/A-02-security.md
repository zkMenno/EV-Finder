# A-02 Security pass (T-017)

**Type:** security · **Date:** 2026-11-15 · **Auditor:** reviewer agent (fresh), branch `proto/overnight-1`

Scope: whole tree (excluding `node_modules`, `.venv`, `.next`, `.git`, caches), web app headers and runtime behaviour, dependencies, CI. Pipeline/Dockerfile changes in progress by another builder were not reviewed in depth.

## What was checked

| Check | How | Result |
|---|---|---|
| Secrets in the tree | 1,826 files (tracked + untracked; no git commands used, so `.gitignore` rules were read by hand). Regexes for AWS/GitHub/OpenAI/Slack/Google keys, JWTs, PEM private keys, `postgres://user:pass@`, and `password/secret/token/api_key = <8+ chars>`. | **Clean.** Hits: `.env.example` placeholders (`evfinder:evfinder@localhost`, `AUTH_SECRET=change-me`), and `POSTGRES_PASSWORD=openevdata` inside `data/raw/openev/` (third-party sample, and `data/raw/` is git-ignored). No `.env` file present. |
| Decision 004 (no sampling targets / partner ids) | Grep for marketplace domains and fetch/httpx calls. | **Clean.** Marketplace domains appear only as public search URL templates in `config/countries/*.yaml` → `listings.generated.json` (link-out only). The pipeline only calls `opendata.rdw.nl`, `*.eea.europa.eu`, `www.kba.de` (+ a GitHub URL); the Nyland URL comes from env and is scrubbed from logs. The only browser `fetch()` is Explore → `/data/catalogue-<n>.json` (same origin). No marketplace fetching anywhere. |
| `pnpm audit --prod` | | **No known vulnerabilities.** |
| `pnpm audit` (all) | | 16 advisories (3 critical, 1 high, 11 moderate, 1 low), **all dev-only**: `vitest` 2.1.9 and its `vite`/`esbuild`/`tinypool`/`@vitest/mocker`, plus `minimatch` via `typescript-eslint`. None reach the production bundle or image runtime. |
| Python deps | `uv pip list` (28 packages: httpx 0.28.1, duckdb 2.0.0, pyarrow 26.0.1, pydantic 2.14.3, pyyaml 6.0.3, openpyxl 3.1.5, jsonschema 4.26.0, …) + `uvx pip-audit` on the frozen list | **No known vulnerabilities.** |
| Headers (app, `next.config.ts`) | `curl -I` on `next start` | CSP `default-src 'self'` with `script-src 'self' 'unsafe-inline'`, `connect-src 'self'`, `frame-ancestors 'none'`, `base-uri 'self'`, `form-action 'self'`; `Referrer-Policy: strict-origin-when-cross-origin`; `X-Content-Type-Options: nosniff`; `poweredByHeader: false`. No HSTS / Permissions-Policy (left to Caddy). |
| Headers (Caddy, `infra/deploy/ev.caddy`) | Read | HSTS 1 year + includeSubDomains, same CSP + `object-src 'none'`, `X-Frame-Options: DENY`, Permissions-Policy, `-Server`, `-X-Powered-By`, deferred so Caddy's values win; staging `noindex`. Not applied yet (placeholder domain). |
| Browser makes no external calls | New e2e `e2e/review.spec.ts` → "T-017: every page talks only to our own origin": records every request on `/nl` (with a provenance popover open), a variant page, its generation and model pages, `/nl/compare?ids=…`, `/nl/learn/real-range`, `/nl/top`, `/nl/top/fastest-dc`, `/uk?lang=en`, waiting for network idle on each. | **Pass**: 0 foreign requests. (The existing smoke test covers `/nl` and a learn page.) |
| Staff page gated | `STAFF_PAGES` unset → `GET /staff/review` = 404 (e2e + curl); only the exact value `1` enables it (unit). `X-Robots-Tag: noindex, nofollow` on `/staff/*`. File parameter is whitelisted (`unmatched`/`conflicts`), no path traversal. | **Pass.** |
| `/health` | `curl` | `{"status":"ok","release":1,"time":"…"}`, `no-store`. No env, paths, versions or errors. **Pass.** |
| `/data/[file]` | Regex `^catalogue-(\d+|dev)\.json$` and must equal the live key; `..%2f` → 404. | **Pass.** |
| Outbound links | "See listings" on `/nl/ev/tesla/model-3/gen1`: `rel="nofollow noopener" target="_blank"`, from `LISTING_REL` in `src/lib/listings.ts:34`. | **Pass.** |
| CI | `.github/workflows/*.yml` | `permissions: contents: read` by default, `packages: write` only on the image job, no `pull_request_target`. Actions pinned by major tag, not SHA. |
| Container | `apps/web/Dockerfile` | Runs as `USER node`, has a HEALTHCHECK. |

## Findings by severity

No critical or high findings in production code or runtime dependencies.

| # | Severity | Finding | Fix |
|---|---|---|---|
| 1 | Medium | **The e2e smoke test (and with it the "no foreign request" guarantee from `apps/web/AGENTS.md` rule 3) does not run in CI.** `ci.yml` runs lint, typecheck, test and build only. | Add a CI job: `pnpm --filter @ev/web exec playwright install --with-deps chromium` + `pnpm --filter @ev/web e2e` after build. Proposed task: **CI e2e job**. |
| 2 | Medium | CSP allows `script-src 'unsafe-inline'` (needed for Next's inline RSC payload), which weakens it as an XSS backstop. No XSS path was found (React escapes everything; no `dangerouslySetInnerHTML` with user input), so this is defence in depth. | Move to per-request nonces (`proxy.ts` sets a nonce, Next reads it from the CSP header) when pages become static or auth lands. Keep `next.config.ts` and `ev.caddy` in step. |
| 3 | Medium | Dev-dependency advisories, 3 critical (vitest 2.1.9 → tinypool prototype pollution, Vitest UI file read). They only matter on a dev machine or CI runner running vitest/vite servers, but CI runs vitest. | Upgrade `vitest` to ≥ 4.1.12 (pulls patched vite/esbuild/tinypool/mocker); bump `typescript-eslint` for `minimatch` ≥ 11.0.1. |
| 4 | Low | Dependabot only watches GitHub Actions; `apps/web` (npm) and `pipeline` (pip/uv) now have manifests, as the file's own comment anticipates. | Add `npm` (`/`) and `pip`/`uv` (`/pipeline`) ecosystems, weekly. |
| 5 | Low | `STAFF_PAGES=1` exposes the review queue to anyone (no auth, Q-035). Default is off and `.env.example` says keep 0 in production. | Before enabling on any public host, put `/staff/*` behind Caddy `basic_auth` or the future auth. |
| 6 | Low | HSTS and Permissions-Policy exist only in Caddy. If the container is ever exposed directly, they're missing. | Optional: add Permissions-Policy to `next.config.ts` too (HSTS is fine to keep at the edge). |
| 7 | Low | Listing links send the origin as referrer (`strict-origin-when-cross-origin`), so marketplaces see our domain. Acceptable, but if we want zero leakage use `noreferrer`. | Product call: `rel="nofollow noopener noreferrer"` or leave as is. |
| 8 | Info | Actions are pinned by tag (`@v7`), not by commit SHA. | Pin third-party actions (docker/*, astral-sh/*) to SHAs; Dependabot keeps them updated. |
| 9 | Info | `data/review/*.csv` (152 KB) is not git-ignored and holds unmatched/conflicting rows from source datasets. Check licences allow it in a public repo (AGENTS.md data rule 4), or ignore it. | Coordinator to decide; add `data/review/` to `.gitignore` if unsure. |
| 10 | Info | e2e serves with `next start` although `output: "standalone"` (Next warns). Production uses `server.js`, so the smoke test doesn't exercise the exact prod entry point. | Optionally run e2e against `node .next/standalone/apps/web/server.js` (copy `static`/`public` first). |

**Verdict:** pass for the prototype. #1 and #3 should be fixed before the first public deploy.

## Fixes

**2026-11-15, builder (proto/overnight-1), web lane.**

| # | Fix |
|---|---|
| 1 | `.github/workflows/ci.yml` has an `e2e` job (switches on with `web`): installs Playwright Chromium with system deps, builds, runs `pnpm --filter @ev/web e2e` (smoke + review specs, including "every page talks only to our own origin"), uploads traces on failure. `ci-ok` now needs it. |
| 3 | `vitest` ^2.1.8 → **^5.1.0** (latest major) in `apps/web` and `packages/schema`; it pulls `vite` 8.3.8, patched `esbuild`/`tinypool`/`@vitest/mocker`. No test changes were needed (web 151 tests, schema 14 tests pass). |
| 4 | `.github/dependabot.yml`: `npm` (root workspace, weekly, grouped dev/prod minor+patch), `uv` (`/pipeline`, weekly, grouped), `docker` (`/apps/web`, `/pipeline`, weekly, grouped), next to the existing GitHub Actions entry. |

**`pnpm audit` after the fixes: 1 advisory (1 moderate), down from 16 (3 critical, 1 high, 11 moderate, 1 low).** `pnpm audit --prod`: no known vulnerabilities.

The one left: `minimatch` 10.2.6 (GHSA-g3hv-75wg-m249, patched ≥ 11.0.1) via `typescript-eslint` → `@typescript-eslint/typescript-estree`, dev only (lint). The latest `typescript-eslint` (8.72.2) still depends on `minimatch ^10.2.2`, so a bump can't fix it; a root `pnpm.overrides` entry (`"minimatch@>=7 <11.0.1": ">=11.0.1"`) would, but the root `package.json` is outside the web lane and a major-version override of a lint dependency needs a test run by the coordinator. Dependabot will pick up a fixed `typescript-eslint`.
