---
title: "Stekkers en tweerichtingsladen"
slug: plugs-and-bidirectional
lang: nl
review: needed
updated: 2026-11-15
glossary: [ac-charging, dc-charging, usable-vs-gross, not-disclosed]
sources:
  - {title: "EV Shortlist research R-01: bidirectional charging and plug standards", url: "https://github.com/zkMenno/EV-Finder/blob/main/research/R-01-bidirectional-and-connectors.md", retrieved: 2026-11-15}
  - {title: "electrive: Renault and The Mobility House launch V2G project in France", url: "https://www.electrive.com/2024/10/22/renault-and-the-mobility-house-launch-v2g-project-in-france", retrieved: 2026-11-15}
  - {title: "electrive: Germany clears the way for bidirectional charging", url: "https://www.electrive.com/2025/11/14/germany-clears-the-way-for-bidirectional-charging", retrieved: 2026-11-15}
  - {title: "BMW Group: Germany's first bidirectional V2G charging offer from BMW Group and E.ON", url: "https://newsroom.bmwgroup.com/global/germanys-first-bidirectional-vehicle-to-grid-v2g-charging-offer-from-bmw-group-and-eon-wallbox-and-electricity-tariff-now-available-to-order", retrieved: 2026-11-15}
  - {title: "electrive: VW and Elli launch V2G offer with up to €720 annual bonus", url: "https://electrive.com/2026/06/23/vw-and-elli-launch-v2g-offer-with-up-to-e720-euros-annual-bonus", retrieved: 2026-11-15}
  - {title: "electrive: VW subsidiary Elli exits hardware business", url: "https://electrive.com/2026/11/03/vw-subsidiary-elli-exits-hardware-business-opens-doors-to-investors", retrieved: 2026-11-15}
  - {title: "Volkswagen Austria: Bidirektionales Laden", url: "https://www.volkswagen.at/elektroauto/laden/bidirektionales-laden", retrieved: 2026-11-15}
  - {title: "EUR-Lex: Commission Delegated Regulation (EU) 2025/656", url: "https://eur-lex.europa.eu/eli/reg_del/2025/656/oj/eng", retrieved: 2026-11-15}
  - {title: "go-e: AFIR explained (ISO 15118-20 from 2027)", url: "https://go-e.com/en/magazine/afir", retrieved: 2026-11-15}
  - {title: "KEBA: AFIR FAQ, ISO 15118-20 from 2027", url: "https://www.keba.com/en/news/emobility/afir-compliant-with-keba-kecontact-p40-and-p40-pro", retrieved: 2026-11-15}
---

# Stekkers en tweerichtingsladen

Deze pagina gaat over twee vragen die kopers vaak stellen: "Welke stekker heeft deze auto?" en "Kan deze auto mijn huis van stroom voorzien?". Het gaat over Europa en het Verenigd Koninkrijk.

## Stekkers in Europa

