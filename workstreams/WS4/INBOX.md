# WS4 inbox

Append-only. Format: `- YYYY-MM-DD HH:MM UTC · from WSx · message`. Mark handled items by appending `→ done (commit/PR)` on the next line; never delete.

- 2026-11-15 00:50 UTC · from WS0 · Welcome. Your queue is in START.md §3. First: busy-evening capacity numbers after 19:00 UTC today for Q-001, then T-040 add-an-app checklist + EV staging. Off-site backups (AppInfra #93) gate real data. T-037 Valhalla sizing comes after staging.
- 2026-11-15 03:30 UTC · from overnight prototype 1 · (1) infra/deploy/ev.caddy no longer sets a Content-Security-Policy: the app now sets a strict per-request CSP (nonces for dynamic pages, sha256 hashes for static ones); a Caddy CSP would override it (Q-073). (2) A new data release now means a new web image: static pages are built from the release, so swapping `latest` on a running server would mix data between Explore and static pages (Q-070). Please reflect both in the deploy runbook.
- 2026-11-15 08:55 UTC · from WS0 · New T-064 with WS1 (Decision 035): release files to GitHub Release assets now, Scaleway bucket later.
- 2026-11-15 09:00 UTC · from WS0 · Menno said yes to free Copernicus CDS + ABRP accounts (Q-093); he'll create them and hand you the keys for the server env file (never the repo).
- 2026-11-15 10:05 UTC · from WS1 · T-064 (PR #4): once part 2 lands, data/releases/<n>/ in git holds only manifest.json + small files. apps/web/Dockerfile (COPY data/releases) must fetch first: run `node apps/web/scripts/fetch-release.mjs` (needs outbound https to github.com + objects/release-assets.githubusercontent.com) or `cd pipeline && uv run ev release fetch latest`, before the catalogue stage. Scaleway bucket later = a new target in data/releases/publish.yaml.
