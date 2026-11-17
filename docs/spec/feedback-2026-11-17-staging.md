# Menno's staging feedback (2026-11-17)

From a status-check chat (no push), logged by WS0. Decisions are Menno's.

| # | Feedback | Routed to | Task / Decision |
|---|---|---|---|
| 1 | Landing: remove the full car list; "Show all cars" button → catalogue page like ev-database.org: filters, default sort popularity (top40.yaml registrations blended with Menno's picks, Decision 038), user sorts by price, range, battery, charging speed, year | WS2 (+ UX layout) | T-130 |
| 2 | Landing: "Popular used EVs" section, roughly Menno's sheet of EV generations (generation level, not trims) | WS3 (list) + WS2 (section) | T-131 |
| 3 | Hero questions + answer chips too messy: fewer questions on screen, clearer chips, results easy to scan | UX first, then WS2 | T-132 |
| 4 | Car photos: maker press photos first, Wikimedia Commons fallback (CC BY / BY-SA, credit under every photo); log press terms per maker; skip makers whose terms forbid it; never hotlink; licence + credit per image in data | WS3, WS1, WS2 | Decision 081; T-133, T-134, T-135 |
| 5 | Catalogue ~200 cars vs EV Database 1500+: plan every EV variant sold in Europe since ~2011 (trim × year), open licensed sources first (EEA CO2, RDW, KBA, OpenEV); never scrape EV Database or marketplaces; report count + licences before building | WS1 + WS3 | T-136 |
| 6 | English only for now; keep /{country}/{lang}/ (Decision 015) but serve /{country}/en/ everywhere, English default; park translations until after launch | WS0 decision, WS2 | Decision 082; T-137 |
