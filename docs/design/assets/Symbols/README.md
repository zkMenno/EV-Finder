# Symbols

The EV Shortlist icon set: map symbols on a 24px grid, 2px ink line (#16233A in the files), round caps and joins, at most one flat fill from the palette (sky #3B78AE, sunflower #FFD166, sky tint #CFE3F3, meadow #7BB661). Version 1, to refine with the logo round.

| Group | Icons |
|---|---|
| Map and navigation | home-pin, flag, route, explore, learn, search, filter |
| Shortlist | shortlist (tick + sun), rule-out, compare, share |
| Range and weather | range (road to the sun), summer, winter |
| Charging | charge-stop, fast-charge, home-charging, plug-type2, plug-ccs, voltage-400, voltage-800, voltage-900 |
| Battery | chemistry, air-cooled, battery-health |
| Money and cars | price, monthly-cost, car, used-car, see-listings, boot-space |
| Data and help | legend (the ⓘ), source, known-issue, detail-levels |

- In the product, inline the SVG and swap the ink stroke for `currentColor` (follows `ink` in both themes); keep fills on tokens (`var(--sky)`, `var(--sunflower)`, `var(--paper-sea)`).
- Sizes: 24px in UI, 20px inside buttons and chips, 16px minimum. Always paired with a text label; never the only signal.
- Never a lightning bolt on its own as "EV": bolts only mean charging speed or voltage class.
