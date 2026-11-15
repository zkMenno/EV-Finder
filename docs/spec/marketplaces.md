<!-- Mirror of the claude.ai spec doc, tab "Marketplaces" (rev 1), exported 2026-11-15 by WS0. For builders this repo copy wins; product changes start in the doc and WS0 mirrors them here. Transcribed from the export; if a figure looks off, check the doc tab. -->

# Used-car marketplaces per country

The 3–5 sites per country where used cars are actually bought, who owns them, and what that means for deep links, feeds and price ranges. Order is roughly by reach. 🟢 = confirmed in this research round (Nov 2026), 🟡 = from general knowledge, check before building the country config. Facebook Marketplace is big almost everywhere but cannot be deep-linked or fed reliably, so it is left out of the tables.

## The big finding: about eight groups own most of the market

One partnership conversation covers several countries at once. That makes layer 1 (feeds) far more realistic than one deal per site, and it is also why layer 3 (automated sampling) is risky: these groups have legal teams and strong bot detection.

| Group | Car marketplaces | Countries |
| --- | --- | --- |
| Autonex (AutoScout24 group) | AutoScout24, AutoTrack, Gaspedaal, gebrauchtwagen.at, AutoTrader.ca | DE, NL, BE, LU, IT, FR, AT, ES, PL, Nordics, CA 🟢 |
| Adevinta | mobile.de, Kleinanzeigen, leboncoin, Marktplaats, 2dehands/2ememain, Subito, automobile.it, Adverts.ie | DE, FR, NL, BE, IT, IE 🟢 |
| OLX Group (Prosus) | Otomoto, Standvirtual, Autovit, OLX | PL, PT, RO and more 🟢 |
| Vend (ex-Schibsted) | FINN, Blocket, Bytbil, Bilbasen, DBA, Tori | NO, SE, DK, FI 🟢 |
| CAR Group | carsales, Encar, webmotors, chileautos, soloautos | AU, KR, BR, CL, MX 🟢 |
| Carsome | Carlist.my, Mobil123, Carmudi ID, One2car, Wapcar | MY, ID, TH 🟢 |
| Mercado Libre | Mercado Libre Autos, TuCarro | MX, CO, CL, AR 🟡 |
| Independent leaders | Autotrader UK, La Centrale, Trade Me, Sahibinden, Cars24 | UK, FR, NZ, TR, IN |

Note: Adevinta sold its Spanish business (coches.net, Milanuncios) to EQT in early 2026, so Spain is a separate conversation. 🟢

## Launch countries

| Country | Top sites | Notes |
| --- | --- | --- |
| Netherlands | Marktplaats, AutoScout24.nl, AutoTrack, Gaspedaal | AutoScout24 bought AutoTrack and Gaspedaal in Nov 2025, so three of the four big portals now share one owner 🟢 |
| Germany | mobile.de, AutoScout24, Kleinanzeigen, Autohero 🟡 | mobile.de has an official Search-API under a partner contract 🟢; AutoScout24 publishes a monthly used-price index (AGPI) 🟢 |
| France | leboncoin, La Centrale, AutoScout24.fr, ParuVendu, Aramisauto 🟡 | leboncoin is Adevinta 🟢; La Centrale is the car specialist |
| Belgium | AutoScout24.be, 2dehands/2ememain, Gocar.be 🟡 | Since Jan 2026 sellers can add an independent battery health test to the Car-Pass 🟢, a great trust signal to show |
| UK | Autotrader UK, Motors.co.uk, eBay/Gumtree, Carwow 🟡 | Autotrader is the UK's largest marketplace and publishes a monthly Retail Price Index with a used-EV section 🟢 |

## Second wave: US, Australia (+ NZ, Canada as cheap extras)

| Country | Top sites | Notes |
| --- | --- | --- |
| US | Autotrader/KBB (Cox), Cars.com, CarGurus, Carvana 🟡 | Recurrent publishes free used-EV price reports and is a possible partner or competitor 🟢 |
| Australia | carsales, Gumtree, Drive, Carma 🟡 | carsales is CAR Group 🟢, so one deal could extend to KR, BR and CL later |
| New Zealand | Trade Me Motors, AutoTrader NZ 🟡 | Trade Me is the leading marketplace 🟢; used EVs are mostly imported Nissan Leafs from Japan 🟢 |
| Canada | AutoTrader.ca, Kijiji Autos, Clutch, CarGurus 🟡 | AutoTrader.ca is now part of the AutoScout24 group (Autonex) 🟢; Clutch publishes a monthly used-price report 🟢 |

## Rest of Europe

