# Questions for Menno

Agents add questions here when they're blocked. Menno answers inline under **Answer:**. Once answered, the coordinator moves the outcome into DECISIONS.md or the task file and marks the question closed.

Format: `Q-NNN` · task id (if any) · who asked · date.

---

## Open

### Q-001 · Server capacity · coordinator · 2026-11-15
Does the AppInfra server have room for EV Finder? Partly answered (see Decision 006): CAX31, 16 GB, shared with GardenLayer and Dungeon Tracker; fits on paper while Cahier stays off. Still needed from the "EV Finder capacity check" chat: real `docker stats`, free disk, existing job timers (to confirm the 00:30–02:30 UTC window), and off-site backup status.

**Answer:**

### Q-002 · Package managers · coordinator · 2026-11-15
Default proposal: **pnpm** for the web app and **uv** for the Python pipeline (both fast and widely used by agents). OK, or do you prefer npm / pip?

**Answer:**

### Q-003 · Pull requests on `main` · coordinator · 2026-11-15
Right now `main` only blocks force-pushes and deletion. Once code arrives, should `main` require a pull request with green CI (agents can't push straight to `main`)? Recommended: yes, from wave 1.

**Answer:**

### Q-004 · Push access · coordinator · 2026-11-15
The overnight session could clone the repo (it's public) but was refused push access, so nothing could be pushed to `proto/overnight-1` and no draft PR could be opened. **Default:** all work is committed locally on `proto/overnight-1` and handed over as a git bundle; you push it with `git fetch <bundle> proto/overnight-1:proto/overnight-1 && git push -u origin proto/overnight-1`. Next time, attach the repo with write access before starting the session.

**Answer:**

### Q-005 · Conflicting rules: "stop and ask" vs "never stop" · coordinator · 2026-11-15
AGENTS.md says a blocked builder stops and asks; the overnight brief says never stop. Repo files win, but nobody could answer overnight. **Default:** builders picked the safest option, logged it here and carried on, which is what "ask in QUESTIONS.md" amounts to when unattended. Should unattended runs get an explicit exception in AGENTS.md?

**Answer:**

### Q-006 · Where deploy files live · coordinator · 2026-11-15
The brief says `deploy/`; AGENTS.md and the README name `infra/` for deploy config. **Default:** repo wins, so the files are in `infra/deploy/` (`compose.ev.yml`, `ev.caddy`). Never applied. OK?

**Answer:**

### Q-007 · OpenEV Data coverage of older cars · T-004 · coordinator · 2026-11-15
OpenEV Data (CDLA-Permissive-2.0) mostly covers model years 2023+. Pre-2020 used favourites (Leaf ZE0, e-Golf, Zoe Q210/R240, i3 60 Ah, Ioniq 28 kWh, Soul EV) have few or no rows, so their generation pages show "no sourced specs yet". **Default:** leave them empty rather than fill from memory. Which open source should cover pre-2020 cars?

**Answer:**

## Closed

_none yet_
