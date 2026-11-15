<!-- Mirror of the claude.ai spec doc, tab "Battery & voltage guide" (rev 1), exported 2026-11-15 by WS0. For builders this repo copy wins; product changes start in the doc and WS0 mirrors them here. Transcribed from the export; if a figure looks off, check the doc tab. -->

# Battery and voltage guide (draft explainer content)

Starting text for the ⓘ popovers and /learn pages. These become rows in the chemistries and voltage\_classes tables and are edited in Sveltia later. Written for buyers, not engineers. 🟡 = general knowledge to have checked by a battery-savvy reviewer before launch; 🟢 = from sources checked in Nov 2026.

## Voltage classes

| Class | What it means | Pros | Cons / watch out |
| --- | --- | --- | --- |
| 400 V class | The long-time standard; most EVs on the road | Charges at full speed on every charger, old or new; usually cheaper | Above roughly 150–250 kW the current gets very high, so peak charging power is limited 🟡 |
| 800 V class | Roughly double the voltage. Porsche Taycan was first (2019), then Hyundai/Kia E-GMP | Faster charging on 350 kW chargers, less heat, thinner cables, often a bit more efficient 🟡 | Needs a booster to charge well on older 400 V chargers. Some early cars without one charge slowly there, so check "Fast on older 400 V chargers" 🟡 |
| 900 V+ class | Newest. Lucid has used 900 V+ since the Air; NIO's ET9 runs up to 925 V; BYD's Super e-Platform runs at 1,000 V 🟢 | The fastest charging, on chargers that can deliver it | Few chargers outside China deliver this yet; gains over 800 V are smaller than the jump from 400 V 🟡 |

Why a slider too: the bands are a simplification. The real number (for example 697 V or 925 V) is stored and shown on every car.

## Battery chemistries

| Chemistry | Status | Pros | Cons | How to look after it |
| --- | --- | --- | --- | --- |
| NMC / NCA (nickel-based) | Mainstream since 2010s | Most energy per kg, so more range; good in the cold 🟡 | More expensive; uses cobalt and nickel; slightly higher fire risk than LFP 🟡 | Charge to about 80–90% daily, 100% before long trips 🟡 |
| LFP (lithium iron phosphate) | Mainstream, fast-growing | Very long life, safer, cheaper, no cobalt or nickel; most makers say 100% daily is fine 🟡 | Less range for the same weight; slower charging and less range in the cold unless preheated; the range estimate can drift 🟡 | Charge to 100% at least weekly so the car recalibrates; precondition before fast charging in winter 🟡 |
| LMFP (manganese-boosted LFP) | Emerging | A bit more range than LFP with similar safety 🟡 | New, so little long-term data 🟡 | As LFP until makers say otherwise 🟡 |
| LMO/NMC blend (early Nissan Leaf) | Older cars only | Cheap used | Combined with air cooling, these packs aged fast in heat 🟡 | Check battery health before buying; avoid frequent fast charging in summer 🟡 |
| Sodium-ion | Emerging: the first mass-production passenger car (Changan, with CATL) was unveiled in Feb 2026 🟢 | No lithium, cobalt or nickel; energy density up to 175 Wh/kg, close to LFP 🟢; strong in the cold 🟢 | Very new: little cycle-life data from real cars 🟢; mostly China for now | Follow the maker's advice; data will build up |
| Semi-solid-state | Emerging, in a few production cars | More energy per kg; NIO already sells a 150 kWh semi-solid pack 🟢 | Premium and rare; limited long-term data | Follow the maker's advice |
| All-solid-state | Future | Promises much more range and very fast charging | As of March 2026, no all-solid-state cells were in cars you can buy 🟢; Toyota plans cars in 2027–28 and BYD small-batch production in 2027 🟢 | — |
| LMR (lithium manganese rich) | Future | Cheaper than NMC with similar range 🟡 | Not in cars yet 🟡 | — |

## Battery cooling

| Type | Pros | Cons |
| --- | --- | --- |
| Liquid / refrigerant | Keeps the battery at the right temperature, so it ages slower and charges faster | None worth noting for buyers |
| Air / passive | Simpler and cheaper | Heats up on fast charging and in hot weather; packs age faster. A key thing to check on used cars 🟡 |
