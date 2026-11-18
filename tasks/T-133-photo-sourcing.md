# T-133 Car photos: sourcing and licence log per maker
Role: builder   Lane: WS3: data/images/   Wave: launch (staging feedback 2026-11-17)
Status: review (WS3 2nd chat, 2026-11-17)

## Goal
One licensed photo per generation, with its credit (Decision 081).

## Acceptance criteria
- [x] `data/images/press-terms.yaml`: per maker, the press/media terms URL, date checked, a short quote of the relevant clause, verdict allowed / not allowed / unclear; unclear = not used
- [x] Per generation: the chosen image (maker press if allowed, else Wikimedia Commons CC BY / CC BY-SA, or CC0 / worldwide PD since Decision 083), source page URL, licence, author/credit line, retrieval date
- [x] Coverage report: % of launch generations with a photo, by source
- [x] No downloads committed to git (data rule 4): WS1 stores the files
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
Decision 081

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
**WS3 (2026-11-17):** `data/images/press-terms.yaml` (35 makes), `data/images/photos.yaml` (120 of 122 generations), method + coverage in `data/images/README.md`, tools in `data/images/tools/`.
- Press: no maker's public terms cover a non-media finder site. 13 not allowed (journalists/news media only, or written permission needed: Tesla, Audi, Nissan, Renault/Dacia, Stellantis brands, Polestar, smart, BYD), 22 unclear ("editorial use only" or terms not found). Decision 081: unclear = not used. Volvo is the closest ("editorial and strictly private use"); a permission email (Menno's name, draft) could unlock it.
- Commons CC BY / CC BY-SA at first (Decision 081); ported CC BY-SA 3.0 DE asked of WS1. Since Decision 083 (2026-11-18) also CC0 / worldwide PD with the template read from the file page: 4 photos moved (PR #132), which waits for WS1's validator to accept `CC0-1.0` / `public-domain`.
- Every pick checked by eye on contact sheets; 13 replaced (interiors, rear views, a door sill, wrong generation).
- Missing: volvo-ex50-gen1, xpeng-l05-gen1 (not launched).
- Could not HEAD-check file_url from this session (upload.wikimedia.org rate-limits our egress); all 120 URLs match Commons' MD5 path scheme. WS1's download step is the real check.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
