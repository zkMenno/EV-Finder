# T-013 Health docker deploy
Role: builder   Lane: apps/web/Dockerfile, infra/   Wave: 3
Status: review

## Goal
/health, arm64 Dockerfile, compose and Caddy files (not applied).

## Acceptance criteria
- [x] /health returns 200 JSON
- [ ] Image builds for linux/arm64
- [x] Limits as in Decision 006
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes
Builder, overnight 2026-11-15 (branch proto/overnight-1). Nothing applied anywhere.

**Built**
- `apps/web/src/app/health/route.ts`: GET → 200 `{status:"ok", release:<n|null>, time}`, `cache-control: no-store`; release is null while the dev fixture is in use. Reads `getCatalogue()` only. Test: `route.test.ts` next to it (tmp CATALOGUE_DIR fixtures; checks status, release, null fallback, no paths or env in the body). Web suite: 62/62 tests, tsc and eslint clean.
- `apps/web/next.config.ts`: added `output: "standalone"` (one line, as allowed by the brief).
- `apps/web/Dockerfile` + root `.dockerignore` (deny-all allowlist, shared by both images; context = repo root).
- `pipeline/Dockerfile`: python:3.12-slim + uv, editable install so `packages/schema/schemas` resolves, user `ev` (uid 10001), `ENTRYPOINT ["ev"]`, `EV_DATA_DIR=/data`.
- `infra/AGENTS.md`, `infra/README.md`, `infra/deploy/compose.ev.yml`, `infra/deploy/ev.caddy` (per Q-006 default).
- `.github/workflows/images.yml`: native `ubuntu-24.04-arm`, matrix web/jobs, GHCR `sha-<short>` + `main` tags, gha cache, no deploy step.

**Verified locally (x86_64 sandbox)**
- Both images build natively for **linux/amd64**. Web image: runs with read-only rootfs + tmpfs, cap_drop ALL, no-new-privileges, as uid 1000; `/health` → `{"release":1}`, `/nl` 200, Docker health `healthy`; 62 MB app dir, about 101 MB compressed. Jobs image: `ev version` works read-only as uid 10001.
- **linux/arm64 was NOT built here**: QEMU/binfmt needs a privileged container, which this environment refused. CI builds on a native Arm runner; the first `Images` run on main is the real arm64 check.
- Compose validates (`docker compose config`); Caddyfile validates (`caddy adapt --validate`). Caddy + web were tested end to end on a throwaway network: one CSP (not duplicated), HSTS, Permissions-Policy, XFO DENY, no Server/Via, gzip, immutable cache on `/data/catalogue-1.json`.

**Decided (safe defaults, to confirm)**
- Script CSP needs `'unsafe-inline'`: Next inlines RSC payload scripts (`self.__next_f.push`). Nonces would mean touching `src/proxy.ts`, which isn't my lane. Caddy's CSP = app CSP + `object-src 'none'`.
- Optional BuildKit secret `extra_ca` in both Dockerfiles, for builds behind a TLS-intercepting proxy (needed in this sandbox). It does nothing in CI and is never stored in a layer.
- Placeholder names: networks `appinfra-proxy` / `ev-db`, env files `/srv/ev/env/{web,web-staging,jobs}.env`, data `/srv/ev/data`, domains `ev.example.com` / `staging.ev.example.com`.
- Jobs: `profiles: [jobs]`, `cpu_shares: 256`, `oom_score_adj: 500`, run by a host timer (`timeout 2h`) at 00:30 UTC until pg-boss exists (window 🟡 Q-001).
- Action majors (`setup-buildx@v3`, `login@v3`, `metadata@v5`, `build-push@v6`) couldn't be checked online; Dependabot (github-actions) will bump them.
- Catalogue is baked into the web image (latest release only), so a data rollback is an image rollback. Mounting `/srv/ev/data/releases` is a listed next step.

## Review

