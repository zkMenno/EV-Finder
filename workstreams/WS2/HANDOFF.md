# WS2 handoff — 2026-11-18 00:20 UTC

Chat: https://claude.ai/code/session_01JuyZEUuCTBUyPNJ74C3iRD

## State
- **#117 T-130 part 1** (/cars catalogue, Most popular default, landing "Show all cars", old-link redirect): CI green on 03d8220; fresh review running. Merge when PASS (merge main in first if main moved). Then merge gate PR **#118** (apps/web AGENTS.md lines).
- **#111 T-137** English only: still waiting for WS0 (feature-map approval). #111 and #117 both edit e2e specs: whoever merges second merges main in.
- **#104** landing parallax (2nd WS2 chat): open.
- Asked WS1 for a release `popularity` field (WS1 INBOX 23:58); until then the web builds it from data/seed/top40.yaml + menno-picks (scripts/popularity.mjs, weights config/popularity.yaml).

## Next (in order)
1. T-130 part 2: the design's visual layer (PR #107 frames t130-*): sidebar filter groups, phone "Filters · n" bottom sheet + sticky bar, removable pills + Clear, count "N models · M match", one card per generation (used price band, winter km, summer km, km/20 min). Photos wait for T-135.
2. T-131 Popular used EVs (data/editorial/popular_used.yaml, WS3 PR #106).
3. T-135 photo cards (WS1 T-134 image fields).
4. T-132 hero redesign (designs in #107).

## Lessons
- A native `<select>` is as wide as its longest option: FR/ES overflowed 360 px. Test 360 px in all six languages.
- `**/AGENTS.md` is a gate file: split doc changes into their own PR.
- Feature-map triggers must resolve inside apps/web (outside paths fail verify-map.test).
- Next page files may only export page things: helpers go to src/lib.
- Run `pnpm vitest run` again after editing e2e/feature-map.yaml.

## Previous handoff (2026-11-17 22:06)

Chat: https://claude.ai/code/session_01JuyZEUgDrkg5ED4ZkeyEzg

## State
- **#111 T-137 English only:** fresh review PASS on e2e49ce, CI green (Images red = main's release-2 Docker error, WS1/WS4). Waiting for WS0 to approve the feature-map change, then merge (main moved since: merge main in and let CI run first).
- **#104** landing parallax (2nd WS2 chat): still open.
- Open with others: REVIEW D6 gate PR for Decision 082 (WS0); verify flow `tooltip` checks only the first of ~336 hidden tooltip nodes (scripts/verify.mjs:223, `.first()`), fails on main too: rubric fix, WS0.

## How T-137 works (for whoever adds a language back)
- Languages come only from `config/countries/<cc>.yaml`: `languages: []` + `default_language: en` everywhere; the old list sits in a comment above. List a language again → routes, sitemap, hreflang, picker and banner all return, no code change.
- e2e specs that need a second language skip on `ENGLISH_ONLY` (apps/web/e2e/langs.ts, read from the generated config) and switch back on by themselves.

## Next (in order)
1. T-130 catalogue page + "Show all cars": UX designs are in PR #107 (not merged yet). Popularity score must come from the release: ask WS1 for the field (blend weights in config, Decision 038).
2. T-131 Popular used EVs section (WS3 makes the list first).
3. T-135 photo cards (needs WS1's image fields, T-134).
4. T-132 hero redesign (designs in #107).

## Lessons
- Run `pnpm vitest run` again after editing e2e/feature-map.yaml: verify-map.test.ts pins required flow ids.
- Don't rename files during `pnpm build` (the standalone copy step fails).
- num-labels.test.ts can fail locally and pass in CI: check CI before calling something "red on main".
