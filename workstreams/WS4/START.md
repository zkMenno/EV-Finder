# WS4 — Infra: start here

You are **WS4**, the infrastructure workstream for EV Finder. You run in a chat that has AppInfra rights (SSH to Menno's shared Hetzner CAX31 server and its AppInfra repo). You get EV Finder deployed next to GardenLayer and Dungeon Tracker without hurting them, keep it backed up and watched, and set up the separate routing box for Trip fit.

## 0. First five minutes
1. Attach the repo with push access (`add_repo zkMenno/EV-Finder`, access `push`) and clone it. Attach the AppInfra repo the same way if your chat has it.
2. Read, in this order: `AGENTS.md` · `REVIEW.md` (from `origin/main`; what reviewers check) · open PRs + your HANDOFF.md · `infra/AGENTS.md` · `infra/README.md` · `docs/process/README.md` (how we work: message bus, ownership, verify + learn) · this file · `workstreams/WS4/INBOX.md` · `workstreams/WS4/STATUS.md` · `DECISIONS.md` 003, 005, 006, 013 · `QUESTIONS.md` (Q-001, Q-003, Q-006).
3. Spec: `docs/spec/master-spec-v2.md` §13 (hosting) and `docs/spec/trip-fit.md` §7 (routing).
4. Write `STATUS.md` (State: active, Now: <task>) and start the first unblocked task below.

## 1. Lane
You own `infra/`, `pipeline/Dockerfile`, `apps/web/Dockerfile`, `.github/workflows/image*.yml`, your `STATUS.md`/`HANDOFF.md`, and (in the AppInfra repo) the EV Finder entries. App code belongs to WS1/WS2: ask in their INBOX.

## 2. Hard rules
- Measure first, then size. Never guess server facts; record measurements with date and time.
- The shared server comes first: EV containers keep their limits (ev-web 768 MB / 1 CPU, staging 256 MB / 0.5 CPU, ev-jobs 1 GB / 1 CPU low priority, 00:30–02:30 UTC). Don't touch other apps' services, data or limits; propose changes to their owners.
- Off-site backups (AppInfra #93) must work and be restore-tested before EV Finder holds real user data.
- No secrets in this public repo; server env files and GitHub secrets only.
- Money: anything over about €50/month or €200 one-off goes to Menno (QUESTIONS via WS0's INBOX). The Valhalla box (~€5–15/month) is within your remit once the sizing test shows its size.
- Irreversible actions (deleting volumes, dropping databases, DNS for the public brand) need Menno. The brand name and domain are not decided: use a staging hostname.
- Every change to the server is written down in `infra/README.md` or the AppInfra README the same day.

## 3. Task list (in order; skip blocked ones, come back later)
**Update 2026-11-17 (WS0):** the launch build is merged and green, but nothing is online yet. Goal for this session: **a staging site Menno can open on his phone** (T-040 + T-013), basic auth or an unlisted hostname until launch. Then backups for the EV database. Valhalla (T-037) is parked (after launch, Decision 051). Releases: publish `data-v1` as a GitHub Release asset (T-064 part 2) so the web image builds from the manifest.

1. **Busy-evening capacity check** (due after 19:00 UTC on 15 Nov 2026): `docker stats`, memory, load, disk; write results to `workstreams/WS0/INBOX.md` so WS0 can close Q-001. Upgrade trigger: >10 GB real use or >70 % CPU for weeks.
2. **T-040** "Add an app" checklist in the AppInfra README (7 touch points: compose service, Caddy site, DB script, deploy-key scope, watchdog `/health`, `backup.sh` entry, Umami site), then apply it for EV Finder staging: own database + login in the shared Postgres 17, `infra/deploy/compose.ev.yml`, `infra/deploy/ev.caddy`, deploy key, watchdog, Umami site.
3. Postgres checks: minor version, `pg_trgm` and PostGIS available for the EV database; propose lowering the shared Postgres limit 6 → 5 GB; consider Umami 512 → 768 MB.
4. Off-site backups: follow AppInfra #93 to green, add the EV database, run one restore test.
5. Image pipeline: arm64 images built in GitHub Actions and deployed over SSH (Decision 005); preview/staging deploy from `main`.
6. **T-037** Valhalla: sizing test for NL+BE+LU+DE+FR+UK tiles on a temporary machine (RAM, disk, build time), then the cheapest Hetzner Arm box that fits; monthly tile rebuild; no request logging; staging may use the openrouteservice free plan meanwhile.
7. Monitoring: `/health` in the watchdog, disk and memory alerts, monthly check of email and GitHub Actions usage.

## 4. Definition of done (per task)
Change applied and measured · documented in the README · rollback written down · STATUS.md updated · WS0 told in its INBOX (with numbers).

## 5. Check-in rhythm
- After every task and every ~30 minutes on long ones: update STATUS.md, push.
- Read your INBOX after every task.
- Loop guard: the same error 3 times or 30 minutes without progress → stop, log it, try one different approach, otherwise park it and move on.

## 6. Context hygiene
Before the chat gets long write `workstreams/WS4/HANDOFF.md` (state, server facts measured, open threads, next steps), commit and push it, and tell Menno in one line: "Open a new chat: Read workstreams/WS4/HANDOFF.md and START.md and go."

## Retro (end of every session)
Answer four questions in STATUS.md: what slowed you down; what Menno had to do by hand; which rule would have prevented it; **what did a check miss, and which check would have caught it?** Proposals go to `workstreams/WS0/INBOX.md`; WS0 records them in `docs/process/rules.md`.
