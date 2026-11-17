# WS2 handoff — 2026-11-15 13:20 UTC

Chat: https://claude.ai/code/session_01JuyZEUSsvVozgE36R16xAS

## State (2026-11-17 04:14 UTC)
All WS2 PRs are merged (#22, #23, #24, #25, #28, #29, #36, #37). Nothing open. Main green.

## Decisions made
- Decision 055 (hero above Explore at /{country}/{lang}/, presets/gates never drop a car for missing data, rule units). 053/054 were taken by WS0 for Dependabot.
- Hero refine filters = Explore filters (`seats`, `ac`, `ymin`/`ymax`, `make`/`xmake` added); Explore and hero stay in step through `src/lib/filter-bus.ts` (filters + profile answers).
- Parked features (T-091): `PARKED=1` or one flag each; parked e2e run with `E2E_PARKED=1` against a `PARKED=1` build.

## Open threads
- Owner's note built in #23 (T-067 lists it as launch). Asked WS0: /learn shows 5 articles, launch names 3 (WS3 index.yaml).
- When WS1's T-069 publishes `shortlist_score` (schema from #30), consider reading it instead of browser scoring; keep browser scoring for re-ranking by budget.
- Asked WS1: winter range field in PublishedVariant (cards say "In winter: not known yet"); list used_prices.json in the manifest.
- Asked WS3: `unit:` on dc-speed rules (daily-driver/runabout read as km per 20 min).
- UX: hero scene copied into apps/web/src/assets/illustrations (Docker image has no public/); the `evs-tex--map` texture isn't used (the app doesn't load bundle.css).

## Next steps
1. For new PRs: merge main in (no force-push; it's blocked here), resolve i18n JSON by key (theirs + our new keys), keep both sides of inboxes; start CI with workflow_dispatch.
2. When WS3's T-082 content lands: link /learn/batteries from hero cards (battery-health factor) and variant pages.
3. When a winter field lands: hero card + `rankHero` reasons + T-045 deltas.
4. Lessons: never rebase a pushed branch; always `date -u` for inbox timestamps; grep for conflict markers before every push.
