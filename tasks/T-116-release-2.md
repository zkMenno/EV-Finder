# T-116 Rebuild and publish release 2; latest = 2
Role: builder   Lane: WS1 (+ WS4 if staging data is needed): pipeline/, data/releases/   Wave: launch fixes (A-35)
Status: todo

## Goal
The site runs on data that includes every launch data task.

## Acceptance criteria
- [ ] After T-110, T-111, T-112, T-113 and #44/#51 (T-123 release diff, T-127 `ev verify`) are merged: rebuild from the same inputs; raw public sources fetched on a session or temporary machine, never the shared server (Decision 006)
- [ ] Release 2 has `used_prices.json` (bands + estimates), `shortlist_scores.json`, winter range, T-068 seed, T-031 heat pump facts, the Model Y fix; the plausibility gate passes
- [ ] Release diff vs 1 (T-123) in the PR with every change approved; manifest committed → Data publish workflow → `latest` = 2
- [ ] A-35 S7 (T-064 part 2): release files no longer tracked in git
- [ ] Hero walk on release 2: winter range and a used band on most NL cards
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
audits/A-35 B1, S7; Decision 035, 044

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- WS1 (T-116 prep), 2026-11-17, source status (Decision 068, 080): `manual` is `active` with `use: cited-facts`, `decision: "068"` and a `cited_hosts` list of maker hosts; every manual fact must cite a listed host or name a blocked source. New blocked source `cited-third-party` holds 12 press/dealer/review facts in data/manual/heat-pump/r21-heat-pump.yaml. Dry run on the repo: 58 maker facts releasable (a06 11, r21 6, t110 12, t112 21, t118 8), held: autotijd 71, cited-third-party 12. The CC BY open-data bundle refuses `cited-facts` sources (a leak the new test caught: "facts cited, no licence" passed the licence check). `maker-docs` (seed `cited:`) stays blocked: 31 cites include third-party hosts (xr793.com, vaielettrico.it, projekt-renault.de, rinnovabili.it); WS3 must give those a `source_id:` before it flips.
- WS1, 2026-11-17, PR #80 review fixes: (1) a manual fact's `source:` (file or fact) may only name an `access: manual` source, or a source whose own `hosts` serve the fact's URL (`_source_claim_problems`, manual/facts.py); a meinauto page labelled `source: rdw` now fails `ev manual check` and never reaches the release or the CC BY bundle. A source with no `access` counts as not manual (fail closed). (2) `cited_hosts` entries may be a host/path prefix (`url_matches`, `*` = one path segment). louwman.nl narrowed to `www.louwman.nl/uploads/*/Peugeot/prijslijsten/`: the PDF's imprint is "Stellantis Nederland B.V." (the Peugeot NL importer), so it stays a maker document. Cision narrowed to `/Main/23604/` (Volvo Car Belux), Prezly to the one Toyota Belgium asset path. Counts unchanged: 58 ship, 83 held (autotijd 71, cited-third-party 12). Not done (optional): RDW TGK facts stay `manual`; relabelling them `rdw-tgk` drops them out of merge's CITED_SOURCES (cited_wins), so it's a merge-behaviour change, not a label: follow-up.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B1, S7 fixed. -->
