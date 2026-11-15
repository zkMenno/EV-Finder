# R-32 How Menno picks EVs: patterns → shortlist rules

Date: 2026-11-15 · Author: WS0 (picks chat) · Inputs: `data/editorial/menno-picks.yaml` (tabs "EVs top tier", "OTHER EVs", "Used EVs") · Rules: `data/editorial/shortlist_rules.yaml` · Decision 038

## Bottom line

Menno's picks follow a small, consistent rule set. Encoded as 8 weighted factors, 2 gates and 4 bonuses/penalties, the rules put **24 of 30 rated cars in the same band he did (80%) and all 30 within one band**. On the older "Used EVs" tab, which was not used for tuning, they order **85% of car pairs** the same way he did inside each price band. 🟡 Tuned on one person's 30 rows: good as a starting profile, not proof it generalises.

## The patterns

1. **Fast charging first, measured in km/h, not kW.** 🟢 Every A/B-tier car adds 1,100+ km per hour (10–80%). The same models in their older versions (G6 2024, EV6 2021, IONIQ 5 2022 at 960–1,070 km/h) drop to "fallback". Four cars are struck out purely for "terrible DC charging" (Ampera-e, Zoe, Leaf, MG5).
2. **Two leagues: 800 V and 400 V.** 🟢 The tab is split by voltage. 800 V cars must clear a high bar; 400 V cars are judged against each other, so the best 400 V cars (L03 880 km/h, ID.7 Pro S 840, Zeekr 001) are green even though they charge slower than "fallback" 800 V cars. → rule bands per voltage class.
3. **Winter range ≥ ~380 km for the top, ~250 km hard floor.** 🟢 Shortlist: 380–465 km winter. The 54 kWh IONIQ 5 / EV6 (≈250 km winter) were the lowest used tier despite fast charging.
4. **Real space: boot + frunk.** 🟢 MG4 (363 L) never leaves "fallback"; IONIQ 6 (446 L total) only "watching". Estates are a plus (e-308 SW, Astra Sports Tourer marked yellow; the petrol shortlist is all estates/MPVs).
5. **One-pedal / strong regen is close to a must.** 🟢 IM6 has a 665 L boot and 1,230 km/h charging yet sits in C-tier: "Weak regen / No one-pedal driving". Every shortlisted car's note names its regen control.
6. **Efficient beats big battery.** 🟡 Picks cluster at 212–240 Wh/km; 270 Wh/km is accepted only with very fast charging.
7. **Newest version wins.** 🟢 Every model that appears twice ranks its latest battery/charging update 1–2 tiers higher.
8. **Bidirectional is a plus, V2H/V2G gets an exclamation mark.** 🟢 V2L on all 800 V greens; "V2H, AC @ 11kw!" on EX60, iX3, Megane 2026.
9. **Not too big.** 🟡 Zeekr 7X: "Quite chubby for B roads" → C-tier despite top charging. Rural roads matter. Needs width/mass data to calibrate.
10. **Price is its own axis.** 🟢 "Awesome, yet expensive" is a separate group, not a lower tier. Quality first, then budget.
11. **Used: supply and age count.** 🟢 Each used pick has an availability note (Plenty/Good/Ok/Rare); "2021+/2022+" are listed as pros, "2019+" as a con.
12. **Soft things he notes but doesn't score:** ADAS level, OTA, Android Automotive, looks ("Ugly"), parking sensors. Shown as notes; a later "tech" factor is possible.

## What the rules miss (6 of 30)

| Car | Menno | Rules | Likely reason |
|---|---|---|---|
| ID.7 Tourer Pro, Kia EV4 | consider | shortlist | His 400 V bar is a bit higher than the fitted 52 points; EV4 boot 435 L |
| Model Y 2022, ID.5 Pro | consider | fallback | Full-size class judged more leniently; Tesla network/software not in the data |
| Zeekr 7X (×2) | consider | shortlist / consider | The size penalty needs real width data |

On the Used tab the clearest miss is the Renault Megane 60 (his A1–A2, rules low): cheap, plentiful, Android Automotive and OTA. Value-for-money and software are the missing factors.

## Uncertain / to check

- 🔴 Thresholds are fitted to 30 rows; expect drift once 100+ cars are scored. Re-fit when Menno adds picks.
- 🟡 2024–2026 used prices rose after the oil shock: the Used tab's € bands are stale, its order is still useful.
- 🟡 Seed years disagree with his sheet for Elroq (he lists 2024, seed 2025) and Scenic (2023 vs 2024): WS3 to check against maker sources.
- 🟢 About 35 of his models are missing from the seed, mostly Chinese brands and 2025+ cars (XPENG G6/P7+/L03/L05, Zeekr 7X/7GT/001, Volvo EX60/EX50, Kia EV4, IONIQ 3, VW ID.5, Polestar 4, IM6, BYD Sealion 7, Renault 4, e-308 SW …). The seed also has no facelift split for EV6 / IONIQ 5 (2024 update), which his tiers treat as different cars: T-068.
