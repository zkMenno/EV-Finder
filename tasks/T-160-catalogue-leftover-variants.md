# T-160 Elroq alias + hold off, ZKXZ years, Model S 75D, catalogue leftovers: MX-30, smart forfour 453, Model X gen1, EV6 63 kWh, then the rest
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: review (batch: catalogue T-160, https://claude.ai/code/session_01JuyZEVd9J7FfZJTPaQQmnc, 2026-11-19): gate #196, data PRs Elroq, ZKXZ + 75D, leftovers

## Goal
The biggest no-variant groups left after T-154 get cited seed variants, so their EU registrations land on real rows.

## Acceptance criteria
- [x] **Elroq, first and in ONE change** (T-153 ask 0): add `source_names: {openev: [Base]}` to `skoda-elroq-gen1-85` **and** remove the OpenEV Elroq "Base" source hold from T-154 (#183). Never one without the other: the hold removal alone builds a `skoda-elroq-gen1-base` row with the wrong 150 kW. After-check in the PR body: no `skoda-elroq-gen1-base` row in the build, and the validation row shows OpenEV 150 kW withheld vs Škoda's cited 210 kW on the Elroq 85.
- [x] **ZKXZ 2025–26 versions** (T-153 ask 1): e-208 / Corsa / e-2008 versions with the 100 kW motor now go to review because the 50 kWh rows end 2023: extend the rows' years or add the 2025–26 variant, cited.
- [x] **Tesla Model S facelift 75D** (T-153 ask 2, the one G-48 hit): seed says RWD, build says AWD; fix the seed from a Tesla document.
- [x] **Mazda MX-30** (EV, 35.5 kWh): seed variant(s) from Mazda documents.
- [x] **smart forfour EQ (453)**: seed variant from smart / Mercedes documents.
- [ ] **Tesla Model X gen1**: split by pack / year as Tesla documents allow (cited WLTP per version).
- [x] **Kia EV6 63 kWh** (facelift Standard Range): its own variant next to T-154's 84 kWh RWD / AWD.
- [ ] Then, biggest EU cars first, as time allows: Škoda Citigo e iV / SEAT Mii electric, Kia EV9, MG Marvel R, BYD Sealion 7. List what's left in Handoff notes.
- [ ] Maker documents only, cited per car, never a whole table (Decision 087). Check built drivetrain and WLTP against the seed (G-48).
- [ ] `sh data/seed/data_qa.sh` and `ev verify --base main` pass; matching regression run (0 unintended moves); queue numbers before / after (no-variant EU cars, % EU registrations on groups we have: 470,298 / 69.0 % after T-154).

## Inputs
WS0 INBOX 2026-11-19 09:15 UTC (batch: catalogue T-154, "Left on the list") and 10:54 UTC (batch: data T-153, WS3 asks 0–2); T-154 Handoff notes; Decision 057, 068, 087; workstreams/WS3/START.md.

## Out of scope
Matcher or rule changes (T-159, T-161, WS1). Cargo versions (Decision 084). T-156's items.

## Handoff notes
2026-11-19, batch: catalogue T-160. Staging recorded 2026-11-19 12:51–13:51 UTC; every number below is from that staging. Same-staging release builds (main vs branch) for the moves, `ev verify --base origin/main` for the PR numbers.

- **Elroq (one change, PR "Elroq"):** `source_names: {openev: [Base]}` on `skoda-elroq-gen1-85` and the OpenEV Elroq "Base" hold removed together. After-check, same-staging build: Elroq rows are 50 / 60 / 85 / RS only (no `skoda-elroq-gen1-base`); validation.csv `va-956c150a1c`: "power contradicts the cited maker power: withheld (150 vs 210 kW cited)" on the 85. The 85 gains 11 charging fields from OpenEV (AC 11 kW, DC 185 kW claim, 10–80 % 25.9 min), so 18 score lines move against today's main build (e.g. daily-driver not-enough-data -> shortlist); against release 3 they block nothing, so no approval.
- **ZKXZ (PR "ZKXZ + 75D"):** e-208 / e-2008 / Corsa 50 kWh rows run on past 2023 (years end -> open), cited in comments: Stellantis Peugeot em-en 03 Apr 2025 ("Electric 136 hp/100 kW and 156 hp/115 kW"), Peugeot UK MY2024 E-2008 release (100 kW / 50 kWh back), Opel DE 28 Oct 2024 + Opel DE price list 6 Feb 2026. Effect: the "no variant fits the type_codes (ZKXZ)" review lines for e-208 (11 versions), Corsa (8), e-2008 (5) are gone; the rows gain used-price bands for 2024–26 (996 cells) and `on_sale_new` true. Gate #196 approves the 3 `year_end` clears (release 4, not built).
- **Model S facelift 75D (same PR):** drivetrain RWD -> AWD, name "75 / 75D" -> "75D". Tesla's EU type approval e4*2007/46*0667 (RDW TGK, CC0) files variant `75D` apart from `75R`. G-48 seed vs built: 1 -> 0 mismatches. **WS1 ask:** TGK variant code as split evidence (`75R` rear-motor 2016–18 versions still land on the 75D row; a `tesla-model-s-facelift-75` RWD row would tie without it).
- **New seed rows (PR "leftovers"):** `kia-ev6-facelift-63kwh-rwd` (Kia DE press kit Nov 2024: 63 kWh; Kia DE price list June 2026, dealer-hosted copy: 125 kW, RWD, 428 km), `mazda-mx-30-gen1-ev` (Mazda DE press kit: 35.5 kWh, 107 kW, WLTP 200 km; FWD per Mazda USA 2022 press kit), `smart-eq-forfour-453-eq` (Mercedes-Benz PL smart release 24 Feb 2017: 17.6 kWh, 60 kW, rear-wheel drive). New platform `mazda-mx-30` and pack `mazda-mx-30-35-5` (not-disclosed where no Mazda doc says). Kia's EU release of the same EV6 update says 62 kWh; Kia DE says 63: battery confidence medium.
- **Built rows (same-staging build):** EV6 63 RWD: rwd, WLTP 428, real 351 km; MX-30: fwd, 30 kWh net (source), WLTP 200, real 164; forfour: rwd, 16.7 net, WLTP 127, real 108. G-48: all match. Cited power / gross pack values are evidence only until Q-008 (maker-docs not releasable, build.py A-06 F3), so `power_kw` stays empty on these rows, as on the Elroq 85: pre-existing.
- **Queue (`ev variants propose`, same staging, EEA per-version counts fetched 2026-11-19):** no-variant EU cars 470,298 (200 groups) -> 406,363 (195 groups); have 4,601,448 (241) -> 4,664,882 (246). ZKXZ and Elroq leave the queue buckets unchanged (fingerprint groups). Share of EU cars in "have" groups, my count (have / all five buckets): 53.5 % -> 54.3 % (T-153's 71.4 % uses another denominator; not recomputed).
- **Review follow-ups (fresh review 2026-11-19, all PASS WITH NITS; not fixed here):** (1) Elroq 85 now ships OpenEV's DC peak 185 kW; Škoda's press kit reads 175 kW (85x) / "135 kW" in text: check against a Škoda document before launch. (2) MX-30: re-cite to Mazda DE's public price list (14 Feb 2023: 35,5 kWh, 107 kW, 200 km, Vorderradantrieb); the de.mazda-press.com PDF now shows a password page. (3) EV6 63: cite 125 kW / 428 km from Kia's own press kit (press.kia.com) instead of the dealer-hosted price list. (4) 6 smart EQ forfour TGK versions are new review lines ("no variant fits the battery"). WebFetch was blocked in this session after one unanswered approval, so (2) and (3) could not be read here.
- **Numbers re-measured after T-161 (#197) merged:** ev verify on gate + #200 / + #201 / + #202: 0 blocking; approved 580 / 583 / 583; review 12250 / 13298 / 13320; variants 399 / 399 / 402.
- **Not done, biggest first:** Tesla Model X gen1 (Tesla's type approval gives variant codes 60X / 75X / 90X / 100X and 2019 XA1 375 km / XA3 487–507 km WLTP but no pack kWh; a pack split needs the same TGK variant-code evidence as the 75R ask), Škoda Citigo e iV / SEAT Mii electric, Kia EV9, MG Marvel R, BYD Sealion 7.

## Review
