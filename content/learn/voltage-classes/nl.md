---
title: "400V, 800V en hoger: accuspanning uitgelegd"
slug: voltage-classes
lang: nl
review: needed
updated: 2026-11-15
glossary: [voltage-class, 400v, 800v, 900v-plus, nominal-voltage, booster, 400v-charger-behaviour, peak-kw, 10-80, dc-charging]
sources:
  - {title: "Porsche Newsroom: World premiere of the Porsche Taycan (4 September 2019)", url: "https://newsroom.porsche.com/en_AU/2019/products/porsche-taycan-world-premiere-live-all-electric-sports-car-18445.html", retrieved: 2026-11-15}
  - {title: "Lucid Motors: The Lucid Air is the fastest charging EV ever", url: "https://www.lucidmotors.com/stories/lucid-air-fastest-charging-ev", retrieved: 2026-11-15}
  - {title: "Electrek: World's first mass-produced 900V EV drive system rolls out (NIO ET9)", url: "https://electrek.co/2024/03/27/worlds-first-mass-produced-900v-ev-drive-system-rolls-out/", retrieved: 2026-11-15}
  - {title: "BYD: BYD unveils Super e-Platform with megawatt flash charging (17 March 2025)", url: "https://www.byd.com/us/news-list/BYD-Unveils-Super-e-Platform-Megawatt-Flash-Charging-Electric-Vehicles-Matching-Refueling-Speeds", retrieved: 2026-11-15}
  - {title: "EV Shortlist taxonomy: voltage classes (our own band definitions)", url: "https://github.com/zkMenno/EV-Finder/blob/main/data/taxonomy/voltage_classes.yaml", retrieved: 2026-11-15}
---

# 400V, 800V en hoger: accuspanning uitgelegd

In tests en brochures zie je "400V" of "800V" staan. Dat is de [[voltage-class|accuspanning]], en die bepaalt vooral hoe snel een auto kan laden. Bij het dagelijkse rijden merk je er niets van.

## Waarom spanning uitmaakt bij het laden

Laadvermogen is spanning maal stroom. Bij een hogere spanning heeft de auto minder stroom nodig voor hetzelfde vermogen. Minder stroom betekent minder warmte en dunnere kabels, dus kan de auto meestal langer met hoog vermogen laden.

Dat is de theorie. In de praktijk hangt de laadsnelheid af van de hele auto: de accu, de temperatuur en de software. Kijk daarom naar de [[10-80|laadtijd van 10 naar 80 %]] en niet alleen naar de spanning of de [[peak-kw|maximale laadsnelheid]].

## Hoe wij auto's indelen

We delen auto's in drie klassen in op basis van de [[nominal-voltage|nominale spanning]] van de accu. Die grenzen zijn onze eigen vereenvoudiging, geen officiële norm ([onze tabel met spanningsklassen](https://github.com/zkMenno/EV-Finder/blob/main/data/taxonomy/voltage_classes.yaml)). We bewaren en tonen ook de echte spanning van elke auto, bijvoorbeeld 697 V.

| Klasse | Nominale accuspanning |
|---|---|
| [[400v|400V]] | ongeveer 300 tot 550 V |
| [[800v|800V]] | ongeveer 550 tot 850 V |
| [[900v-plus|900V en hoger]] | ongeveer 850 V en meer |

## 400V: de vertrouwde standaard

De meeste elektrische auto's op de weg hebben tot nu toe een 400V-accu.

- **Goed:** ze laden op vrijwel elke [[dc-charging|DC-snellader]] op volle snelheid, oud of nieuw, omdat het laadnetwerk rond deze auto's is gebouwd. Ze zijn meestal goedkoper te maken.
- **Let op:** bij heel hoog laadvermogen wordt de stroom erg groot. Dat begrenst hoe hoog de maximale laadsnelheid kan worden.

## 800V: sneller op moderne laders

De Porsche Taycan was de eerste productieauto met een 800V-systeem, gepresenteerd in september 2019 ([Porsche](https://newsroom.porsche.com/en_AU/2019/products/porsche-taycan-world-premiere-live-all-electric-sports-car-18445.html)). Sindsdien volgden veel merken.

- **Goed:** meestal sneller laden op moderne laders met hoog vermogen, en minder warmte.
- **Let op:** veel oudere snelladers leveren maar tot ongeveer 500 V. Daaraan moet een 800V-auto de spanning omhoog brengen met een [[booster|booster]], of hij laadt met minder vermogen. Bij sommige auto's is dat veel trager dan de opgegeven topsnelheid. Kijk vóór je koopt naar [[400v-charger-behaviour|"Op oudere laders"]] op de pagina van de auto, zeker als er op jouw vaste routes oudere laders staan.

## 900V en hoger: het nieuwste

Een kleine maar groeiende groep auto's gaat nog hoger:

- Lucid gebruikt in de Lucid Air wat het een "900V+"-architectuur noemt ([Lucid](https://www.lucidmotors.com/stories/lucid-air-fastest-charging-ev)).
- De ET9 van NIO heeft een aandrijving die tot 925 V werkt ([Electrek](https://electrek.co/2024/03/27/worlds-first-mass-produced-900v-ev-drive-system-rolls-out/)).
- BYD presenteerde in maart 2025 zijn Super e-Platform, met een architectuur van 1.000 V en een laadvermogen tot 1.000 kW ([BYD](https://www.byd.com/us/news-list/BYD-Unveils-Super-e-Platform-Megawatt-Flash-Charging-Electric-Vehicles-Matching-Refueling-Speeds)).

- **Goed:** het hoogste laadvermogen, op laders die dat kunnen leveren.
- **Let op:** buiten China kunnen nog maar weinig laders deze snelheden leveren. Hoe deze auto's zich gedragen op oudere laders of laders met een lagere spanning, hangt af van de omvormer in de auto. Wees voorzichtig met claims tot er onafhankelijke tests zijn.

## Wat betekent dit voor een tweedehands auto?

- Een 400V-auto is de eenvoudige keuze: hij laadt overal goed.
- Een 800V-auto kan op lange ritten tijd besparen, als hij ook op oudere laders goed laadt. Controleer dat voordat je koopt.
- Voor het meeste dagelijkse rijden, met thuisladen, maakt de spanning helemaal niets uit.
