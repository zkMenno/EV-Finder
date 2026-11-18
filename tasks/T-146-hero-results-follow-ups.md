# T-146 Hero results: phone Refine sheet, row photos, a feature-map flow for the results

Role: builder   Lane: WS2 (apps/web)   Wave: launch
Status: todo

## Goal
Follow-ups from T-132 (parts 1 #145 and 2 #161), decided by the coordinator 2026-11-18.

## Acceptance criteria
- [ ] **Refine on phones as a bottom sheet** (≤ 640 px): same controls as the desktop answers sidebar, opens from the results, keeps focus inside, closes with Esc / back / swipe-down, answers stay in the URL. Desktop sidebar unchanged.
- [ ] **Photo thumbnails on shortlist rows** from `generations[].image` (Decision 081; smallest width, lazy, fixed aspect ratio so rows don't jump, alt text "<make model generation>", credit reachable). Only when the release carries images (release 3+); rows without an image keep today's layout. Skip this item if no published release has images yet and say so in the PR.
- [ ] **Feature-map flow `hero-results`** for the results layout (rows, "also worth a look", answers sidebar edit, Show all cars box): a rubric change in its own gate PR, approved by the coordinator in advance (adds a check, drops none).
- [ ] 360/1280 px, light + dark, plus one run with ~6 % wider letters; axe clean; e2e for the sheet; evidence pack; fresh review; "Verified:" on every commit.

## Inputs
docs/design/explorations/staging-r1/README.md; T-132 task file and #161 review notes; Decision 081.

## Handoff notes

## Review