Je hoeft maar een paar stekkers te kennen ([ons onderzoeksverslag R-01](https://github.com/zkMenno/EV-Finder/blob/main/research/R-01-bidirectional-and-connectors.md)):

- **Type 2** voor [[ac-charging|AC-laden]] thuis en aan de laadpaal in de straat. Elke huidige auto in Europa heeft deze aansluiting.
- **CCS2** voor [[dc-charging|DC-snelladen]].
- **CHAdeMO**, een oudere snellaadstekker. Die vind je op sommige oudere tweedehands auto's, zoals de eerste twee generaties van de Nissan Leaf, de Nissan e-NV200 en de Mitsubishi Outlander plug-in hybride. CHAdeMO-laders worden steeds zeldzamer.
- **Oudere Tesla Model S en X** (van vóór 2019) gebruikten bij Tesla Superchargers een aangepaste Type 2-stekker. Tesla's die nu in Europa worden verkocht, hebben CCS2.

Kijk je naar een tweedehands auto met CHAdeMO? Controleer dan of er genoeg werkende CHAdeMO-laders zijn op de routes die jij rijdt.

## Drie soorten "stroom eruit"

"Bidirectioneel" betekent dat de auto stroom kan teruggeven, en niet alleen kan opnemen. Er zijn drie niveaus ([R-01](https://github.com/zkMenno/EV-Finder/blob/main/research/R-01-bidirectional-and-connectors.md)):

- **V2L (vehicle to load):** de auto voedt een apparaat, zoals een waterkoker, een e-bikelader of kampeerspullen, via een stopcontact of een adapter. Komt vrij vaak voor op nieuwere auto's.
- **V2H (vehicle to home):** de auto voedt je huis, bijvoorbeeld 's avonds of bij een stroomstoring. Daarvoor heb je een speciale laadpaal en installatie nodig.
- **V2G (vehicle to grid):** de auto levert stroom terug aan het net als het net dat nodig heeft, en jij krijgt daarvoor geld of korting. Daarvoor heb je een speciale laadpaal nodig **en** een energiecontract dat dit ondersteunt.

V2L is niet hetzelfde als V2H. Een auto met een stopcontact voor apparaten kan daardoor nog niet je huis van stroom voorzien.

## Twee manieren, twee prijsniveaus

Waar de vermogenselektronica zit, bepaalt wat de laadpaal kost ([R-01](https://github.com/zkMenno/EV-Finder/blob/main/research/R-01-bidirectional-and-connectors.md)):

- **AC-route:** de auto heeft een ingebouwde lader die twee kanten op werkt. De laadpaal kan vrij eenvoudig blijven. Renault doet dit bij de Renault 5 en de Alpine A290, met de PowerBox Verso-laadpaal ([electrive](https://www.electrive.com/2024/10/22/renault-and-the-mobility-house-launch-v2g-project-in-france)).
- **DC-route:** de laadpaal zet de stroom om en heeft daarvoor veel duurdere elektronica nodig. De ID.-modellen van Volkswagen gebruiken deze route, met een DC-laadpaal ([Volkswagen](https://www.volkswagen.at/elektroauto/laden/bidirektionales-laden)).

Gebruik alleen een laadpaal die de fabrikant van je auto goedkeurt voor tweerichtingsladen.

## Het hangt af van waar je woont

Of een auto voor jou V2H of V2G kan doen, verschilt per land, omdat energieregels en aanbiedingen verschillen.

- **Frankrijk** had het eerste commerciële V2G-aanbod: de Renault 5 en Alpine A290 met de PowerBox Verso en een Mobilize Power-contract, gestart in oktober 2024 ([electrive](https://www.electrive.com/2024/10/22/renault-and-the-mobility-house-launch-v2g-project-in-france)).
- **Duitsland** paste in november 2025 de wet aan: over stroom die in een auto is opgeslagen en later wordt teruggeleverd, betaal je niet langer twee keer netkosten en energiebelasting. Een slimme meter blijft nodig ([electrive](https://www.electrive.com/2025/11/14/germany-clears-the-way-for-bidirectional-charging)). Sindsdien komen er aanbiedingen. BMW en E.ON verkopen sinds februari 2026 een V2G-pakket voor de nieuwe BMW iX3, met een laadpaal, een tarief en een slimme meter als je die nog niet hebt ([BMW Group](https://newsroom.bmwgroup.com/global/germanys-first-bidirectional-vehicle-to-grid-v2g-charging-offer-from-bmw-group-and-eon-wallbox-and-electricity-tariff-now-available-to-order)). Volkswagen en Elli kondigden een V2G-aanbod aan, eerst in Duitsland en later in Frankrijk en het Verenigd Koninkrijk ([electrive](https://electrive.com/2026/06/23/vw-and-elli-launch-v2g-offer-with-up-to-e720-euros-annual-bonus)).
- **Andere landen:** veel aanbiedingen zijn nog proeven of aankondigingen. Op de pagina van elke auto tonen we de status per land, met de datum waarop we het voor het laatst hebben gecontroleerd.

Aanbiedingen veranderen vaak. Elli maakte bijvoorbeeld in november 2026 bekend dat het stopt met eigen laadpalen en voortaan een DC-laadpaal van een partner gebruikt ([electrive](https://electrive.com/2026/11/03/vw-subsidiary-elli-exits-hardware-business-opens-doors-to-investors)). Gegevens die ouder zijn dan 90 dagen markeren we met "mogelijk verouderd".

## Een tweedehands auto kopen: let op de voorwaarden

Bij een tweedehands auto gelden er vaak voorwaarden voor "kan V2G". Volkswagen is een goed voorbeeld ([Volkswagen](https://www.volkswagen.at/elektroauto/laden/bidirektionales-laden)):

- Alle ID.-modellen met **ID. Software 6** kunnen in twee richtingen laden.
- Auto's met **ID. Software 3.5** (tot versie 6) kunnen het alleen met een accu van **77 kWh of meer**.
- Bij die auto's met 3.5 is het ontladen begrensd op in totaal 10.000 kWh of 4.000 uur.
- Volkswagen verwijst voor de regels over tweerichtingsladen en de accu naar de voorwaarden van de nieuwwagengarantie.

Twee auto's van hetzelfde model kunnen dus een ander antwoord geven. Vraag de verkoper naar:

1. de softwareversie,
2. de accugrootte, als [[usable-vs-gross|bruikbare (netto) capaciteit]] in kWh,
3. de bouwdatum,

en kijk op de eigen pagina van de fabrikant welke auto's in aanmerking komen. Zegt een fabrikant niet of een auto het ondersteunt, dan tonen we "[[not-disclosed|niet bekendgemaakt]]" in plaats van te gokken.

**Slijtage van de accu:** we gokken niet hoeveel tweerichtingsladen de accu laat slijten. Lees de garantievoorwaarden van de fabrikant voor jouw auto.

## Een laadpaal kopen vanaf 2027

Vanaf 1 januari 2027 moet elke nieuwe of gerenoveerde laadpaal in de EU de standaard ISO 15118-20 ondersteunen ([EUR-Lex](https://eur-lex.europa.eu/eli/reg_del/2025/656/oj/eng)). Dat is de taal waarmee auto en lader met elkaar praten. Het maakt tweerichtingsladen mogelijk aan de softwarekant, maar het maakt de laadpaal **niet** geschikt om stroom terug te leveren: dat eisen de regels niet ([go-e](https://go-e.com/en/magazine/afir); [KEBA](https://www.keba.com/en/news/emobility/afir-compliant-with-keba-kecontact-p40-and-p40-pro)). Je huidige laadpaal is prima, en je auto moet de standaard ook ondersteunen. Meer hierover op onze pagina "Laden in 2026: wat er veranderd is".
