# CarCard

A car (model generation) in card view: Explore on phones, rankings and shortlists.

- Order: name and years, used price range with its country, then three facts. Real range (winter to summer), km added in 20 minutes, and the monthly money chip.
- Prices are always a range with the market named ("used, in the Netherlands"), never a falsely exact single price.
- The whole card links to the car page. The icon ShortlistButton sits top-right (48px, aria-label naming the car); ticked cards show the tick-road and a sunflower-tint button.
- Simple mode: 3 facts. Detailed: 6. Nerd: add the quality tier chip and the source count.
- `evs-card` uses `surface`, a 1.5px `line` border, `radius-lg` and `shadow-sticker`. On `paper` (white), the border does the work.

## Catalogue card (T-130, signed off 2026-11-17)

On the catalogue page: 16:9 photo with a "#n popular" tag when sorted by popularity, the credit line under the photo (Decision 081), name + years, used price band with the country, three facts (winter km, summer km, km in 20 min), shortlist button. Phones use the compact horizontal version (photo 116 px left). Layout: `explorations/staging-r1/`.