| Country | Top sites | Owner |
| --- | --- | --- |
| Norway | FINN | Vend 🟢 |
| Sweden | Blocket, Bytbil, AutoScout24.se | Vend; AutoScout24 🟢 |
| Denmark | Bilbasen, DBA, AutoScout24.dk | Vend; AutoScout24 🟢 |
| Finland | Nettiauto, Tori | Alma Media; Vend 🟢 |
| Poland | Otomoto, OLX.pl, AutoScout24.pl 🟡 | OLX Group 🟢 |
| Portugal | Standvirtual, OLX.pt, CustoJusto 🟡 | OLX Group 🟢 |
| Spain | coches.net, Wallapop, Milanuncios, AutoScout24.es, Flexicar | EQT (coches.net, Milanuncios) 🟢 |
| Italy | AutoScout24.it, Subito, automobile.it, AutoUncle | AutoScout24; Adevinta 🟢 |
| Austria | willhaben 🟡, AutoScout24.at, gebrauchtwagen.at | AutoScout24 🟢 |
| Switzerland | AutoScout24.ch, tutti/ricardo, car4you 🟡 | Swiss Marketplace Group 🟢 |
| Ireland | DoneDeal, Carzone, Adverts.ie, CarsIreland 🟡 | Adverts.ie is Adevinta 🟢 |

## Emerging and booming markets (Later)

Ember counts 39 countries above 10% EV share of new sales in 2025, 12 of them outside Europe. 🟢 A booming *new* market is not yet a good *used* market: used supply arrives 3–5 years later. So each market is scored on three things: years of EV sales, an online marketplace, and open registration data.

| Country | EV signal | Top sites | Open data | Used-market readiness |
| --- | --- | --- | --- | --- |
| Türkiye | BEVs 17% of new sales in 2025 🟢; used EV sales 18,620 in 2024, +122% 🟢 | Sahibinden, Arabam, Letgo, VavaCars 🟢 | ODMD monthly sales 🟡 | 🟢 High: first emerging market to add |
| South Korea | Mature EV market, used EVs selling faster than petrol at K Car 🟢 | Encar (\~53%), K Car (\~21%), KB Cha Cha Cha (\~13%) 🟢 | K Car monthly price outlook 🟢 | 🟢 High, but needs Korean UI |
| Thailand | EV share above 20% in 2025 🟢 | One2car, Taladrod, Kaidee, Carsome 🟢 | DLT monthly registrations by fuel 🟢 | 🟡 Medium: used EVs only now arriving |
| Malaysia | Growing | Carlist.my, Mudah 🟡, Carsome | 🟡 | 🟡 Medium (same Carsome deal as TH, ID) |
| Indonesia | EV share 15% in 2025 🟢 | OLXmobbi, Mobil123, Carmudi, Carro 🟢 | Gaikindo 🟡 | 🟡 Medium: small used EV pool 🟢 |
| Vietnam | EV share \~40% in 2025 🟢 | Chợ Tốt Xe, Bonbanh, Oto.com.vn 🟢 | 🔴 weak | 🟡 Medium: VinFast's first lease wave ends in 2026 🟢 |
| Brazil | BEV record of 27,166 in Aug 2026 🟢 | Webmotors, OLX, Mobiauto, iCarros 🟢 | ABVE Data monthly (Renavam) 🟢 | 🟡 Medium: volume is very recent |
| Mexico | EV share above Japan's 🟢 | Mercado Libre Autos, Kavak, Seminuevos.com 🟢 | INEGI RAIAVL monthly by model incl. EVs 🟢 | 🟡 Medium |
| India | 176,538 electric cars in 2025, +77% 🟢 | Cars24, Spinny, CarDekho, OLX 🟢 | VAHAN daily registrations by maker 🟢 | 🔴 Low for now: tiny used EV pool |
| Chile, Colombia, Uruguay, Costa Rica | Uruguay 27%, Costa Rica 17%, Colombia near 10% 🟢 | Chileautos (CAR Group), Mercado Libre, TuCarro 🟡 | 🟡 | 🔴 Low |
| Singapore, Philippines, UAE | Singapore above 40% 🟢 | sgCarMart, Carousell, Carmudi PH, Dubizzle, Kavak UAE 🟡 | 🟡 | 🟡 Singapore medium (10-year car rules), others low |
| China (parked) | Above 50% 🟢 | Dongchedi, Che168, Guazi 🟡 | — | Parked: different UX, data and rules |

**Suggested order for emerging markets (🟡 my reasoning):** Türkiye first (Europe-adjacent, big used EV volume already, Latin script), then South Korea, then the Carsome trio (TH, MY, ID) in one go, then Brazil and Chile via CAR Group, then Mexico and Vietnam. India later.

## What this means for the build

1. **Partnerships before scraping.** Approach Autonex, Adevinta, Vend and OLX Group in Phase 1, not Phase 3: four conversations cover nearly all of Europe. Lead with what we give them: qualified, pre-filtered EV buyers on their listings.
2. **Use the free price indices as layer 0.** Autotrader UK's RPI, AutoScout24's AGPI, Indicata's 13-country Market Watch, Recurrent, Clutch and K Car publish used-price trends for free. They give a country-level trend line and a check on our own bands, with no legal risk.
3. **Country config needs a marketplace block:** site, search-URL template, filter-parameter map (make, model, year range, fuel, mileage), affiliate tag, and priority. A builder can add a country by filling this block.
4. **Deep-link templates break when sites change.** A weekly job checks every template still returns results and flags broken ones in the staff dashboard.
