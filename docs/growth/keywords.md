# Keyword research: used-EV search demand per country

Status: proposed 2026-11-15 · Owner: WS5 growth · Feeds: seo-plan.md §2 (page types), WS3 content, WS2 routes · Legend: 🟢 verified · 🟡 reasoned · 🔴 unsure

**The answer.** We have no absolute search volumes. Google Trends refused our requests (HTTP 429), and no free public page gave numbers we could trust 🔴. We do have Google's live autocomplete for each country and language (🟢 observed 2026-11-15), and it shows the same four demand clusters everywhere:

1. **Model + used** ("tesla model 3 occasion", "vw id.3 gebraucht", "used mg4", "zoe occasion"). People add a year, a version ("long range", "62 kwh") or a price, which maps exactly to our **generation and used-market pages**.
2. **Budget lists** ("beste tweedehands elektrische auto onder 20000", "gebrauchtes Elektroauto bis 10000 euro", "voiture électrique occasion moins de 10000 euros", "best used ev under 20k"). These map to **ranking pages with price caps** (`/{country}/top/under-{price}`).
3. **Subsidies** ("subsidie tweedehands elektrische auto 2026", "prime voiture électrique occasion 2026", "e auto gebraucht förderung 2026"). Search interest follows the news cycle, and the rules change. These map to **one learn page per country**, kept up to date.
4. **Battery health and buying advice** ("soh accu meten", "elektroauto batterie zustand prüfen", "soh batterie voiture électrique", "ev battery health check cost", "worauf achten", "waar op letten", "to avoid"). These map to **learn articles** plus a "battery and known issues" block on generation pages.

**Build first:** (a) generation and used-market pages for the top 40 models in NL, DE, FR and UK; (b) three "best used EV under €10k/€15k/€20k" rankings per country (£ in the UK); (c) four learn articles per country: buying checklist, battery health/SoH, the country's subsidy, and "is a used EV worth it". The head terms ("tweedehands elektrische auto", "used electric cars") belong to marketplaces and we should not chase them 🟡.

## 1. Method in one paragraph

We sent seed terms to Google's public autocomplete endpoint (`suggestqueries.google.com`, `client=firefox`) with the matching `hl` (language) and `gl` (country) on 2026-11-15, and wrote down the suggestions in the order Google returned them. Autocomplete shows which queries are common and how people phrase them. It is **not** a volume count, and its order is only a weak popularity signal 🟡. To see who competes, we ran web searches for the main queries. Those searches run from a US index, so local rankings may differ 🟡. Volume context comes only from published articles, which report **on-platform** interest changes (for example AutoScout24 or La Centrale), not Google volumes. "Rel. demand" in the tables below is our ranking from autocomplete breadth and the seed's position. It is 🟡 everywhere and must be checked in Search Console (seo-plan.md §6, "keyword validation sample").

Page-type keys used below (from seo-plan.md §2): **GEN** generation page · **MOD** model page · **USED** used-market page · **TOP** ranking · **LEARN** learn article · **CMP** compare · **CHG** charging country page.

## 2. Netherlands (nl-NL)

| Cluster | Real phrasing seen in autocomplete 🟢 | Rel. demand 🟡 | Intent | Page type | Who ranks (observed) |
|---|---|---|---|---|---|
| Head: used EV | tweedehands elektrische auto (kopen, marktplaats, klein, automaat, met trekhaak); occasion elektrische auto (kopen, suv, klein, kia) | High | Transactional/browse | TOP (filtered hubs), not a head-term page | ANWB guides, AutoScout24, Marktplaats, Gaspedaal, ViaBOVAG |
| Model + occasion | tesla model 3 occasion (long range, 2021, prijs, 2025/2026); kia niro occasion (elektrisch, anwb); volkswagen id.3 occasion (advies, review, pro) | High in total, long tail | Research → buy | **GEN + USED** (year and battery size in titles) | Marketplaces, ANWB occasion pages |
| Best / budget | beste tweedehands elektrische auto (2026, suv, onder 20000, reddit, kleine, goedkope); tweedehands elektrische auto onder 10000 euro | Medium-high | Research | **TOP** `under-10000`, `under-20000`, `small`, `suv`, `tow-bar` | ANWB "koopgids tweedehands EV" and "top 10 goedkope elektrische occasions", AutoScout24 advice, Autoblog, Autorai, Beev |
| Subsidy | subsidie tweedehands elektrische auto (2026, 2027, zakelijk, hoeveel, wanneer, 6000 euro) | Medium, follows the news | Informational | **LEARN** `subsidie-tweedehands-ev` | Autoblog, Autorai, ViaBOVAG, TopGear NL, Solar Magazine |
| Battery health | soh accu (meten, betekenis, kosten, test, tester, auto); accu test elektrische auto; anwb accu test elektrische auto | Medium | Informational → action | **LEARN** `battery-health` + GEN battery block | ANWB (runs its own battery test), VRT (BE) |
| Buying advice | tweedehands elektrische auto waar op letten; ev occasion advies; actieradius / grote actieradius | Medium | Informational | **LEARN** `checklist`; TOP `longest-range-used` | ANWB, AutoScout24 |
| Lease vs buy | (occasion/tweedehands) … private lease / leasen / financial lease | High (appears on almost every seed) | Commercial | Out of scope at first; maybe a LEARN item later | Leasing firms, ANWB |
| Cross-border | elektrische auto kopen in duitsland; import (kosten) elektrische auto duitsland | Medium-low | Research | **USED** cross-country price block ("same car, cheaper in DE?") + LEARN `import-from-de` | Importers, BPM calculators |

