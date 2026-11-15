# R-01 Bidirectional charging (V2L/V2H/V2G), the EU 2027 ISO 15118-20 rule, and plug standards (CCS/NACS)

Researched 2026-11-15 by WS0 (coordinator). Time-boxed. Confidence: 🟢 verified in a primary or 2+ independent sources · 🟡 reasoned / one good source · 🔴 unsure, verify before publishing.

Spec section built on this: `docs/spec/bidirectional-and-connectors.md`. Decision 011.

## 1. The EU rule from 1 January 2027 — what it actually says

- 🟢 **Legal basis:** AFIR (Regulation (EU) 2023/1804) as amended by **Commission Delegated Regulation (EU) 2025/656** (in force 8 Jan 2026). Public AC/DC points installed or renovated since 8 Jan 2026 must implement ISO 15118-1…-5. **From 1 Jan 2027, every newly installed or renovated charging point — public and private (home and workplace wallboxes, Mode 3 AC and Mode 4 DC) — must implement EN ISO 15118-20:2022.** Sources: EUR-Lex OJ L 2025/656; comemso; KEBA; Vector; voldt.eu; Mennekes.
- 🟢 **Not affected:** chargers already installed (until "renovated"; a new cable is not a renovation); Mode 2 portable "granny" chargers.
- 🟢 **Public points with automatic authentication** (Plug & Charge, Autocharge) installed/renovated from 2027 need both ISO 15118-2 and -20 (Annex 2.1.2).
- 🟡 **Important correction to the common reading:** the rule mandates the *communication protocol* that makes bidirectional charging possible, **not** bidirectional power hardware. A 2027 wallbox "speaks V2G" but most will still not be able to send power back (no inverter, no grid-code certification). go-e and KEBA both state AFIR does not make V2X or Plug & Charge mandatory. So: "2027 wallboxes are V2G-ready on the software side", not "all new wallboxes are bidirectional".
- 🟢 **EPBD recast (Directive (EU) 2024/1275, Art. 12):** recharging points in new/renovated buildings must support smart charging and "where appropriate" bidirectional charging. Transposition deadline 29 May 2026. Policy direction, not a per-car rule.
- 🟡 **Practical gaps:** no agreed ISO 15118-20 conformity test route yet; fewer than 10 accredited labs; IEC 61851-23 ed. 3 (electrical side of bidirectional DC) not before end of 2027 (Codibly, Chargalytics). Expect patchy real-world support through 2027.
- 🟡 **Car side matters too.** The protocol only helps if the car speaks ISO 15118-20. Most cars on sale up to ~2025 speak DIN 70121 / ISO 15118-2 on DC, and many do no high-level communication on AC at all. Makers rarely publish "-20 support". VW's current DC bidirectional is built on ISO 15118-2 (VW press). Volvo EX30 and Kia EV2 are marketed as -20 ready (🔴 single sources).

## 2. Country status (why "can do V2G" depends on where you live)

- 🟢 **France:** first commercial V2G (Renault/Mobilize + The Mobility House, Oct 2024).
- 🟢 **Germany:** double grid fees on fed-back power abolished from 1 Jan 2026 (EnWG amendment, §118(6), passed 13 Nov 2025) + MiSpeL rules. First commercial offers: BMW + E.ON (Feb 2026), Mercedes + The Mobility House (Oct 2026), VW + Elli (Q4 2026). Smart meter required. VDA notes electricity-tax relief initially limited to PV owners (🟡).
- 🟢 **UK:** Octopus V2G tariff (legacy CHAdeMO cars, BYD Dolphin bundle), Nissan's AC V2G (first UK G99 approval for AC V2G), Renault/Mobilize 2026.
- 🟡 **Netherlands:** Hyundai/Kia V2G field test (Ioniq 9, EV9; up to 80 households, 2026); Renault/Mobilize planned 2026; Utrecht car-sharing (We Drive Solar) history.
- 🟢 **US:** V2H for backup is live via maker kits; V2G mostly utility pilots.

## 3. Two hardware routes (the key caveat for buyers)

