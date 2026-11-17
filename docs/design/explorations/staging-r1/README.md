# Staging feedback round 1: hero questions (T-132) and catalogue layout (T-130)

UX, 2026-11-17. **Status: waiting for Menno's sign-off.** WS2 builds only after that (the sign-off line goes in tasks/T-132 and tasks/T-130).
Frames: `*-light.png` / `*-dark.png` at 360 px (phone, 2×) and 1280 px (desktop). Contact sheets: `SHEET-t132-phone.png`, `SHEET-t132-desktop.png`, `SHEET-t130.png`. Generator: `workstreams/UX/tools/staging_r1.py` (real tokens + bundle.css).
Numbers in the frames are **sample values for layout only**; car names come from `data/seed/top40.yaml`. Real values come from the release.

## T-132 Hero: one question at a time

What changed against staging, and why:

| Staging | New | Why |
|---|---|---|
| All 3 steps and 4 profile questions open at once | **One question on screen.** Tap an answer, the next one slides in (≈250 ms; reduced motion: instant) | Menno: "fewer questions on screen" |
| "Step 1" headings only | **Progress road**: 4 stops (Country · Your driving · Budget · Shortlist) on a dashed road that fills sky-blue. Done = the tick-V, now = sunflower dot with a number, later = outlined number. Text label under each | Shows where you are; shape + text + colour (colour-blind safe) |
| Small grey chips in rows | **Answer tiles**: full-width, ≥ 64 px tall, bold label + one hint line, empty ring → tick-V when picked; picked = 3 px ink border + `paper-sea` fill. Country = 2-column tiles | Clearer chips, bigger targets |
| — | **Answer trail** above the question: pills of what you said ("Netherlands ✎", "Our main car ✎"); tap one to jump back. After step 2 the four answers collapse into the profile name ("Road-tripper ✎") | No answers lost when we hide the questions |
| Budget field + 5 toggles | Big € field, 6 quick picks in a 3×2 grid (incl. "No limit"), the ≈ monthly box under it, New / Used / Either segmented switch, one primary "Show my top 10" | One clear end to the questions |
| Refine filters open inside the hero | "More filters (optional)" link on the budget step; on results a **"Refine · n"** button (phone: bottom sheet like T-130's filter sheet; desktop: sidebar link) | Optional stays out of the way |
| Results as big cards | **Phone:** profile summary bar (name, country, budget, Edit) → "Your shortlist" (sunflower tint) with 5 compact rows: rank, name, years, price band, winter range, km in 20 min, one "Why:" line, shortlist button → "Also worth a look" 6–10 as one-line rows (name, price, winter range). **Desktop:** answers in a sticky sidebar (each editable, plus the profile's preset filters) and the top 10 as a table with aligned columns (price, winter range, km/20 min, why) | Scan in seconds: the same numbers sit in the same place on every row |
| Full car list under the hero | Gone. "Show all cars" box at the end of the results → catalogue page (T-130) | Feedback item 1 |

Copy changes for WS2 (en.json): split the trips answers into label + hint ("Never" / "We take the train, rent or borrow"); question becomes "How often do you drive 300 km or more in one go?"; lead "Three questions. Then a top 10 for the way you drive, with prices where you live."; button "Show my top 10". Hints for the charge answers as in the desktop frame. The "keep it 8 years" box moves to the refine sheet (its scores don't exist yet, so it shouldn't take a question slot).

Behaviour: every answer still writes the URL (shareable, back button = previous question). Desktop keeps the scene on the right while asking; results replace the hero area. Semantics: each question is a `fieldset` + radios; the trail is a list of buttons; the road is an `ol` with `aria-current="step"`.

## T-130 Catalogue page

- **Desktop:** filters in a 272 px sidebar (collapsible groups: used price, real winter range, body type, fast charging, build year, seats/battery/towing, brands with search and counts). Top: title, "214 models · 87 match", Simple/Detailed/Nerd and Cards/Table switches. Bar: active filters as removable pills + "Clear", **Sort: Most popular** (price, winter range, battery, charging speed, year in the menu). One line under the bar explains "Most popular" with a "How we rank" link (Decision 038 blend). 3-column card grid.
- **Card:** 16:9 photo with a "#n popular" tag and the **credit line under every photo** (Decision 081), name + years, used price band "used, in the Netherlands", three facts (winter km, summer km, km in 20 min), shortlist button.
- **Phone:** sticky bar with "Filters · n" (opens a bottom sheet with the same groups and a "Show 87 cars" button) and "Popular first ▾"; active pills scroll sideways; compact horizontal cards (photo left 116 px, facts under).
- Landing: no list; "Show all cars" box (see T-132 results) and T-131's Popular used EVs section.
