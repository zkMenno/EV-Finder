# T-143 Official WLTP range next to our real range (real range leads)

Role: builder   Lane: WS2 (apps/web); UX for the visual pattern   Wave: launch
Status: review (batch chat https://claude.ai/code/session_01JuyZEWUcQc9VrZx4Ru21x6, 2026-11-18)

## Goal
Decision 085 (Menno, 2026-11-18): everywhere range shows, our real range comes first and most prominent, and the official WLTP range sits right next to it in the same section, labelled "Official (WLTP)".

## Acceptance criteria
- [x] Catalogue cards/rows (/cars), hero cards, car / generation / variant pages, compare: real range (and winter range where shown) leads; WLTP next to it in the same block, secondary style, label "Official (WLTP)"; tooltip explains the difference in one sentence.
- [x] Filters: range filter defaults to real range; WLTP selectable in the same filter group (toggle or second control); URL state keeps which one; sort by range defaults to real range, WLTP sort available.
- [x] Missing WLTP shows "not known" (never our estimate in its place); missing real range keeps today's behaviour.
- [x] EN strings (Decision 082: English only at launch); other language files get keys only if the i18n tests require them.
- [x] Contrast WCAG AA; 360 px and 1280 px, light + dark, plus one run with ~6 % wider letters (CI fonts); axe clean.
- [x] Unit tests + e2e for the filter toggle and one variant page; verify-web skill; evidence pack with screenshots in the PR; `Verified:` on every commit.
- [x] Fresh review (REVIEW.md from origin/main) passes.

## Inputs
Decision 085; docs/design/ (UX patterns); `wltp_range_km`, `real_range_km`, `real_range_winter_km` in the release.

## Out of scope
New data fields or pipeline changes.

## Handoff notes
2026-11-18, batch chat https://claude.ai/code/session_01JuyZEWUcQc9VrZx4Ru21x6
- **One shared piece:** `apps/web/src/components/OfficialRange.tsx`: the "Official (WLTP)" line (secondary style: text-xs, slate-700 label, value through `<Num>` with its provenance), "not known" when missing (never our estimate), optional ⓘ with a one-sentence tip (`range.wltp.tip`). Used by catalogue cards (full-width row under winter + summer range), the Explore table (second line in the real-range cell, no ⓘ there: table Tab-stop rule 12), hero cards (under "Real range") and `SpecValue` (variant page, generation spec diff, compare: the existing WLTP row right after real range, now labelled "Official (WLTP)").
- **Filters:** second slider in the range group (`wltpMin`, URL `wltp=`), under the real winter range slider; group title is now "Range". Pill "N+ km official (WLTP)". A car without WLTP never matches the WLTP filter.
- **Sort:** new key `wltp` (URL `sort=-wltp`), in the sort menu after winter range. The table's range header and `range` sort stay on real range.
- **Data:** `wltp_range_km` now ships with its provenance in the client catalogue (+8.9 KB gzip: 221.8 → 230.7 KB, budget 300). Release 2: 219 of 271 rows have WLTP; 20 rows have a real range but no WLTP ("not known").
- **Judgement calls (reversible):** tooltip text is ours (`range.wltp.tip`, one sentence, AC) instead of the glossary `wltp.short` (two sentences); the ⓘ still links to /learn/wltp. Spec-page label changed from "Official range (WLTP)" to "Official (WLTP)" (Decision 085 wording). DE/FR/ES/IT got draft strings only because `i18n.test.ts` requires every public key (not served at launch, Decision 082).
- **For UX (docs/design, not my lane):** CarCard README could note the WLTP line under the range facts.
- Feature-map flow `wltp-next-to-real-range` added (verify-web).

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
