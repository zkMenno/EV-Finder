# WS2 handoff — 2026-11-17 22:06 UTC

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
