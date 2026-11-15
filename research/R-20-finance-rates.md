# R-20 Finance rates for the loan calculator (T-043)

Researcher: WS3 research agent · Retrieved: 2026-11-15 · Status: done (first pass, time-boxed)

## The answer (plain language)

No central bank publishes a "used-car loan" rate, so we use each country's official **consumer-credit APRC** (the all-in yearly cost of a loan, fees included) as the "typical rate". For **DE, FR and BE** the ECB publishes it monthly; the latest month is **September 2026**: DE **8.91 %**, FR **6.11 %**, BE **6.24 %** (euro area 8.46 %). The ECB has **no current figure for NL**: its Dutch consumer-credit series stop in 2010 or 2017. For NL we use a comparison-site average instead (geld.nl, July 2026: **7.29 %** for a €20,000 personal loan) and mark it 🟡. The legal cap in NL is 12 %. For the **UK**, the Bank of England's £10k personal-loan rate is **7.11 %** (October 2026). The FCA reports that used-car finance arranged at the dealer averaged about **13 %** (2023 data). No official source publishes a typical term or deposit, so the defaults are **48 months** (from the spec) and a **10 % deposit**. Both are 🟡 and the user can change them. All ECB and Bank of England numbers can be reused for free with attribution. The Bank of England's own terms page could not be opened, so its licence is 🔴 still to check.

Legend: 🟢 official / 🟡 secondary or reasoned / 🔴 unsure.

## 1. Typical rates per country

### ECB MFI interest rate statistics (MIR): DE, FR, BE

Series pattern: `MIR.M.{CC}.B.A2B.A.C.A.2250.EUR.N`. The ECB's title reads: "Bank interest rates on loans to households for consumption, APRC (new business)". It covers "Loans for consumption excluding revolving loans and overdrafts, convenience and extended credit card debt, Total initial rate fixation, New business". So this is instalment consumer credit with credit cards excluded: the closest official proxy for a car loan. 🟢

| Country | Series key | Latest (ref. month) | Status flag | Previous |
| --- | --- | --- | --- | --- |
| DE | MIR.M.DE.B.A2B.A.C.A.2250.EUR.N | 8.91 % (2026-09) | P (provisional) | 8.99 % (2026-08) |
| FR | MIR.M.FR.B.A2B.A.C.A.2250.EUR.N | 6.11 % (2026-09) | P (provisional) | 6.14 % (2026-08) |
| BE | MIR.M.BE.B.A2B.A.C.A.2250.EUR.N | 6.24 % (2026-09) | A (normal) | 6.55 % (2026-08) |
| Euro area (reference) | MIR.M.U2.B.A2B.A.C.A.2250.EUR.N | 8.46 % (2026-09) | P | 8.59 % (2026-08) |

