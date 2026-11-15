# A-04 Accessibility (axe-core), both themes

**Type:** accessibility · **Date:** 2026-11-15 · **Auditor:** web builder (Wave 5 polish), branch `proto/overnight-1` · **Data:** release 1 as published at 03:34 UTC (244 rows)

## Method

- Automated: `apps/web/e2e/a11y.spec.ts` runs [axe-core](https://github.com/dequelabs/axe-core) through `@axe-core/playwright` (devDependency) on a production build, tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`, `best-practice`.
- Pages: Explore table view (EN, Detailed), Explore cards view, Explore table in Nerd (NL), a generation page (`/nl/en/ev/renault/zoe/ph1`), a variant page (`…/ph1/r240`), Compare (Zoe R240 vs R135), a /learn guide (`/nl/en/learn/winter-range`), a ranking list (`/nl/en/top/fastest-dc`).
- Each page twice: light "Day trip" and dark "Night drive" (`prefers-color-scheme` emulated; the toggle itself is checked by its own test). 16 runs.
- The test **fails on critical or serious** violations. Moderate and minor ones are attached to the test report (`axe-summary.json`) and listed here. `AXE_REPORT=1 pnpm e2e e2e/a11y.spec.ts` prints them.
- Not covered by axe (manual or other tests): screen-reader wording, 200 % zoom, real phones. Keyboard Tab order and focus rings are checked in `e2e/polish.spec.ts` and `e2e/review.spec.ts`.

## Results

| Run | Before (first run tonight) | After |
|---|---|---|
| Explore table, light + dark | 1 serious: `label-content-name-mismatch` (9 sort buttons) | 0 |
| Explore Nerd table, light + dark | 2 serious: `label-content-name-mismatch` (9), `target-size` (100 nodes) | 0 |
| Explore cards, light + dark | 0 | 0 |
| Generation, light + dark | 1 moderate: `landmark-unique` | 0 |
| Variant, light + dark | 1 moderate: `landmark-unique` | 0 |
| Compare, light + dark | 1 moderate: `landmark-unique` | 0 |
| /learn guide, light + dark | 0 | 0 |
| Ranking list, light + dark | 1 moderate: `landmark-unique` | 0 |
| **Colour contrast (both themes)** | 0 | 0 |

"Before" was measured after the dark theme existed (axe needs both themes), so it reflects the light-theme switch to the design tokens too. No contrast violation showed up in either theme: the design tokens' AA claims (ink on paper 12.4:1 / 15:1, ink-3 ≥ 4.5:1) hold in the app.

## Fixes

1. **`label-content-name-mismatch` (serious, WCAG 2.5.3):** the Explore sort buttons had `aria-label="Sort by Years"` while showing "Years / Model years on sale in Europe". The aria-label is gone. "Sort by" is now sr-only text around the visible label, split from the translated `sort.by` template so word order works in every language.
2. **`target-size` (serious, WCAG 2.5.8):** in Nerd mode, number buttons, the name link and the "Sources" button were under 24 px tall and packed together. They now have `min-h-6` (24 px), and the name link has a little vertical padding.
3. **`landmark-unique` (moderate):** breadcrumbs used the same label as the main nav ("Main"). They now use `crumb.label` ("Breadcrumb" / "Kruimelpad").
4. **Found while checking (no axe rule):** absolutely positioned sr-only text inside the table scroll areas escaped them, so at 1280 px the whole page could scroll sideways to 2,817 px. The scroll containers are now `relative` (Explore, Compare, spec diff, rankings, about credits, learn tables). `e2e/polish.spec.ts` checks for it.

## Remaining moderate / minor

None reported by axe on these 16 runs.

## Not checked yet (follow-ups)

- Model page, /learn index, about page, staff page (staff is EN-only and off by default).
- The trip panel open (behind `TRIP_FIT=1`) and price-mode panels in loan mode.
- Popovers while open (axe runs with them closed).
- Manual: VoiceOver/NVDA pass, 200 % zoom with DE/NL strings, Windows high-contrast mode.
