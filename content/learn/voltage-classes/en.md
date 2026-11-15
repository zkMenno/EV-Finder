---
title: "400 V, 800 V and more: battery voltage explained"
slug: voltage-classes
lang: en
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

# 400 V, 800 V and more: battery voltage explained

You'll see "400 V" or "800 V" in car reviews and brochures. It is the [[voltage-class|battery voltage]], and it mainly affects how fast a car can charge. For daily driving you won't notice it.

## Why voltage matters for charging

Charging power is voltage times current. With a higher voltage, the car needs less current for the same power. Less current means less heat and thinner cables, so the car can usually charge at high power for longer.

That's the theory. In practice, how fast a car charges depends on the whole car: the battery, its temperature and the software. Look at the [[10-80|charging time from 10 to 80 %]] rather than at the voltage or the [[peak-kw|top charging speed]] alone.

## How we group cars

We group cars by the battery's [[nominal-voltage|nominal voltage]] into three classes. The bands are our own simplification, not an official standard ([our voltage class table](https://github.com/zkMenno/EV-Finder/blob/main/data/taxonomy/voltage_classes.yaml)). Each car's real voltage is also stored and shown, for example 697 V.

| Class | Nominal battery voltage |
|---|---|
| [[400v|400 V]] | about 300 to 550 V |
| [[800v|800 V]] | about 550 to 850 V |
| [[900v-plus|900 V and higher]] | about 850 V and up |

## 400 V: the long-time standard

Most electric cars on the road so far use a 400 V battery.

- **Good:** they charge at full speed on almost every [[dc-charging|DC fast charger]], old or new, because the charging network was built around them. They are usually cheaper to build.
- **Watch out:** at very high charging power the current gets very large. That limits how high their top charging speed can go.

## 800 V: faster on modern chargers

The Porsche Taycan was the first production car with an 800 V system, presented in September 2019 ([Porsche](https://newsroom.porsche.com/en_AU/2019/products/porsche-taycan-world-premiere-live-all-electric-sports-car-18445.html)). Many brands have followed since.

- **Good:** usually faster charging on modern high-power chargers, and less heat.
- **Watch out:** many older fast chargers only deliver up to about 500 V. On those, an 800 V car must step the voltage up with a [[booster|booster]], or it charges at reduced power. On some cars that is much slower than the advertised top speed. Check [[400v-charger-behaviour|"On older chargers"]] on the car's page before you buy, especially if your usual routes have older chargers.

## 900 V and higher: the newest

A small but growing group of cars goes even higher:

- Lucid has used what it calls a "900V+" architecture in the Lucid Air ([Lucid](https://www.lucidmotors.com/stories/lucid-air-fastest-charging-ev)).
- NIO's ET9 has a drive system that runs at up to 925 V ([Electrek](https://electrek.co/2024/03/27/worlds-first-mass-produced-900v-ev-drive-system-rolls-out/)).
- BYD presented its Super e-Platform in March 2025, with a 1,000 V architecture and charging power of up to 1,000 kW ([BYD](https://www.byd.com/us/news-list/BYD-Unveils-Super-e-Platform-Megawatt-Flash-Charging-Electric-Vehicles-Matching-Refueling-Speeds)).

- **Good:** the highest charging power, on chargers that can deliver it.
- **Watch out:** few chargers outside China can deliver these speeds yet. How these cars behave on older or lower-voltage chargers depends on the car's own converter. Treat claims with care until there are independent tests.

## What this means for a used car

- A 400 V car is the simple choice: it charges well everywhere.
- An 800 V car can save time on long trips, if it also charges well on older chargers. Check that before you buy.
- For most daily driving, charging at home, voltage makes no difference at all.
