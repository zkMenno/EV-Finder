# T-162 Re-cite MX-30 + EV6 63, Elroq 85 DC check, Model X gen1, Citigo e / Mii, EV9, Marvel R, Sealion 7
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: todo

## Goal
T-160's two weak citations move to maker-hosted documents, the Elroq 85 DC peak is checked before launch, and the biggest no-variant groups left get cited rows.

## Acceptance criteria
- [ ] **Re-cite to maker-hosted documents:** Mazda MX-30 (Mazda DE price list) and Kia EV6 63 kWh (press.kia.com kit) replace T-160's current citations; values change only if the maker document says otherwise (say which).
- [ ] **Elroq 85 DC peak:** check the shipped 185 kW against a Škoda document; fix or confirm with the citation.
- [ ] **Tesla Model X gen1:** rows per Tesla type-approval variant (60X / 75X / 90X / 100X …) as Tesla documents allow, cited WLTP per row. Records land on them once T-163 adds TGK variant codes as split evidence; if T-163 isn't merged, seed the rows and note the expected `tie` in Handoff notes.
- [ ] **Then, biggest EU cars first:** Škoda Citigo e iV / SEAT Mii electric, Kia EV9, MG Marvel R, BYD Sealion 7. List what's left in Handoff notes.
- [ ] Maker documents only, cited per car, never a whole table (Decision 087); built drivetrain and WLTP match the seed (G-48); `sh data/seed/data_qa.sh` (incl. the seed-pinned split tests once T-165 adds them, else run `pytest tests/test_t153_split.py tests/test_t159_split.py` by hand) and `ev verify --base-release-from origin/main` pass.
- [ ] Queue numbers before / after (no-variant EU cars: 406,363 in 195 groups after T-160).

## Inputs
WS0 INBOX 2026-11-19 16:05 UTC (batch: catalogue T-160, "Left" + WS3 asks); T-160 Handoff notes; Decision 057, 068, 087.

## Out of scope
Power citations for the 22 flag-less rows (T-164). Matcher changes (T-163). `tgk_split.yaml` (WS1).

## Handoff notes

## Review