Traps: "accu check" autocompletes to **Accu-Chek glucose meters** 🟢, so never target it. Use "accu test elektrische auto" or "soh accu". "tweedehands ev" drifts to e-bikes.

Context: AutoScout24 NL reported +48% EV requests in March 2026 vs February, and +80% year on year. Gaspedaal reported +47% EV searches in March. These are on-platform figures, not Google volumes 🟡 ([AutoScout24 NL](https://www.autoscout24.nl/bedrijf/occasion-dashboard/forse-stijging-48-meer-interesse-in-tweedehands-ev-s-door-hoge-brandstofprijzen/)). A used-EV trade-in subsidy was planned for Q4 2026 and still needed parliamentary approval, with the amount open 🟡 ([EVupdate](https://www.evupdate.nl/elektrisch-rijden/artikel/inruilregeling-fossiele-auto-vervroegd-subsidie-voor-tweedehands-ev-al-in-q4-2026)). WS3 must check the current status before publishing.

## 3. Germany (de-DE)

| Cluster | Real phrasing seen 🟢 | Rel. demand 🟡 | Intent | Page type | Who ranks (observed) |
|---|---|---|---|---|---|
| Head: used EV | elektroauto gebraucht (kaufen, von privat, in der nähe, günstig); gebrauchtes elektroauto (kaufen, leasen); e-auto gebraucht | High | Transactional | TOP hubs; don't chase head | mobile.de, AutoScout24, Kleinanzeigen, AutoBild |
| Budget | e-auto gebraucht unter 10.000 euro (top suggestion), unter 5.000; gebrauchtes elektroauto bis 10000 / 20000 / 25000 euro; elektroauto gebraucht kaufen bis 5000 euro | **High: in DE, price caps rank above the plain term** | Research → buy | **TOP** `unter-5000`, `unter-10000`, `unter-20000`, `unter-25000` | mobile.de magazine ("günstige gebrauchte Elektroautos"), AutoBild |
| Model + gebraucht | tesla model 3 gebraucht (preis, preisentwicklung, worauf achten, long range, test); vw id.3 gebraucht (sinnvoll, mit anhängerkupplung, preis, österreich) | High in total | Research → buy | **GEN + USED**; "preisentwicklung" fits the price-trend chart | Marketplaces, AutoBild, ADAC |
| Is it worth it / advice | elektroauto gebraucht kaufen sinnvoll / erfahrungen / worauf achten; gebrauchtes e auto (kaufen) worauf achten | Medium-high | Informational | **LEARN** `checkliste` and `lohnt-sich` | ADAC, AutoZeitung, EnBW, elektroauto-news, InsideEVs DE, GIGA, insurers (ERGO) |
| Battery health | elektroauto batterie zustand prüfen; soh elektroauto (auslesen, wert, test); adac batterietest (kosten, e auto); akku test elektroauto | Medium | Informational → action | **LEARN** `batterie-soh`; GEN battery block | ADAC (sells the test), electrive, regional news |
| Subsidy | gebrauchtes elektroauto förderung; e auto gebraucht förderung 2026 | Medium, follows the news | Informational | **LEARN** `foerderung` | AutoBild, Vision Mobility |
| Range / tow-bar | gebrauchtes elektroauto mit hoher reichweite / mit anhängerkupplung | Medium | Research | **TOP** `hohe-reichweite`, `anhaengerkupplung` (filter-driven) | Marketplaces |

ADAC is both a competitor and a source: it ranks for advice and sells the battery test. Cite it and link to it, don't fight it 🟡.

## 4. France (fr-FR)

| Cluster | Real phrasing seen 🟢 | Rel. demand 🟡 | Intent | Page type | Who ranks (observed) |
|---|---|---|---|---|---|
| Head | voiture électrique occasion (pas cher, le bon coin, sans apport, particulier, invendable); voiture électrique d'occasion (la plus fiable, avis, la centrale, la moins chère) | High | Transactional | TOP hubs | Leboncoin, La Centrale, Aramis, Capcar, Autohero, Beev |
| Budget | … moins de 5000 / 8000 / 10000 / 12000 / 15000 / 20000 / 25000 euros; 6000 euros; quelle voiture électrique occasion pour moins de 20000 euros | **High: the deepest price ladder of any country** | Research | **TOP** `moins-de-{5k…25k}` | Capcar, Caroom, Beev, Vivacar |
| Best / which one | meilleure voiture électrique occasion (2026); quelle voiture électrique occasion choisir / acheter en 2026; comparatif; top; la plus fiable | Medium-high | Research | **TOP** + **CMP**; "la plus fiable" needs the known-issues data | Caroom, Capcar, Beev, Autohero, Automobile Propre |
| Model + occasion | zoe occasion (achat intégral, sans location de batterie, avec batterie incluse, 5000 euros, avis); tesla model 3 occasion (15000/20000/25000 euros, certifié, grande autonomie) | High | Research → buy | **GEN + USED**. **Zoe battery rental is a France-specific field we must model** | Leboncoin, Renault, La Centrale |
| Subsidy | prime voiture électrique occasion (2026, simulation, montant, septembre 2026, edf); bonus voiture électrique occasion 2026; aide (achat) voiture électrique occasion 2026; leasing social (2026, conditions, quelle voiture, 2027) | **High and spiky (new CEE prime since 1 Sep 2026)** | Informational | **LEARN** `prime-occasion` + TOP "occasions éligibles à la prime" | Automobile Propre, Selectra, aide-sociale.fr, info.gouv.fr, energy suppliers |
| Battery health | soh batterie (voiture électrique, zoe, tesla, obligatoire, prix, comment savoir); certificat (état) batterie voiture électrique | Medium, rising 🟡 | Informational → action | **LEARN** `soh-batterie`; GEN battery block | Automobile Propre, test providers |

Why it matters: France's used-EV CEE prime (from 1 Sep 2026) requires **≥80% of original battery capacity**, a car first registered in France 2017–2023, a purchase through a professional, and three years of ownership. The amount depends on the supplier, roughly €337 by one estimate 🟢 ([Connaissance des Énergies/AFP](https://www.connaissancedesenergies.org/afp/entree-en-vigueur-dune-nouvelle-aide-pour-lachat-dune-voiture-electrique-doccasion-260901)). So subsidy and SoH queries meet in one page: "Which used EVs qualify for the prime". We can compute that from registration year plus a battery note. "soh batterie obligatoire" in autocomplete reflects this 🟡. Leasing social is mainly a new-car scheme. Link to it, don't build for it 🟡.

Context: La Centrale reported used-EV searches up 214% on 20 Sep 2026 vs 28 Feb 2026 (via Les Echos, on-platform) 🟡 ([Presse-citron](https://www.presse-citron.net/voiture-electrique-populaire-france-recherches/)).

## 5. Belgium (nl-BE, fr-BE)

| Cluster | Real phrasing seen 🟢 | Rel. demand 🟡 | Intent | Page type | Note |
|---|---|---|---|---|---|
| Head (nl-BE) | tweedehands elektrische auto (belgië, van mossel, fiscaal aftrekbaar); **elektrische wagen tweedehands** / tweedehands elektrische wagen(s te koop) | High | Transactional | TOP hubs | Flemish users say "wagen" as well as "auto": put both in titles and H1 variants |
| Cross-border (nl-BE) | elektrische auto tweedehands duitsland | Medium | Research | USED cross-country block | Same angle as NL |
| Tax / premium (nl-BE) | fiscaal aftrekbaar; verkeersbelasting elektrische wagen tweedehands; premie tweedehands elektrische wagen | Medium | Informational | **LEARN** `fiscaliteit-be` (company-car angle, per launch-plan) | Belgian-specific: company-car deductibility drives lease-return supply |
| Head (fr-BE) | voiture électrique occasion (belgique, pas cher, 6000 euros, moins de 10000 euros, luxembourg, france) | High | Transactional | TOP `moins-de-10000` (fr-BE) | Same budget phrasing as France |
| Battery health | (no BE-specific seeds tested) | 🔴 | Informational | LEARN shared with NL/FR | VRT ran a story on used-EV battery tests (2026-04) |

Ranking: AutoScout24 BE, 2dehands, Gocar, VRT, Van Mossel (dealer group) 🟡.

## 6. United Kingdom (en-GB)

| Cluster | Real phrasing seen 🟢 | Rel. demand 🟡 | Intent | Page type | Who ranks (observed) |
|---|---|---|---|---|---|
| Head | used electric cars (for sale, near me, uk, to avoid); used ev (for sale, cars) | High | Transactional | TOP hubs; don't chase head | Auto Trader, Cinch, Motorpoint, CarGurus, webuyanycar |
| Best / budget | best used ev (to buy in 2026, suv, uk, under 20k/30k, deals); best used electric car(s) (under 10k/15k/20k); used electric car under 5k/10k/12k/15k/20k | High | Research | **TOP** `under-5000/10000/15000/20000` (GBP) | Auto Express, CarGurus UK, Carsa, Honest John, Carwow, electricdrives.tv |
| Model + used | used tesla model 3 (long range, performance, 2023/2024/2025); used nissan leaf (62 kwh, battery, review); used mg4 (long range, trophy, xpower, urban) | High | Research → buy | **GEN + USED**. "used nissan leaf battery" shows battery-size intent | Auto Trader, dealers, What Car?/Auto Express reviews |
| Avoid / known issues | used electric cars to avoid | Medium-high | Informational | **LEARN** `used-evs-to-avoid` built from known-issues data (Phase 3) | Auto Express, Honest John |
| Battery health | ev battery health check (near me, cost, certificate, tool, app, uk) | Medium, rising (policy push for mandatory certificates) | Informational → action | **LEARN** `battery-health-check` + GEN battery block | Electrifying.com, Motorpoint, AVILOO, trade press |
| Worth it | is it worth buying a used electric car (uk); should i buy a used electric car; new or used | Medium | Informational | **LEARN** `is-a-used-ev-worth-it` | Electrifying, What Car?, Which? |
| Grant | used electric car grant (uk, scotland); second hand electric car grant | Low-medium | Informational | Short LEARN section, not a page, unless a scheme exists 🔴 | Gov / Energy Saving Trust (Scotland) |

Traps: "battery health check" alone means phones and laptops 🟢, so always use "EV battery health check". UK autocomplete mixes in US ($) and Indian (Bangalore) results, so hreflang `en-GB` and £ prices matter.

Context: iVendi reported EV share of UK used-car searches rising from 0.53% to 1.34% (2022, on-platform, old) 🔴 ([Car Dealer Magazine](https://cardealermagazine.co.uk/online-used-electric-car-searches-treble-in-12-months-according-to-new-data/258709)).

## 7. Spain and Italy (Phase 4, brief)

| Country | Real phrasing seen 🟢 | Takeaway 🟡 | Page type when we open |
|---|---|---|---|
| ES | coche eléctrico segunda mano (barato, madrid, mallorca, canarias, milanuncios, wallapop); comprar coche eléctrico de ocasión; mejor coche eléctrico (calidad precio) segunda mano; plan moves (iii, 2025, 2026) segunda mano | "segunda mano" is the main term and "de ocasión" second. Searches are strongly regional (cities, islands), and subsidy interest goes through Plan MOVES | TOP + LEARN `plan-moves`; city pages only with demand evidence |
| IT | auto elettrica usata (economica, conviene, sotto i 5.000 / 10000 euro, prezzo, subito); auto elettriche usate (prezzi in caduta, vicino a me); migliore auto elettrica usata 2026; incentivi auto elettrica usata 2025/2026 | Price-led like DE and FR; "conviene" equals "is it worth it" | TOP `sotto-i-10000`, LEARN `conviene`, LEARN `incentivi` |

## 8. Cross-country patterns (what this changes in seo-plan.md)

1. **Price-cap rankings are the biggest programmatic win** 🟡. Every market autocompletes price ladders. Add `under-{price}` lists to the 10 launch rankings, with caps in country config (FR needs 5k–25k; UK uses £).
2. **Titles need the local "used" word plus year and battery size.** Use "occasion" and "tweedehands" (NL), "wagen" (BE-nl), "gebraucht" (DE), "occasion"/"d'occasion" (FR), "used" (UK). People search "model 3 occasion 2021" and "leaf 62 kwh", which matches our generation and variant split.
3. **Battery health is one cluster in every country.** Build one canonical learn article and translate it, plus a GEN battery block. In FR it also decides who gets the prime (≥80%).
4. **Subsidy pages are evergreen URLs with changing content.** Use one URL per country (no year in the slug), show `dateModified`, and put the year in the title.
5. **Skip lease queries for now.** "private lease" and "leasen" appear on almost every NL seed 🟢, but they are a different product. Park in ROADMAP.
6. **Tow-bar, small, SUV and long-range** recur as modifiers in NL and DE. They are cheap filter-driven rankings once the data has those fields.

## 9. Limits

- No absolute volumes. Google Trends returned HTTP 429. We did not use Keyword Planner or paid tools (they need an account) 🔴.
- Autocomplete depends on the moment and the person. We sent no cookies, but results can vary by day 🟡.
- The competitor lists come from a US-region web search, not a local SERP. Treat them as "known players", not as rankings 🟡.
- The on-platform interest figures (AutoScout24, La Centrale, iVendi) measure their own users, not Google.
- BE battery queries, UK grants and ES/IT were only sampled lightly 🔴.
- **Next step:** after launch, pull 90 days of Search Console queries per country property and replace every 🟡 rank here with impressions.

## Sources (all opened 2026-11-15)

- Google autocomplete, `suggestqueries.google.com/complete/search?client=firefox&hl={lang}&gl={country}&q={seed}` for nl-NL, nl-BE, fr-BE, de-DE, fr-FR, en-GB, es-ES, it-IT (raw output not stored; rerun the seeds above to reproduce)
- Google Trends explore endpoint: HTTP 429, no data
- [AutoScout24 NL: 48% meer interesse in tweedehands EV's](https://www.autoscout24.nl/bedrijf/occasion-dashboard/forse-stijging-48-meer-interesse-in-tweedehands-ev-s-door-hoge-brandstofprijzen/)
- [EVupdate: inruilregeling, subsidie tweedehands EV Q4 2026](https://www.evupdate.nl/elektrisch-rijden/artikel/inruilregeling-fossiele-auto-vervroegd-subsidie-voor-tweedehands-ev-al-in-q4-2026)
- [Connaissance des Énergies / AFP: nouvelle aide VE d'occasion](https://www.connaissancedesenergies.org/afp/entree-en-vigueur-dune-nouvelle-aide-pour-lachat-dune-voiture-electrique-doccasion-260901)
- [Presse-citron: recherches voitures électriques (La Centrale +214%)](https://www.presse-citron.net/voiture-electrique-populaire-france-recherches/)
- [Fiches-auto: hausse du carburant, intérêt pour l'électrique](https://www.fiches-auto.fr/articles-auto/nouveautes-automobiles/s-4116-hausse-du-carburant-explosion-de-l-interet-pour-l-electrique-les-chiffres.php)
- [Car Dealer Magazine: used EV searches nearly treble (2022, iVendi)](https://cardealermagazine.co.uk/online-used-electric-car-searches-treble-in-12-months-according-to-new-data/258709)
- Competitor examples seen in search: [ANWB koopgids tweedehands EV](https://www.anwb.nl/auto/elektrisch-rijden/elektrische-autos/koopgids-tweedehands-ev), [AutoScout24 NL beste koop](https://www.autoscout24.nl/informeren/advies/beste-autos/beste-koop-tweedehands-elektrische-auto/), [ADAC gebrauchte Elektroautos](https://www.adac.de/der-adac/regionalclubs/hessen-thueringen/sicherheit-mobilitaet/gebrauchte-elektroautos/), [mobile.de günstige gebrauchte Elektroautos](https://www.mobile.de/magazin/artikel/guenstige-gebrauchte-elektroautos), [Caroom laquelle choisir](https://www.caroom.fr/guide/voiture-propre/electrique/occasion/laquelle-choisir), [Capcar meilleure VE occasion](https://www.capcar.fr/blog/meilleure-voiture-electrique-occasion), [Auto Express best used EVs](https://www.autoexpress.co.uk/best/used-electric-cars), [CarGurus UK](https://www.cargurus.co.uk/Cars/articles/best-used-electric-cars), [Electrifying: battery health checks](https://www.electrifying.com/blog/article/electric-groups-call-for-used-battery-health-checks)