**Reviewer (fresh agent), 2026-11-15. Verdict: changes needed (small); not ready to apply.**

Checked:
- `/health` returns 200 JSON with `cache-control: no-store` and leaks nothing; `src/app/health/route.test.ts` passes (3/3).
- Limits in `infra/deploy/compose.ev.yml` match Decision 006 exactly: ev-web 768m/1.0, ev-web-staging 256m/0.5, ev-jobs 1g/1.0 with `cpu_shares: 256` and `oom_score_adj: 500`, profile `jobs` (never started by `up`).
- Both images are non-root (web `USER node`; jobs uid 10001), and compose adds read-only rootfs, cap_drop ALL and no-new-privileges.
- Base images (node:22-slim, python:3.12-slim, busybox, uv) are multi-arch, so arm64 should work.
- Nothing is applied: `images.yml` has no deploy step, and compose/Caddy say NOT APPLIED with placeholder domains.
- No secrets: env files are referenced by path only, and the registry login uses `GITHUB_TOKEN`.

Findings
1. **Status still says `todo`** even though the work is done. Set it to `review`. The arm64 box stays unticked: no arm64 image has been built yet. The first `Images` run on main is the real test (handoff says so too).
2. **`images.yml` runs only on push to main** (`.github/workflows/images.yml:5-8`). A broken Dockerfile reaches main before anyone sees it. Add a `pull_request` trigger that builds with `push: false`, at least when Dockerfiles, lockfiles or `.dockerignore` change.
3. **The jobs image ships `pipeline/tests/`**, fixtures included (`pipeline/Dockerfile:34` `COPY pipeline/ ./`; `.dockerignore` allows all of `pipeline/`). That includes the real-car "nyland" release fixture (T-006 finding 1). Exclude `pipeline/tests` in `.dockerignore`.
4. `COPY --from=ghcr.io/astral-sh/uv:latest` (`pipeline/Dockerfile:11`) is unpinned, so builds aren't reproducible. Pin a version tag.
5. The second `uv sync` (`pipeline/Dockerfile:35-37`) doesn't mount the optional `extra_ca` secret, unlike the first. A local build behind the proxy failed at that step (`hatchling` fetch) while the first step passed. No effect in CI, but the two should match.
6. The jobs container mounts only `/srv/ev/data`, so seed, taxonomy, sources.yaml and field_sources.yaml have to be on the server already. That's undocumented in `infra/README.md`. Either bake them into the image or add a sync step.

## Fixes after review

**Builder (pipeline lane), 2026-11-15.**
1. Status set to `review`. The arm64 box stays unticked until the first `Images` run on a native Arm runner.
2. `images.yml` also runs on `pull_request` touching apps/web, pipeline, packages, any Dockerfile,
   .dockerignore, root package/lock files or the workflow. PR builds have no registry login,
   `push: false`, no provenance/SBOM, and read but never write the gha cache.
3. `.dockerignore` excludes `pipeline/tests` (fixtures stay out of the jobs image). Also added
   `!config/countries/` for the web build (coordinator request).
4. `pipeline/Dockerfile`: uv pinned via `ARG UV_VERSION=0.11.32` (`FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv`;
   matches local `uv --version`, tag checked: amd64 + arm64). The second `uv sync` now gets the same optional `extra_ca`
   secret mount as the first.
5. Verified locally (amd64): the jobs image builds with the proxy CA secret, `ev version` runs with a read-only rootfs,
   `/app/pipeline/tests` is absent, and uv in the image is 0.11.32.
- Not done: the coordinator asked for `COPY config/countries config/countries` in the `apps/web/Dockerfile`
  build stage. That file is in the apps/web lane, which this run was told not to touch, so the edit was not
  made. Until someone adds it, the web image build keeps using the committed `listings.generated.json`
  (the current Dockerfile comment says so).
- Finding 6 (jobs container needs seed/taxonomy/sources on the server) is infra and still open.
