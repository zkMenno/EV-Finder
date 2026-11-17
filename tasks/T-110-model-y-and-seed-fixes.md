# T-110 Model Y LR AWD and other A-35 seed figures from maker data
Role: builder   Lane: WS3: data/seed/, data/manual/   Wave: launch fixes (A-35)
Status: todo

## Goal
Correct the implausible Tesla Model Y Long Range AWD rows (gen1 and Juniper) and the A-35 S8 rows from maker data, so the #1 road-tripper pick is real.

## Acceptance criteria
- [ ] WLTP range, usable battery and consumption for `tesla-model-y-gen1` and `tesla-model-y-juniper` Long Range AWD from Tesla's own pages or homologation documents (archived URL + retrieval date + licence note); gen1 and Juniper no longer share copied values
- [ ] A-35 S8 checked against maker sheets: Ioniq 5 battery by year (58/72.6/77.4/84 kWh), Ioniq 5 N 84 kWh, 77.4 kWh rows get figures, MG4 Standard vs Long Range consumption; XPENG P7/P7+ present if the seed has them
- [ ] Each changed fact has source, date, confidence; pytest green
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
audits/A-35 B4, S8; PR #15 note on the Model Y

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B4, S8 fixed. -->
