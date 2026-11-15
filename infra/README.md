# infra/: deploy config for the AppInfra server

> **Status: NOT APPLIED.** Agents wrote these files overnight (T-013). Nothing here is on the
> server yet. Menno reviews and applies them by hand, using the steps below.

EV Finder runs on the shared AppInfra server next to GardenLayer and Dungeon Tracker
(Decision 006): the server's Caddy in front, the shared Postgres behind a private network,
and images built in GitHub Actions (Decision 005).

## Files

| File | What it is |
|---|---|
| `deploy/compose.ev.yml` | Compose project `ev`: `ev-web` (768 MB / 1 CPU), `ev-web-staging` (256 MB / 0.5 CPU), `ev-jobs` (1 GB / 1 CPU, low priority, one-shot under the `jobs` profile). Read-only root filesystems, no-new-privileges, healthchecks, log rotation. Env from `/srv/ev/env/*.env`. No DB container, no published ports. |
| `deploy/ev.caddy` | Site blocks for `ev.example.com` and `staging.ev.example.com` (**placeholders**: the domain is still open). Reverse proxy, zstd/gzip, HSTS, CSP, nosniff, Referrer-Policy, Permissions-Policy, frame blocking, no `Server` header, long caching for `/_next/static/*` and `/data/catalogue-<n>.json`. |
| `../apps/web/Dockerfile` | Web image: pnpm workspace install → Next standalone build → `node:22-slim` runtime as user `node`. Bakes in only the latest catalogue release (`data/releases/<latest>/catalogue.json`) at `/app/data/releases` (`CATALOGUE_DIR`). HEALTHCHECK on `/health`. |
| `../pipeline/Dockerfile` | Jobs image: `python:3.12-slim` + uv, non-root user `ev`, entrypoint `ev`. Data is mounted at `/data` (`EV_DATA_DIR`). |
| `../.github/workflows/images.yml` | On push to `main` (or by hand): builds both images for linux/arm64 on a native Arm runner and pushes `sha-<short>` and `main` tags to GHCR. No deploy step. |

`GET /health` returns `{"status":"ok","release":<n or null>,"time":"…"}` with `no-store`. It is
what the AppInfra watchdog, the Docker healthcheck and Caddy's active health check poll.

## How to apply (later, by hand)

Assumes SSH access to the server and the usual AppInfra layout. Each 🟡 needs a check first.

1. **Answer the open questions:** Q-001 (capacity, job window), Q-006 (file location), and the
   domain. Replace `ev.example.com` / `staging.ev.example.com` in `deploy/ev.caddy`.
2. **Make the GHCR packages pullable.** After the first `Images` run on `main`, either make
   `ev-finder-web` and `ev-finder-jobs` public in the package settings, or `docker login ghcr.io`
   on the server with a read-only (`read:packages`) token.
3. **Create the folders on the server:**
   ```sh
   sudo mkdir -p /srv/ev/env /srv/ev/data
   sudo chown 10001:10001 /srv/ev/data      # uid of the `ev` user in the jobs image
   sudo chmod 700 /srv/ev/env
   ```
4. **Write the env files** (`/srv/ev/env/web.env`, `web-staging.env`, `jobs.env`, mode 600) from
   the names in `.env.example`. Real values only here, never in the repo.
5. **Check the networks** (🟡 names to confirm): the shared Caddy network is assumed to be
   `appinfra-proxy`, EV Finder's private DB network `ev-db`. Adjust the `networks:` block in
   `compose.ev.yml` to the real names (`docker network ls`). The database and login are created
   by AppInfra, not by this file. Nothing uses Postgres yet (Decision 008).
6. **Copy the files** to the server: `compose.ev.yml` → `/srv/ev/compose.ev.yml`,
   `ev.caddy` → `/srv/ev/ev.caddy`.
7. **Start the web containers**, pinning the image tag from the CI run:
   ```sh
   cd /srv/ev
   export EV_WEB_TAG=sha-abc1234 EV_WEB_STAGING_TAG=sha-abc1234
   docker compose -f compose.ev.yml pull ev-web ev-web-staging
   docker compose -f compose.ev.yml up -d ev-web ev-web-staging
   docker compose -f compose.ev.yml ps          # wait for "healthy"
   ```
8. **Hook up Caddy:** add `import /srv/ev/ev.caddy` to the main Caddyfile, then
   `caddy validate` and reload the way AppInfra normally does.
9. **Smoke test:** `curl -sI https://<domain>/health` returns 200 with the security headers;
   `/nl` loads; `/data/catalogue-<n>.json` has `Cache-Control: … immutable`.
10. **Add the watchdog entry** for `https://<domain>/health` in AppInfra.
11. **Nightly jobs** (🟡 window to confirm, Q-001). Until pg-boss scheduling exists, a host
    timer runs the one-shot container inside 00:30–02:30 UTC, for example a systemd timer with
    `OnCalendar=*-*-* 00:30:00 UTC` running:
    ```sh
    cd /srv/ev && EV_JOBS_TAG=sha-abc1234 timeout 2h \
      docker compose -f compose.ev.yml --profile jobs run --rm ev-jobs release
    ```
    The data folder must hold the pipeline inputs (`seed/`, `sources.yaml`, …); not wired up yet.

**Rollback:** set the previous `sha-…` tag and run step 7 again. Catalogue releases ride in the
web image for now, so a data rollback is an image rollback.

## Next steps (not done)

- An SSH deploy job in CI (Decision 005/006), with a deploy key held in GitHub secrets. Only after
  the manual steps above have worked once.
- Serve releases from a mounted `/srv/ev/data/releases` (`CATALOGUE_DIR`) so a data release no
  longer needs a new image.
- Pin base images by digest; add Dependabot `docker` entries for both Dockerfiles.
- Per-request CSP nonces so `script-src` can drop `'unsafe-inline'`.
