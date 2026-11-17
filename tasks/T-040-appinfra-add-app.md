# T-040 AppInfra "add an app" checklist + EV staging
Role: WS4   Lane: infra   Wave: 6
Status: doing (WS4, 2026-11-17): staging runbook in PR #59; server steps wait on Menno

## Goal
Write the missing checklist and use it to put EV Finder staging on the shared server.

## Acceptance criteria
- [ ] Checklist in the AppInfra README covering the 7 touch points
- [ ] EV database + login in shared Postgres 17; compose service; Caddy site; deploy key; watchdog /health; backup.sh entry; Umami site
- [ ] Measured memory after deploy reported to WS0

## Inputs
Decision 006, infra/README.md, workstreams/WS4/START.md.

## Out of scope
Public domain (name not chosen).

## Handoff notes

## Review