| Route | Where the inverter sits | Home box cost | Examples |
|---|---|---|---|
| **AC bidirectional** | in the car (bidirectional on-board charger) | near a normal wallbox | Renault 5/4, Alpine A290 (11 kW, Mobilize PowerBox Verso); BMW Neue Klasse iX3 (11 kW, BMW Wallbox Professional €2,095); Nissan Leaf gen 3 (AC V2G via OTA, Nissan charger, UK first) |
| **DC bidirectional** | in the wallbox | €2,000–3,000+ (ChargeLine BiDi €2,990 list / €1,990 intro; Wallbox Quasar 2 ~£6,100; dcbel Ara US$9,999) | VW group MEB (ID.3/4/5/7/Buzz, Cupra, Škoda) with 77 kWh+ and software ≥3.5; Mercedes GLC/C-Class EQ, CLA/GLA/GLB (MMA); Ford Explorer/Capri (E3/DC Edison V2H) |
| **CHAdeMO DC (legacy)** | in the box | Quasar v1/v2, scarce | Nissan Leaf gen 1–2, e-NV200, Mitsubishi Outlander PHEV; Mercedes EQS V2G in Japan only |

## 4. Model notes (seed candidates; verify against maker pages before publishing)

- 🟢 **VW ID. (MEB):** V2H/V2G only with **net 77 kWh+ battery and ID. Software ≥3.5**; all with Software 6. Between 3.5 and 6 discharge is capped to a set energy/operating time (warranty). Only approved DC boxes (Hager/E3DC S10 E Compact; Sun2Wheel Two-Way-20; Elli ChargeLine BiDi from Q4 2026, DE first). Used-car caveat: check software version and battery size; 58/59 kWh cars are excluded on Software 3.5.
- 🟢 **Renault 5 / A290:** V2G with PowerBox Verso + Mobilize Power contract; FR live, DE/NL/UK 2026. Top two motor versions per electrive (🟡 check trims). Car's warranty unchanged per Renault.
- 🟢 **BMW iX3 (Neue Klasse, Gen6 eDrive):** V2G DE via E.ON tariff + Wallbox Professional; V2H DE/AT/NL late 2026. Other Neue Klasse models to follow. Older BMWs: smart charging only.
- 🟢 **Mercedes GLC EQ, C-Class EQ (MB.EA-M), CLA/GLA/GLB (MMA):** DC bidirectional, V2G package DE launched Oct 2026; FR/UK later.
- 🟢 **Tesla:** no V2H/V2G in Europe. US: Cybertruck Powershare; **Model 3/Y built in the US from 1 Oct 2026** do V2H with Powerwall 3 only. Used older 3/Y: no.
- 🟢 **US V2H:** Ford F-150 Lightning (Charge Station Pro + Home Integration System); GM Ultium (Silverado/Blazer/Equinox/Sierra EV 2024–26, Lyriq/Optiq/Vistiq/Escalade IQ/Hummer 2026, Bolt 2027) with GM Energy PowerShift + V2H Enablement Kit (some 2024s need an update); Kia EV9 (Wallbox Quasar 2); Volvo EX90 / Polestar 3 (dcbel; Polestar 3 400 V 2024–25 only).
- 🟡 **Hyundai/Kia E-GMP (Ioniq 5/6, EV6):** V2L 3.6 kW standard in EU; home V2H/V2G not offered in EU (pilots only). EV9/Ioniq 9: NL V2G pilot; US EV9 V2H live.
- 🟡 **V2L** (adapter/socket, ~2–3.6 kW) is common: E-GMP, BYD, MG, Polestar 2, Volvo EX30, Leaf gen 3. V2L ≠ V2H.
- 🔴 Kia EV2 "V2G standard on all trims"; BYD Dolphin V2G only in the Octopus bundle variant; Ford Explorer "bidirectional" in EU (V2H via E3/DC confirmed, V2G not).

## 5. US plugs: CCS1 vs NACS (SAE J3400)

