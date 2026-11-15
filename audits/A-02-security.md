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

## Status (overnight, addendum 5 item 6)

**2026-11-15, builder (proto/overnight-1), CI + pipeline-fetch lane.** Addendum 5 calls this audit "A-01"; in this repo security is **A-02** (A-01 is the performance budget), so the status lives here.

### Done

| Item | What changed |
|---|---|
| Actions least privilege | `ci.yml`: top-level `contents: read`, and every job states its own `permissions:` (`contents: read`; `ci-ok` gets `{}`). `images.yml` is split in two: `build` (pull requests and manual runs off main; `contents: read`, no registry login, no push) and `push` (main only; the one job with `packages: write`). Before, the single job held `packages: write` while building PR code. All checkouts use `persist-credentials: false`, so the token doesn't stay in `.git/config`. |
| Actions pinned to SHAs | All 8 actions pinned to a full commit SHA with a `# vX.Y.Z` comment, resolved with `git ls-remote` (each pin equals its major tag today): `actions/checkout` v7.0.1 `3d3c42e5…`, `actions/setup-node` v7.1.0 `949feb24…`, `actions/upload-artifact` v7.0.2 `cf430e03…`, `astral-sh/setup-uv` v7.6.0 `37802adc…`, `docker/setup-buildx-action` v3.12.0 `8d2750c6…`, `docker/login-action` v3.7.0 `c94ce9fb…`, `docker/metadata-action` v5.10.0 `c299e40c…`, `docker/build-push-action` v6.19.2 `10e90e36…`. Dependabot's `github-actions` entry bumps SHA and comment together. (Closes #8.) |
| No secrets for fork PRs | Both workflows use `pull_request`, never `pull_request_target`; the only secret (`GITHUB_TOKEN` for GHCR login) is used only in the main-only `push` job. |
| Dependency audit in CI | New `audit` job, `continue-on-error: true` and not part of `ci-ok` (warns, never blocks): `pnpm audit --prod`, and `uvx pip-audit --disable-pip` on `uv export --frozen --no-dev` (the hashed runtime set from `uv.lock`; nothing gets installed). Both report "No known vulnerabilities" locally tonight. |
| Lockfiles | `pnpm-lock.yaml` and `pipeline/uv.lock` are committed (in the git index, not ignored). CI installs with `pnpm install --frozen-lockfile` and now `uv sync --locked` (was plain `uv sync`, which would quietly re-lock); Dockerfiles already use `uv sync --frozen`. |
| Workflow check | YAML parses; `actionlint` 1.7.12 (via `uvx --from actionlint-py`) reports nothing. shellcheck wasn't installed, so `run:` scripts weren't shell-linted. |
| Safe fetch for pipeline | New `pipeline/ev_pipeline/net.py` → `safe_client(source_id, timeout=…, max_bytes=…, max_seconds=…)`. It allows only `https`, default port, no user info, no IP literals, hosts from the source's new `hosts:` list in `data/sources.yaml` (`*.x` = subdomains only). It checks every redirect hop (max 5). The SSRF guard resolves DNS once, refuses the host if any answer is non-public (private, loopback, link-local incl. 169.254.169.254, CGNAT, multicast, reserved, unspecified, IPv4-mapped), then connects to the checked IP itself (no DNS-rebinding gap; TLS still verifies the hostname). Per-operation timeout, a total time budget per response (default 600 s) and a size cap: 32 MB by default, counted on the wire and after gzip decoding (bomb-safe; other encodings are refused). Env proxies are ignored. Errors are `httpx.RequestError` subclasses (`FetchBlocked`, `ResponseTooLarge`), so the adapters' existing error handling covers them. |
| Adapters switched | One-line change in `fetch_cmd` of `rdw`, `eea`, `kba_fz10`, `ademe`, `nyland`, `dft_veh` (DfT: `max_bytes=256 MB`; it already streams to disk). `openev` / `kilowatt-openev` use `git clone` of github.com (not httpx); their `hosts: [github.com]` is there for the egress record. |
| Tests | `pipeline/tests/test_net.py`, 52 tests, no network: allowlist, wildcard, scheme/port/userinfo/IP-literal refusals, redirect re-checks and loop bound, size caps (announced, streamed, stream-to-disk, gzip bomb), time budget, address classes, backend connects to the checked IP, refuses mixed answers, the real transport refuses a loopback-resolving host, and every HTTP source has `hosts:` in the registry. |

### Remaining, code (not done tonight)

