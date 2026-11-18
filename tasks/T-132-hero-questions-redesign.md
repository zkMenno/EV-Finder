# T-132 Cleaner hero questions and answer chips
Role: builder   Lane: UX (design) then WS2 (build): docs/design/ (UX), apps/web/ hero (WS2)   Wave: launch (staging feedback 2026-11-17)
Status: doing (WS2 6th chat, 2026-11-18, branch t-132-hero-questions)

## Goal
The hero questions, answer chips and results are calm and easy to scan.

## Acceptance criteria
- [ ] UX: designs for 360 and 1280 px: fewer questions on screen at once (one step visible, progress shown), clearer answer chips, a results list that scans in seconds; follows claude/brand-design-decisions.md
- [ ] WS2 builds it after UX signs off; same steps and data as launch scope §1; e2e and axe green
- [ ] Before/after screenshots in the PR
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
docs/spec/feedback-2026-11-17-staging.md item 3

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- 2026-11-18 (WS2, T-132 part 1 = questions PR): one question per screen. Step in the URL as `q`
  (country · role · trips · charge · area · budget; no `q` = results for a full profile, so old shared
  links still open the top 10). Every step change is a history entry: browser Back = previous question,
  answer kept. Logic in `src/lib/hero-state.ts` (`heroStep`, `nextStep`, `prevStep`, unit tests in
  `hero-state.test.ts`); drawing in `src/components/HeroSteps.tsx` (ProgressRoad, AnswerTrail,
  AnswerTiles); styles `evs-road / evs-opt / evs-trail / evs-qb / evs-seg / evs-cta` in globals.css.
- Keyboard: tap / click / Enter / Space answers and moves on; arrow keys only move the selection.
  Focus goes to the new question's heading. Slide-in 250 ms, none with reduced motion.
- Country tiles: two columns where the name fits next to its tick (≥ ~380 px phones and desktop), one
  column on 360 px phones (two columns split "Netherlands" mid-word). English country names per
  language (`hero.country.<slug>`), not the native names from config.
- "Keep it 8 years" moved into Refine (on the budget step "More filters (optional)", on results "Refine · n").
- Part 2 (results PR, next): phone result rows + desktop table and sidebar, Refine as a bottom sheet
  (reuse #126's sheet once merged), "Show all cars" box inside the results, thumbnails after T-135.
  Results today = the old cards under a new profile bar (name, country · new/used · budget, Edit).

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
