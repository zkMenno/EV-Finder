# T-013 Health docker deploy
Role: builder   Lane: apps/web/Dockerfile, infra/   Wave: 3
Status: todo

## Goal
/health, arm64 Dockerfile, compose and Caddy files (not applied).

## Acceptance criteria
- [ ] /health returns 200 JSON
- [ ] Image builds for linux/arm64
- [ ] Limits as in Decision 006
- [ ] Tests cover it (with fixtures, no live network calls)

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
