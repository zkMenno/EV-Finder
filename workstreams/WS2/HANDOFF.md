# WS2 handoff — 2026-11-15 13:20 UTC

Chat: https://claude.ai/code/session_01JuyZEUSsvVozgE36R16xAS

## State
Open PRs (merge order): **#22 T-080 hero** → **#23 T-067 Suggested sort** and **#29 T-092 hero used prices** (both stacked on #22; retarget to main after) · **#25 T-090 /data page** · **#28 T-091 parked flags** (#25 and #28 both touch e2e/a11y.spec.ts: second one needs a small merge). #24 T-045 merged.

## Decisions made
- Decision 055 (hero above Explore at /{country}/{lang}/, presets/gates never drop a car for missing data, rule units). 053/054 were taken by WS0 for Dependabot.
- Hero refine filters = Explore filters (`seats`, `ac`, `ymin`/`ymax`, `make`/`xmake` added); Explore and hero stay in step through `src/lib/filter-bus.ts` (filters + profile answers).
- Parked features (T-091): `PARKED=1` or one flag each; parked e2e run with `E2E_PARKED=1` against a `PARKED=1` build.

## Open threads
- Asked WS0: is the model-page "Owner's note" (T-067) launch? /learn shows 5 articles, launch names 3 (WS3 index.yaml).
- Asked WS1: winter range field in PublishedVariant (cards say "In winter: not known yet"); list used_prices.json in the manifest.
- Asked WS3: `unit:` on dc-speed rules (daily-driver/runabout read as km per 20 min).
- UX: hero scene copied into apps/web/src/assets/illustrations (Docker image has no public/); the `evs-tex--map` texture isn't used (the app doesn't load bundle.css).

## Next steps
1. Keep PRs mergeable: merge main into each (no force-push; it's blocked here), resolve i18n JSON by key (`/tmp` resolver: theirs + our new keys).
2. When WS3's T-082 content lands: link /learn/batteries from hero cards (battery-health factor) and variant pages.
3. When a winter field lands: hero card + `rankHero` reasons + T-045 deltas.
4. Lessons: never rebase a pushed branch; always `date -u` for inbox timestamps; grep for conflict markers before every push.
