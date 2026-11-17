# WS4 status

- **State:** waiting on Menno (server steps)
- **Now:** T-040 staging: runbook + measure script in PR #59; Menno runs it on the server
- **Next:** read measure.sh output → close Q-001 numbers, Postgres checks (pg_trgm/PostGIS), EV database + login, then off-site backups (AppInfra #93)
- **Blocked:** everything that needs the server. This session has no SSH and no AppInfra repo, and infra/AGENTS.md rule 1 says agents never apply. Menno runs the steps.
- **Last updated:** 2026-11-17 10:15 UTC by WS4

## Server facts (measured)
- 2026-11-17 ~10:00 UTC, from GitHub, not the server: GHCR `ev-finder-web` and `ev-finder-jobs` pull anonymously (public). Newest finished main web tag: `sha-3c6ce03`.
- Nothing measured on the server yet.

## Log
- 2026-11-17 10:15 UTC · Session 1. Read START, INBOX, infra docs. T-064 part 2 is already done: release `data-v1` has 98 assets. Wrote the staging runbook (infra/README.md "Staging first run"), basic-auth glob import in ev.caddy, read-only `infra/scripts/measure.sh` → PR #59. Caddy validate couldn't run locally (Docker Hub 429).

## Retro (session 1)
- **What slowed me down:** START.md says WS4 has SSH + AppInfra rights; this chat had neither, and infra/AGENTS.md forbids agent SSH anyway. Docker Hub rate limit blocked the Caddy check.
- **What Menno had to do by hand:** attach the repo; all server steps.
- **Rule that would have prevented it:** START.md should say which access the chat really has and match infra/AGENTS.md rule 1.
- **What did a check miss:** nothing failed. But the Caddy lane check depends on Docker Hub; a CI job running `caddy adapt --validate` on infra/deploy/ev.caddy would catch Caddy errors without local Docker.
