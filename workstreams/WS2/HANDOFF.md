# WS2 handoff — 2026-11-15 13:20 UTC

Chat: https://claude.ai/code/session_01JuyZEUSsvVozgE36R16xAS

## State (14:35 UTC)
All WS2 PRs green on their heads, none merged yet except #24 (T-045) and #25 (T-090). Merge order:
1. **#22 T-080 hero** (main)
2. then retarget to main and merge: **#23 T-067** (Suggested sort + owner's note), **#29 T-092** (hero used price per build year), **#36 T-093** (hero /learn links, travel-map texture, DE/FR/ES/IT hero strings)
3. **#37 T-094** (variant page used price by build year, stacked on #29)
4. **#28 T-091** (parked features behind flags; independent)
After each merge, merge main into the remaining branches (resolver: JSON dictionaries by key, inboxes keep both sides) and start CI with workflow_dispatch.

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
1. Keep PRs mergeable: merge main into each (no force-push; it's blocked here), resolve i18n JSON by key (`/tmp` resolver: theirs + our new keys).
2. When WS3's T-082 content lands: link /learn/batteries from hero cards (battery-health factor) and variant pages.
3. When a winter field lands: hero card + `rankHero` reasons + T-045 deltas.
4. Lessons: never rebase a pushed branch; always `date -u` for inbox timestamps; grep for conflict markers before every push.