- 🟢 NACS has won in North America: almost every maker has moved or is moving to a native J3400 port. Hyundai Ioniq 5 (2025) first non-Tesla native; Cadillac Optiq 2026; Rivian R1S/R1T 2026; Toyota bZ / Subaru Solterra 2026; Genesis GV70 2026; new Nissan Leaf (J1772 AC + NACS DC). **GM: all 2027 model-year EVs native NACS; most 2026 GM still CCS1 + adapter.**
- 🟢 Model year decides the port, so the filter must be per variant **and** model year. Used US market will be mixed for a decade.
- 🟢 Native-NACS cars need a NACS→CCS1 adapter at CCS stations and a J1772 adapter for many existing home Level 2 units.
- 🟢 Not every Supercharger site serves non-Teslas (older V2 sites). 🔴 Claim that ≤2021 Teslas aren't compatible with third-party J3400 stations — verify.
- 🟢 CHAdeMO still exists (~8.5k US DC connectors, falling). Europe: CCS2 + Type 2 everywhere (Tesla EU uses CCS2; pre-2019 Model S/X used a modified Type 2 for Superchargers). Australia/NZ: CCS2 + Type 2. Japan: CHAdeMO. China: GB/T (parked).
- 🔴 Bidirectional over NACS: some sources say J3400 lacks native bidirectional support; Ford's bidirectional route uses CCS on the Charge Station Pro. Verify before writing copy.

## 6. Sources (primary first)

- EUR-Lex, Delegated Regulation (EU) 2025/656 — https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202500656
- European Commission, EPBD & sustainable mobility — https://energy.ec.europa.eu/topics/energy-efficiency/energy-performance-buildings/energy-performance-buildings-directive/sustainable-mobility-and-buildings_en
- comemso, ISO 15118 explained — https://comemso.com/knowledge/iso-15118/
- KEBA, AFIR 2027 FAQ — https://www.keba.com/en/news/emobility/afir-compliant-with-keba-kecontact-p40-and-p40-pro
- go-e, AFIR explained — https://go-e.com/en/magazine/afir
- Codibly, ISO 15118-20 under AFIR — https://codibly.com/blog/white-papers/iso-15118-grid-functions-charger
- Chargalytics, Plug&Charge in Europe 2026 — https://www.chargalytics.com/deep-dives/plug-and-charge-europe-status-2026
- Volkswagen AT/DE bidirectional pages; VW compatible wallbox PDF — https://www.volkswagen.at/elektroauto/laden/bidirektionales-laden
- electrive: VW/Elli V2G (2026-06-23), Mercedes V2G (2026-10-13), Germany grid fees (2025-11-14)
- BMW Group press, iX3 V2G with E.ON (2026-02-09)
- Mobilize, V2G — https://www.mobilize.com/en/smart-charging/v2g/
- The Mobility House, V2G-capable cars list — https://mobilityhouse-energy.com/int_en/knowledge-center/article/which-cars-are-v2g-capable
- CleanTechnica / Notebookcheck, Tesla Model 3/Y Powershare (Oct 2026)
- GM newsroom, NACS by model (2026-08-13) — https://news.gm.com/home.detail.html/Pages/topic/us/en/2026/aug/0813-electric-vehicle-nacs-charging.html
- cali-energy.com, US V2H table (GM model years + hardware)
- bestchargers.co.uk, UK V2G compatibility (Leaf gen 3, CHAdeMO hardware)

## Corrections (15 Nov 2026, from research/R-25)
- 🟢 SAE J3400 (NACS) does cover bidirectional power (V2G / backup power); the 🔴 line in §5 is wrong.
- 🟢 Tesla Model 3/Y V2H (Powershare) applies to cars **ordered** from 1 Oct 2026 (US/PR), not to all cars.
- 🟢 Ford Explorer EV V2H is confirmed for DE/AT/CH.
- 🟡 Kia EV2 V2G is listed on Kia UK; BYD Dolphin V2G is a UK bundle only.
- 🔴 "Volvo EX30 is ISO 15118-20 ready" is not backed by Volvo's press release; treat as not disclosed.
- Car-side ISO 15118-20: only VW has an official statement (ISO 15118-2); all others not disclosed.
Details and sources: research/R-25-bidirectional-red-items.md.
