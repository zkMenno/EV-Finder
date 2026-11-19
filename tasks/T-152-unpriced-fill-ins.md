# T-152 Don't fill a small budget with far-too-expensive unpriced cars
Role: builder   Lane: apps/web (WS2)   Wave: launch
Status: review (batch T-152, https://claude.ai/code/session_01JuyZETaUYebGPuMx1hecJs, 2026-11-19) · PR #174

## Goal
At a low budget (e.g. €15k) the hero results show the cars that fit, not €100k+ cars that only appear because we have no used price for them yet.

## Acceptance criteria
- [x] Seen on release 3: at €15k, road-tripper and kerbside show 1 priced car, then "no price yet" fill-ins including Lucid, Lotus and e-tron GT RS. Reproduce first (screenshot or test).
- [x] Default (WS0, reversible): an unpriced car is not used as a fill-in when any price we hold for it (new list price or used price in another country) is more than 2× the budget. Other unpriced fill-ins stay, at most 3, under the existing "no price yet" label, after every priced car.
- [x] If that leaves fewer cards than today, the empty state says why and offers to raise the budget; never a blank list.
- [x] No price is invented or estimated for a car to make it fit.
- [x] Unit test for the rule; hero walk (e2e) still clean; 360 px check (G-44).

## Inputs
WS0 INBOX 2026-11-18 19:14 UTC (batch: data / release 3); T-132, T-146; launch-scope.md (hero).

## Out of scope
Pipeline price coverage. Changing the scoring.

## Handoff notes
- Reproduced on release 3, every EUR country: road-tripper and kerbside at €15k = 1 priced car (Dacia Spring) + 9 unpriced fill-ins (Lucid Air, Zeekr 001, Lucid Gravity, A6 e-tron, Eletre, e-tron GT, Model S, Macan Electric, Emeya).
- Rule `farOverBudget` (src/lib/shortlist.ts): cheapest price we hold, same currency only, evidence own → generation → **segment** (my reversible add: Lucid Air, e-tron GT, Model S, Emeya, Zeekr 001 have no price in any country, so the WS0 rule alone removed only the A6). Reading taken: "cheapest" price > 2×, not "any" price (the more cautious reading). Checked after score and gate, so "left out" counts only cars that would have shown (review should-fix).
- Cap 3 only with a budget; no budget unchanged (UK has no prices at all).
- UI note `hero-left-out`; "Raise your budget" only when cars were left out for price (the cap does not lift with budget).
- Left for data (WS1/WS3): Lucid Gravity, Lotus Eletre, Macan Electric have no price anywhere and sit in J-large/J-medium, so they stay as fill-ins until a list price lands. UK: no GBP prices, so the rule never fires there (Lucid Air still a £15k fill-in, list capped at 3).
- Nit left: "{n} more cars" with n = 1 (same plural pattern as other strings).

## Review
