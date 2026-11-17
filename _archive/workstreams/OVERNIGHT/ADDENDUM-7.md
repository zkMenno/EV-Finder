# Overnight build 1 — addendum 7: decision number clash + one schema task (from WS0, 2026-11-15 01:35 UTC)

Small, do it at your next commit break, then carry on with your queue (addendum 6 first, then addendum 5, then the backlog).

1. **Decision number clash.** `main` now has **Decision 019: Variant finder** (accepted by Menno). Your schema-conventions decision is also numbered 019 on your branch. Renumber yours to **Decision 020** and update every reference (Q-054, commit notes in MORNING.md, task handoff notes). From now on, before adding a decision, `git fetch origin main` and take the next free number after both sides.
2. **Task numbers.** `main` now uses T-044–T-049 (Variant finder). Any task files you write start at **T-050**.
3. **Schema task T-044** (`tasks/T-044-schema-variant-clue.md` on main): add `VariantClue` and `LookalikeGroup` with fixtures and generated types, all optional so release 1 still validates. Spec: `docs/spec/variant-finder.md` §4. Slot it in after your current addendum 6 item.