1. ~~Strict CSP with nonces (web lane, #2)~~ **done**, see "Web items" below. Caddy still needs a change (server item 2).
2. ~~Staff page guard (Q-035, web lane, #5)~~ **done**, see "Web items" below.
3. `minimatch` dev advisory via `typescript-eslint` (see Fixes): needs a coordinator decision on a root `pnpm.overrides` entry.
4. Optional: list `httpcore` as a direct dependency in `pipeline/pyproject.toml` (`net.py` imports it; today it comes in through `httpx`, locked in `uv.lock`). `net.py` swaps httpx's private `_pool` to plug in the pinned backend; a test fails if an httpx upgrade breaks that.

### Remaining, server (WS4 / AppInfra)

1. Caddy `basic_auth` (or IP allowlist) on `/staff/*` before `STAFF_PAGES=1` is set on any public host.
2. Apply `infra/deploy/ev.caddy` headers (HSTS, Permissions-Policy) once the real domain exists, but **remove its `Content-Security-Policy` line**: it is deferred, so it replaces the app's strict per-request policy with the old one that has `script-src 'unsafe-inline'` (Q-073). Re-check with `curl -I` on staging that the CSP has a nonce (Explore) or `sha256-` hashes (a model page) and no `'unsafe-inline'` in `script-src`.
3. Egress: the jobs container only needs HTTPS (443) to the hosts in `data/sources.yaml` `hosts:` (plus github.com for git). An outbound firewall or Docker network rule enforces it at a second layer. Also block the Hetzner metadata address `169.254.169.254` from containers.
4. Mount `data/sources.yaml` read-only into the jobs container (it is now also the fetch allowlist), or ship it in the image.
5. Run containers as non-root with read-only root filesystems and memory limits (Decision 006). The jobs image already runs as `ev`.
6. GitHub repo settings (Menno or WS4): branch protection on `main` requiring `ci-ok`; "Require approval for all outside collaborators" for fork PR workflows; Actions default token permission set to read-only.

### Web items (2026-11-15, web builder, proto/overnight-1)

| Item | What changed |
|---|---|
| Strict CSP, no `'unsafe-inline'` for scripts (#2) | Set per request in `apps/web/src/proxy.ts` (policy in `src/lib/csp.ts`; removed from `next.config.ts`). **Dynamic pages** (Explore, Compare, staff): fresh 16-byte nonce per request, passed in the request's CSP header so Next.js stamps its own scripts. **Static pages** (4,235 SSG pages since T-050): no request at render time, so no nonce; `scripts/csp-hashes.mjs` runs after `next build` (part of `pnpm build`), hashes each prerendered page's inline scripts (sha256) into `.next/server/csp-hashes.json` (+ the standalone copy), and the proxy sends that page's hashes. Static pages stay static. `script-src 'self'` + nonce or hashes; `object-src 'none'`, `connect-src 'self'`, `frame-ancestors 'none'`, `base-uri`/`form-action 'self'`. `style-src` keeps `'unsafe-inline'` (style attributes). Dev adds `'unsafe-eval'` only in `next dev`. If the manifest is missing in production, the proxy logs an error and falls back to the old policy so the site keeps working (Q-073). |
| Zero foreign requests | Unchanged (`connect-src 'self'`, `img-src 'self' data:`, `font-src 'self'`); e2e "every page talks only to our own origin" passes on the new URLs. |
| CSP tests | Unit (`src/lib/csp.test.ts`): nonce format/freshness, no `'unsafe-inline'`, hash vs nonce choice, hashing of a prerendered page, 404 hashes. e2e (`e2e/security.spec.ts`): a static learn page gets hashes and no nonce, a dynamic page a new nonce per request, neither has `'unsafe-inline'`, no CSP violations in the console, and client components still work under the policy. |
| Other headers (#6) | `next.config.ts` adds `X-Frame-Options: DENY`, `Cross-Origin-Opener-Policy: same-origin`, `Permissions-Policy` and HSTS (1 year, includeSubDomains), next to `nosniff` and `Referrer-Policy`; e2e checks them. |
| Staff guard (Q-035, #5) | `src/lib/staff-auth.ts` + proxy: with `STAFF_PAGES=1`, `/staff/*` needs HTTP Basic credentials equal to `STAFF_BASIC_AUTH` (`user:pass`, env only; compared in constant time via sha256 + `timingSafeEqual`). No `STAFF_BASIC_AUTH` = always 401 (fails closed). 401 and staff responses carry `X-Robots-Tag: noindex, nofollow` and `Cache-Control: no-store`; pages stay `noindex` and are never linked. `STAFF_PAGES` unset = 404 as before (e2e). Names added to `.env.example` with a dummy value. |
| Static build safety | Not a security item, but related: `next build` now fails if `data/releases/latest` exists but can't be read (no silent fixture pages), and the CSP step fails the build if a prerendered catalogue page is a 404. |

Remaining (web): none from this list. Server: Caddy CSP line (server item 2), optional Caddy `basic_auth` on top of the app guard (server item 1).