All values 🟢, retrieved from the ECB Data API on 2026-11-15 ([DE](https://data-api.ecb.europa.eu/service/data/MIR/M.DE.B.A2B.A.C.A.2250.EUR.N?lastNObservations=2&format=csvdata), [FR](https://data-api.ecb.europa.eu/service/data/MIR/M.FR.B.A2B.A.C.A.2250.EUR.N?lastNObservations=2&format=csvdata), [BE](https://data-api.ecb.europa.eu/service/data/MIR/M.BE.B.A2B.A.C.A.2250.EUR.N?lastNObservations=2&format=csvdata), [U2](https://data-api.ecb.europa.eu/service/data/MIR/M.U2.B.A2B.A.C.A.2250.EUR.N?lastNObservations=2&format=csvdata)). Human-readable page: `https://data.ecb.europa.eu/data/datasets/MIR/<series key>`. That page was blocked for this agent, so I did not open it; the API returned the same series.

Notes:
- The national central banks (Bundesbank, Banque de France, NBB) compile these figures and the ECB publishes them. Taking them from the ECB API gives one feed for all three countries.
- **Alternative series** (fixed rate for 1 to 5 years, which fits a 48-month loan, but it is the "narrowly defined effective rate" *without* fees, so it is not an APR): `MIR.M.{CC}.B.A2B.I.R.A.2250.EUR.N`. Values for 2026-09: DE 7.44 % (P), FR 6.14 % (P), BE 5.54 %. 🟢 ([API query](https://data-api.ecb.europa.eu/service/data/MIR/M.DE.B.A2B..R.A.2250.EUR.N?lastNObservations=1&format=csvdata)). Recommendation: use the APRC, because it matches "APR" and includes fees.
- Values flagged P are provisional and can be revised. The pipeline should refresh monthly and keep the flag.

### NL: no current official rate

- ECB MIR for NL: the APRC series `MIR.M.NL.B.A2B.A.C.A.2250.EUR.N` ends at **2010-05** (8.56 %). The over-1-year series `MIR.M.NL.B.A2B.K.R.A.2250.EUR.N` ends at **2017-07** (5.77 %). The only current NL household series are mortgages and revolving credit. 🟢 for the gap ([API query](https://data-api.ecb.europa.eu/service/data/MIR/M.NL.B.A2B......?lastNObservations=1&format=csvdata)). Why it stopped is 🔴 unknown; it may be confidentiality or a reporting change.
- I found no DNB table with a current consumer-credit rate ([DNB statistics home](https://www.dnb.nl/statistieken/) lists no such series). 🔴 Not found, not proven absent. Worth one email to DNB statistics later.
- **Proxy used:** geld.nl's averages for July 2026: €5k 10.87 %, €10k 8.42 %, **€20k 7.29 %**, €50k 7.01 %. The loan term is not stated. 🟡 ([geld.nl, Jul 2026](https://www.geld.nl/lenen/nieuws/laagste-leenrentes-juli-2026)). €20k is about the price of a typical used EV, so the default is **7.29 %**. geld.nl also reports that the car is the most popular reason to borrow (41 % of its 2025 loans). 🟡 ([geld.nl Datamonitor 2025](https://www.geld.nl/lenen/nieuws/datamonitor-lenen-2025-trends-en-ontwikkelingen))
- **Legal cap:** "De maximale rente op kredieten is per 1 januari 2026 12%." 🟢 ([Rijksoverheid](https://www.rijksoverheid.nl/vraag-en-antwoord/bescherming-van-consumenten/wat-is-kredietvergoeding-en-wat-is-het-maximale-kredietvergoedingspercentage)). Use it as an upper bound in validation.
- Licence: geld.nl is a commercial site. We store one derived number with a link, never its table. 🟡 This is fine as a cited fact; check again if we ever show more than one number from it.

### UK: Bank of England + FCA

- **BoE `IUMHPTL`**: "Monthly interest rate of UK monetary financial institutions (excl. Central Bank) sterling personal loan, £10K to households (in percent) not seasonally adjusted". **7.11 % (Oct 2026)**, 6.98 % (Sep 2026). 🟢 ([BoE database, IUMHPTL](https://www.bankofengland.co.uk/boeapps/database/fromshowcolumns.asp?Travel=NIxAZxSUx&FromSeries=1&ToSeries=50&DAT=RNG&FD=1&FM=Sep&FY=2026&TD=15&TM=Nov&TY=2026&FNY=Y&CSVF=TT&html.x=66&html.y=26&SeriesCodes=IUMHPTL&UsingCodes=Y&Filter=N&title=IUMHPTL&VPD=Y)). My understanding is that this is a *quoted* (advertised) rate from the BoE's quoted-rates series, not an effective rate. 🟡 I did not open the series notes to confirm it.
- **BoE `IUMBX67`** (£5k personal loan): 11.20 % (Oct 2026). 🟢, same database.
- **FCA (dealer motor finance, 2023 lender sample):** used vehicles had a weighted average APR of **13 %**, and HP averaged 12 %. New vehicles averaged 5.9 %. Motor finance agreements "typically run 2-5 years". Average amount financed on a used car was about £15,000 (FLA data, 2024). Point-of-sale finance covered 19 % of used-car sales in 2024. 🟢 ([FCA CP25/27 technical annex 2](https://www.fca.org.uk/publication/consultation/cp25-27-technical-annex-2.pdf)). These figures are from 2023 and are not updated monthly, so the FCA figure is a second UK row, not the default.
- **FLA (industry):** used-car finance at the point of sale was £21.8bn in the 12 months to June 2026, on 1.39m cars. FLA publishes no APR, term or deposit figures. 🟢 ([FLA, Jun 2026](https://fla.org.uk/news/consumer-car-finance-new-business-volumes-grew-by-7-in-june-2026/))

### Term and deposit

- No central bank or industry body I checked publishes a typical term or deposit for used-car loans: Bankenfachverband via [autohaus.de](https://www.autohaus.de/nachrichten/autohandel/finanzierung-im-fokus-pkw-bleibt-spitzenreiter-bei-ratenkrediten-3604329), [ASF June 2026](https://asf-france.com/wp-content/uploads/2026/08/CitConso06m26.pdf), FLA and the FCA. 🔴 Not found.
- The FCA's "2-5 years" supports a **48-month** default, which is the same as the spec. 🟡
- Deposit default **10 %** 🟡: this is reasoned, not sourced. It sits low enough not to put people off and is common in HP. The user changes it with a slider. Revisit if a source turns up.
- Useful for lease mode in FR: in H1 2026 about half of used-car financing in France went through LOA (€1,393m of €2,756m; LOA +7.0 %, instalment credit tied to the car −12.4 %). 🟢 ([ASF CitConso 06/2026](https://asf-france.com/wp-content/uploads/2026/08/CitConso06m26.pdf))

## 2. Regulatory context (brief, not legal advice)

- **EU CCD2 (Directive (EU) 2023/2225):** member states had to transpose it by **20 Nov 2025**, and it **applies from 20 Nov 2026**. It repeals Directive 2008/48/EC. Credit advertising must be "fair, clear and not misleading" and must carry a prominent warning such as "Caution! Borrowing money costs money". 🟢 ([European Parliament OEIL summary](https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1764052)). The EUR-Lex summary linked in the spec was blocked for this agent, so I did not re-open it.
- **UK:** introducing customers to third-party finance providers, "including lease/hire agreements and hire purchase agreements", is credit broking and needs FCA permission (full or limited). 🟢 ([FCA primary credit brokers](https://www.fca.org.uk/firms/authorisation/consumer-credit-brokers/primary-credit-brokers)). Separately, s21 FSMA restricts who may communicate a financial promotion. Since 7 Feb 2024, an authorised firm needs the FCA's special permission (the "gateway") to approve an unauthorised firm's promotions. 🟢 ([FCA PS23/13](https://www.fca.org.uk/publication/policy/ps23-13.pdf)). Whether a plain labelled link to a UK lease site counts as broking or a promotion is 🔴 for the lawyer (R-03). Until then: **no UK finance or lease links**, calculator only, which matches the spec.

## 3. Used-EV lease providers and partner programmes

| Country | Provider | Used-EV lease? | Partner / affiliate programme | Conf. |
| --- | --- | --- | --- | --- |
| NL | Justlease | "nieuwe en gebruikte auto's" for private customers | Yes: Daisycon campaign 15283, NL, since 13 Aug 2020 ([Daisycon](https://daisycon.com/nl/campagnes/15283-justlease)) | 🟢 |
| NL | DirectLease Private | Private lease; used not mentioned on listing | Yes: Daisycon 19548, NL, since 15 Aug 2024 ([Daisycon](https://daisycon.com/nl/campagnes/19548-directlease-private-nl)) | 🟢 listing / 🔴 used |
| NL | Privateleaseovernemen | Marketplace for taking over private leases (in effect used) | Yes: Daisycon 18092 ([Daisycon](https://daisycon.com/en/campaigns/18092-privateleaseovernemen-nl)) | 🟢 |
| NL | Ayvens, Athlon | Private occasion lease (sources in spec §8) | Not checked (Ayvens page failed to load) | 🔴 |
| NL | Leasys | Not found | Not found | 🔴 |
| DE | LeasingMarkt.de | Yes: 2,014 used-EV offers, private filter, from €139/month (Dacia Spring, 36 months, 10,000 km/yr) ([page](https://www.leasingmarkt.de/e-auto/gebraucht)) | Affiliate on **TradeTracker** only, live since Aug 2018 ([Affilitizer](https://www.affilitizer.com/programs/leasingmarkt.de)). Its own [/partner](https://www.leasingmarkt.de/partner) page is a dealer pay-per-lead programme | 🟢 offers / 🟡 affiliate (secondary listing) |
| DE | Vehiculum, Ayvens DE | Not checked | Not found | 🔴 |
| FR | Vivacar | Used LOA/LLD (spec §8) | Not found (the Awin ID I tried, 58019, is VIP Cars, not Vivacar) | 🔴 |
| FR | Renault Renew / Mobilize, Leasys FR | Used LOA (spec §8) | Not checked | 🔴 |
| BE | Ayvens Re-lease | Used, inspected ex-lease cars, "Leasing vanaf 12 maanden"; private access and EVs not stated ([Ayvens BE](https://www.ayvens.com/nl-be/leasen/andere-diensten/re-lease/)) | None mentioned | 🟢 / 🔴 affiliate |
| BE | JustLease BE, BNP Fortis Private Lease, DirectLease BE | Few used offers (10, 1 and 1) per [HelloSafe BE](https://hellosafe.be/?p=96856) | Not checked for BE | 🟡 |
| UK | Leasing.com | re.leasing.com: used leasing with loveelectric, launched Oct 2024; **business-only** at launch ([Broker News](https://brokernews.co.uk/leasing-com-launches-used-car-leasing-on-its-site-with-loveelectric/)) | Yes: Awin 129397, pays per validated enquiry ([Awin](https://ui.awin.com/merchant-profile/129397)); also Impact and Sale Gains per [affi.io](https://affi.io/m/leasing-com). **Blocked for us by the UK rule** | 🟢 |

Data rule reminder: affiliate commission rates and credentials never go in the public repo (Decision 004), so this table only says whether a programme exists. Payout amounts can be read on the linked listings when needed and go to private config.

## 4. Licences and terms of data sources

- **ECB / ESCB statistics (covers the Bundesbank, BdF and NBB figures in MIR):** free reuse, "irrespective of any subsequent commercial or non-commercial use". We must cite the source (e.g. "Source: ECB statistics"), must not change the statistics or metadata, and get no guarantee of continuity. 🟢 ([ECB usage policy](https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html), [Bundesbank, same terms](https://www.bundesbank.de/en/homepage/user-information/terms-of-use-regarding-the-reuse-of-escb-statistics-621188))
- **Bank of England database:** the terms page (bankofengland.co.uk/legal) was blocked for this agent, and the [database help page](https://www.bankofengland.co.uk/boeapps/database/help.asp) only points to it. 🔴 Check before launch. Until then, attribute "Source: Bank of England".
- **FCA publications, FLA, ASF:** we cite single facts with a link and copy no tables. 🟡
- **geld.nl:** commercial; we cite one derived number. 🟡

## 5. Gaps / follow-ups

1. NL official consumer-credit rate: ask DNB statistics, or find the CBS/DNB table. 🔴
2. BoE terms of use (blocked URL: https://www.bankofengland.co.uk/legal). 🔴
3. No sourced typical term or deposit anywhere. Defaults 48 months / 10 % are 🟡.
4. Affiliate status not found for Vivacar, Vehiculum, Ayvens, Athlon, Leasys, Renault Renew.
5. URLs blocked for this agent (not opened): data.ecb.europa.eu series page, EUR-Lex CCD2 summary, FCA primary-credit-brokers printable page, bankofengland.co.uk/legal.

## finance_profiles (ready to import)

```yaml
finance_profiles:
  - country: DE
    product: used_car_loan
    typical_apr: 8.91
    default_term_months: 48
    default_deposit_pct: 10
    source_id: ecb_mir
    source_url: https://data-api.ecb.europa.eu/service/data/MIR/M.DE.B.A2B.A.C.A.2250.EUR.N?lastNObservations=2&format=csvdata
    series_id: MIR.M.DE.B.A2B.A.C.A.2250.EUR.N
    reference_period: 2026-09   # provisional (P)
    retrieved_at: 2026-11-15
    confidence: green           # rate; term/deposit are yellow defaults
  - country: FR
    product: used_car_loan
    typical_apr: 6.11
    default_term_months: 48
    default_deposit_pct: 10
    source_id: ecb_mir
    source_url: https://data-api.ecb.europa.eu/service/data/MIR/M.FR.B.A2B.A.C.A.2250.EUR.N?lastNObservations=2&format=csvdata
    series_id: MIR.M.FR.B.A2B.A.C.A.2250.EUR.N
    reference_period: 2026-09   # provisional (P)
    retrieved_at: 2026-11-15
    confidence: green
  - country: BE
    product: used_car_loan
    typical_apr: 6.24
    default_term_months: 48
    default_deposit_pct: 10
    source_id: ecb_mir
    source_url: https://data-api.ecb.europa.eu/service/data/MIR/M.BE.B.A2B.A.C.A.2250.EUR.N?lastNObservations=2&format=csvdata
    series_id: MIR.M.BE.B.A2B.A.C.A.2250.EUR.N
    reference_period: 2026-09
    retrieved_at: 2026-11-15
    confidence: green
  - country: NL
    product: used_car_loan
    typical_apr: 7.29          # avg personal loan EUR 20k; legal cap 12 % (2026)
    default_term_months: 48
    default_deposit_pct: 10
    source_id: geld_nl_rates
    source_url: https://www.geld.nl/lenen/nieuws/laagste-leenrentes-juli-2026
    series_id: null            # ECB MIR NL consumer-credit APRC discontinued 2010-05
    reference_period: 2026-07
    retrieved_at: 2026-11-15
    confidence: yellow
  - country: UK
    product: used_car_loan
    typical_apr: 7.11          # GBP 10k personal loan (bank loan route)
    default_term_months: 48
    default_deposit_pct: 10
    source_id: boe_iadb
    source_url: https://www.bankofengland.co.uk/boeapps/database/fromshowcolumns.asp?Travel=NIxAZxSUx&FromSeries=1&ToSeries=50&DAT=RNG&FD=1&FM=Sep&FY=2026&TD=15&TM=Nov&TY=2026&FNY=Y&CSVF=TT&html.x=66&html.y=26&SeriesCodes=IUMHPTL&UsingCodes=Y&Filter=N&title=IUMHPTL&VPD=Y
    series_id: IUMHPTL
    reference_period: 2026-10
    retrieved_at: 2026-11-15
    confidence: green          # value; BoE licence still red
  - country: UK
    product: used_car_dealer_finance   # optional second row; 2023 data
    typical_apr: 13.0
    default_term_months: 48
    default_deposit_pct: 10
    source_id: fca_cp25_27
    source_url: https://www.fca.org.uk/publication/consultation/cp25-27-technical-annex-2.pdf
    series_id: null
    reference_period: 2023
    retrieved_at: 2026-11-15
    confidence: green          # value is official but dated
```

## Sources (all opened 2026-11-15 unless marked)

- ECB Data API, MIR series (DE, FR, BE, NL, U2): https://data-api.ecb.europa.eu/service/data/MIR/ (queries above) 🟢
- ECB statistics usage policy: https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html 🟢
- Bundesbank, ESCB reuse terms: https://www.bundesbank.de/en/homepage/user-information/terms-of-use-regarding-the-reuse-of-escb-statistics-621188 🟢
- Bank of England database, IUMHPTL / IUMBX67 (link above) 🟢; help page: https://www.bankofengland.co.uk/boeapps/database/help.asp
- FCA CP25/27 technical annex 2: https://www.fca.org.uk/publication/consultation/cp25-27-technical-annex-2.pdf 🟢
- FCA primary credit brokers: https://www.fca.org.uk/firms/authorisation/consumer-credit-brokers/primary-credit-brokers 🟢
- FCA PS23/13: https://www.fca.org.uk/publication/policy/ps23-13.pdf 🟢
- FLA, June 2026: https://fla.org.uk/news/consumer-car-finance-new-business-volumes-grew-by-7-in-june-2026/ 🟢
- European Parliament OEIL, CCD2 summary: https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1764052 🟢
- Rijksoverheid, max kredietvergoeding: https://www.rijksoverheid.nl/vraag-en-antwoord/bescherming-van-consumenten/wat-is-kredietvergoeding-en-wat-is-het-maximale-kredietvergoedingspercentage 🟢
- DNB statistics: https://www.dnb.nl/statistieken/ 🟢 (absence only)
- geld.nl July 2026 rates: https://www.geld.nl/lenen/nieuws/laagste-leenrentes-juli-2026 🟡; Datamonitor 2025: https://www.geld.nl/lenen/nieuws/datamonitor-lenen-2025-trends-en-ontwikkelingen 🟡
- ASF CitConso 06/2026: https://asf-france.com/wp-content/uploads/2026/08/CitConso06m26.pdf 🟢
- autohaus.de on Bankenfachverband study: https://www.autohaus.de/nachrichten/autohandel/finanzierung-im-fokus-pkw-bleibt-spitzenreiter-bei-ratenkrediten-3604329 🟡
- Daisycon: Justlease https://daisycon.com/nl/campagnes/15283-justlease · DirectLease https://daisycon.com/nl/campagnes/19548-directlease-private-nl · Privateleaseovernemen https://daisycon.com/en/campaigns/18092-privateleaseovernemen-nl 🟢
- LeasingMarkt used EV: https://www.leasingmarkt.de/e-auto/gebraucht · partner: https://www.leasingmarkt.de/partner 🟢; Affilitizer: https://www.affilitizer.com/programs/leasingmarkt.de 🟡
- Awin merchant 129397 (Leasing.com): https://ui.awin.com/merchant-profile/129397 🟢; affi.io: https://affi.io/m/leasing-com 🟡; Awin 58019 (VIP Cars, not Vivacar): https://ui.awin.com/merchant-profile/58019
- Broker News on re.leasing.com: https://brokernews.co.uk/leasing-com-launches-used-car-leasing-on-its-site-with-loveelectric/ 🟡
- Ayvens BE Re-lease: https://www.ayvens.com/nl-be/leasen/andere-diensten/re-lease/ 🟢
- HelloSafe BE private lease comparison: https://hellosafe.be/?p=96856 🟡
