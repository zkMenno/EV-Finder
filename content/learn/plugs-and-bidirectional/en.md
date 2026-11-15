---
title: "Plugs and two-way charging"
slug: plugs-and-bidirectional
lang: en
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

# Plugs and two-way charging

This page covers two questions buyers ask a lot: "Which plug does this car use?" and "Can this car power my house?". It is about Europe and the UK.

## Plugs in Europe

There are only a few plugs to know ([our research note R-01](https://github.com/zkMenno/EV-Finder/blob/main/research/R-01-bidirectional-and-connectors.md)):

- **Type 2** for [[ac-charging|AC charging]] at home and at street posts. Every current car in Europe has it.
- **CCS2** for [[dc-charging|DC fast charging]].
- **CHAdeMO**, an older fast-charging plug. You'll find it on some older used cars, such as the first two generations of the Nissan Leaf, the Nissan e-NV200 and the Mitsubishi Outlander plug-in hybrid. CHAdeMO chargers are getting harder to find.
- **Older Tesla Model S and X** (before 2019) used a modified Type 2 plug at Tesla Superchargers. Teslas sold in Europe now use CCS2.

When you look at a used car with CHAdeMO, check that there are enough working CHAdeMO chargers on the routes you drive.

## Three kinds of "power out"

"Bidirectional" means the car can give power back, not only take it. There are three levels ([R-01](https://github.com/zkMenno/EV-Finder/blob/main/research/R-01-bidirectional-and-connectors.md)):

- **V2L (vehicle to load):** the car powers a device, such as a kettle, an e-bike charger or camping gear, through a socket or an adapter. Quite common on newer cars.
- **V2H (vehicle to home):** the car powers your house, for example in the evening or during a power cut. This needs a special wallbox and installation.
- **V2G (vehicle to grid):** the car sends power back to the grid when the grid needs it, and you get paid or get a discount. This needs a special wallbox **and** an energy contract that supports it.

V2L is not the same as V2H. A car with a socket for appliances can't power your house just because of that.

## Two ways to build it, two price levels

Where the power electronics sit decides what the wallbox costs ([R-01](https://github.com/zkMenno/EV-Finder/blob/main/research/R-01-bidirectional-and-connectors.md)):

- **AC route:** the car has a two-way charger built in. The wallbox can stay fairly simple. Renault uses this for the Renault 5 and Alpine A290 with its PowerBox Verso wallbox ([electrive](https://www.electrive.com/2024/10/22/renault-and-the-mobility-house-launch-v2g-project-in-france)).
- **DC route:** the wallbox does the conversion, so it needs much more expensive electronics. Volkswagen's ID. cars use this route with a DC wallbox ([Volkswagen](https://www.volkswagen.at/elektroauto/laden/bidirektionales-laden)).

Only use a wallbox that the carmaker approves for two-way charging with your car.

## It depends on where you live

Whether a car can do V2H or V2G for you depends on the country, because energy rules and offers differ.

- **France** had the first commercial V2G offer: the Renault 5 and Alpine A290 with the PowerBox Verso and a Mobilize Power contract, launched in October 2024 ([electrive](https://www.electrive.com/2024/10/22/renault-and-the-mobility-house-launch-v2g-project-in-france)).
- **Germany** changed its law in November 2025: power that is stored in a car and later fed back no longer pays grid fees and electricity tax twice. A smart meter is still needed ([electrive](https://www.electrive.com/2025/11/14/germany-clears-the-way-for-bidirectional-charging)). Since then, offers have started. BMW and E.ON sell a V2G package for the new BMW iX3 (from February 2026), with a wallbox, a tariff and a smart meter if you don't have one yet ([BMW Group](https://newsroom.bmwgroup.com/global/germanys-first-bidirectional-vehicle-to-grid-v2g-charging-offer-from-bmw-group-and-eon-wallbox-and-electricity-tariff-now-available-to-order)). Volkswagen and Elli announced a V2G offer for Germany first, with France and the UK later ([electrive](https://electrive.com/2026/06/23/vw-and-elli-launch-v2g-offer-with-up-to-e720-euros-annual-bonus)).
- **Other countries:** many offers are still pilots or announcements. We show the status per country on each car's page, with the date we last checked.

Offers change often. Elli, for example, said in November 2026 that it will stop making its own wallboxes and will use a partner's two-way DC wallbox instead ([electrive](https://electrive.com/2026/11/03/vw-subsidiary-elli-exits-hardware-business-opens-doors-to-investors)). We flag facts older than 90 days as "may be out of date".

## Buying a used car: check the conditions

For a used car, "can do V2G" often comes with conditions. Volkswagen is a good example ([Volkswagen](https://www.volkswagen.at/elektroauto/laden/bidirektionales-laden)):

- All ID. models with **ID. Software 6** can charge both ways.
- Cars with **ID. Software 3.5** (up to version 6) can do it only with a battery of **77 kWh or more**.
- On those 3.5 cars, discharging is capped at 10,000 kWh or 4,000 hours in total.
- Volkswagen points to its new-car warranty conditions for the rules on two-way charging and the battery.

So two cars of the same model can give different answers. Ask the seller for:

1. the software version,
2. the battery size, as the [[usable-vs-gross|usable (net) capacity]] in kWh,
3. the build date,

and check the maker's own eligibility page. If a maker doesn't say whether a car supports it, we show "[[not-disclosed|not disclosed]]" instead of guessing.

**Battery wear:** we don't guess how much two-way charging wears the battery. Read the maker's warranty terms for your car.

## Buying a wallbox from 2027

From 1 January 2027, every new or renovated wallbox in the EU must support the ISO 15118-20 standard ([EUR-Lex](https://eur-lex.europa.eu/eli/reg_del/2025/656/oj/eng)). That is the language car and charger use to talk. It makes two-way charging possible on the software side, but it does **not** make the wallbox two-way: the rules don't require that ([go-e](https://go-e.com/en/magazine/afir); [KEBA](https://www.keba.com/en/news/emobility/afir-compliant-with-keba-kecontact-p40-and-p40-pro)). Your existing wallbox is fine, and your car must support the standard too. More on our page "Charging in 2026: what's changed".
