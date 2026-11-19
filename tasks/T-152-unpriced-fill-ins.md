# T-152 Don't fill a small budget with far-too-expensive unpriced cars
Role: builder   Lane: apps/web (WS2)   Wave: launch
Status: todo

## Goal
At a low budget (e.g. €15k) the hero results show the cars that fit, not €100k+ cars that only appear because we have no used price for them yet.

## Acceptance criteria
- [ ] Seen on release 3: at €15k, road-tripper and kerbside show 1 priced car, then "no price yet" fill-ins including Lucid, Lotus and e-tron GT RS. Reproduce first (screenshot or test).
- [ ] Default (WS0, reversible): an unpriced car is not used as a fill-in when any price we hold for it (new list price or used price in another country) is more than 2× the budget. Other unpriced fill-ins stay, at most 3, under the existing "no price yet" label, after every priced car.
- [ ] If that leaves fewer cards than today, the empty state says why and offers to raise the budget; never a blank list.
- [ ] No price is invented or estimated for a car to make it fit.
- [ ] Unit test for the rule; hero walk (e2e) still clean; 360 px check (G-44).

## Inputs
WS0 INBOX 2026-11-18 19:14 UTC (batch: data / release 3); T-132, T-146; launch-scope.md (hero).

## Out of scope
Pipeline price coverage. Changing the scoring.

## Handoff notes

## Review
