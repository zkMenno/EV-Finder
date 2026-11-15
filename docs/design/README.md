# EV Shortlist

Compare EVs. Make your shortlist.

The design system for EV Shortlist (working title), a site for comparing used and new electric cars and keeping the ones that fit. It looks like an illustrated holiday map with a hand-kept list taped to it: friendly and fun on the outside, calm and exact wherever someone is deciding how to spend €15,000.

**Design board** (mockups, logo sheet, elements, icons, textures): https://claude.ai/artifact/7oaYaK26i6xQBogFuuctMp. The board shows the system in use and installs this system's tokens; this system is the source of truth for values and rules. When one changes, update the other.

Builders: read this page first, then `patterns.md`, then the component guidelines. Use tokens through CSS custom properties (`var(--ink)`) and the `evs-` classes in `components/bundle.css`. Never paste hex values into app code. Fonts are self-hosted in `fonts/` (OFL), latin subset; add latin-ext before launching in Türkiye or Central Europe.

## The idea in one line

**Every car you pick becomes a stop on your trip.** The brand joins two things people already understand: ticking items off a shortlist, and planning a road trip on a map. In the logo, the whole "EV" is one sky-blue shape whose V is a tick, winding and narrowing like a road towards a sunflower sun on the horizon. That sun means "chosen" everywhere: the end of the tick, the shortlist badge, charge stops, the selected detail level.

| Brand device | Where it lives | What it says |
|---|---|---|
| EV with a winding tick for a V | Logo, icon | Picked, and the road it opens up |
| S-road (winding S with start pin and disc) | Illustrations, loading states, share image | The journey from all EVs to your shortlist |
| Tick-road | ShortlistButton, tray, the taped note | "Picked": a tick drawn as a road |
| Sunflower disc | End of the logo tick, icon, count badge, charge stops, switch underline | Chosen, a place to stop |
| Taped note | Hero, shortlist page header, share images | Your own list, in your own words |
| Pen strike | Ruled-out cars on the note | Honest: we help you say no too |
| Range route | Car pages | Range as a journey to real places |

## Who it is for

- People aged 30 to 70. Most are buying their first EV, and some have driven EVs for 5 to 10 years.
- First-timers worry about range, charging, battery health and the price gap. A used EV starts at €10–15k, where an old petrol car costs €2–4k.
- Veterans want the real numbers: charging curves, voltage class, chemistry, sources.

The product promise is that a used EV is cheaper to live with, and that we prove it with honest numbers. The shortlist is how people get from "all EVs" to "the three I’ll test-drive". The design has to make that feel obvious, trustworthy and a little bit fun.

## Principles

1. **Fun in the margins, calm in the middle.** Doodles, map notes and the route line live in heroes, empty states, /learn pages and the range map. Tables, prices, forms and specs are clean and sharp: no hand-drawn type, no wobble, no decoration.
2. **Money first, honestly.** Lead with what a car costs per month to own compared with petrol, then range, then charging. Show ranges, not falsely exact single prices. Mark estimates as estimates.
3. **Simple by default, nerdy on demand.** Every figure has a plain label with the technical term underneath and an ⓘ legend. The Simple / Detailed / Nerd switch adds depth without changing the layout people have learned.
4. **Readable for everyone.** Body text is 17px and nothing a buyer reads is smaller than 14px. Tap targets are at least 48px. Contrast is AA or better in both themes. Colour never carries meaning alone: there is always a word or an icon too.
5. **Range is a journey, not a number.** Wherever range matters, draw it as a route to real places (see Range route).

## Voice: a knowledgeable neighbour

The neighbour who has had an EV for years, knows cars, and tells you the truth over the fence.

- Plain words first: "Real range in winter", with "WLTP combined" underneath as the technical term.
- Honest about downsides: "Air-cooled battery. It wears faster in hot climates, so check its health report."
- Specific beats clever: "Reaches Bordeaux, one charge stop to Toulouse", not "Go further".
- Sentence case everywhere. Contractions are fine. No exclamation marks in the interface.
- Buttons say what happens: "See listings", "Add to shortlist", "Compare 3 cars". The toast then echoes the verb: "Added to your shortlist".
- Errors say what happened and what to do: "We couldn't find that town. Try a nearby city."
- Empty states invite: "Your shortlist is empty. Tap “Add to shortlist” on any car to keep it here."
- Never: "game-changer", "seamless", "unlock", "simply", "just", "easy".
- Six languages (EN, NL, DE, FR, ES, IT). German and Dutch run about 30% longer, so labels and buttons must wrap or grow, never truncate.

## Shortlist vocabulary

One set of words, everywhere, in all six languages.

| Action or state | Words |
|---|---|
| Toggle off | Add to shortlist |
| Toggle on | On your shortlist |
| Toast | Added to your shortlist (Undo) / Removed from your shortlist (Undo) |
| Page and tab | Shortlist (count badge) |
| Comparing | Compare 3 cars |
| Ruling out | Rule out (the car stays visible, struck through, with your reason) |
| Sharing | Share your shortlist |

Never "favourites", "saved", "wishlist" or a heart. Translators: keep "shortlist" as one concept and decide each language's word once in the glossary table (NL can keep "shortlist"; DE and FR need a choice).

## Colour

The palette is Ink and sky: deep ink for text and linework, a calm sky blue for the brand and routes, sunflower for anything chosen, with meadow and sea tints for the holiday-map illustrations, all on white paper. It deliberately avoids the electric blue, lime green and lightning bolts most EV brands use. Two themes: Day trip (light) and Night drive (dark). Every token has both.

| Role | Token | Rule |
|---|---|---|
| Page | `paper`, `paper-sea` | White sheet; the sea tint for hero bands and alternate sections |
| Text | `ink`, `ink-2`, `ink-3` | Primary, secondary (the technical term), captions and sources |
| Brand | `sky` | The EV and tick in the logo, route lines, pen strikes, large shapes. White on it passes 4.7:1; buttons use the darker `action` |
| Action | `action` + `on-action` | The one primary button per view |
| Chosen | `sunflower`, `sunflower-tint`, `on-sunflower` | The disc: logo dot, shortlist badge, charge stops, selected states, money chips |
| Land and sea | `meadow`, `sea` | Illustration and map only. Meadow is never text |
| Status | `success`, `warning`, `danger` (+ tints) | Always with an icon or a word. Danger is berry, so errors never look like the brand or a button |
| Links and focus | `link`, `focus` | Underlined links; a 3px focus outline on everything |

Contrast checked (WCAG): ink on paper 12.4:1 (light) and 15:1 (dark); action with on-action 4.8:1 and 7.4:1; ink-3 on surface-sunk 4.6:1 or better; line-strong against paper 3.1:1 and 3.3:1 for control borders.

Charts use `chart-1` to `chart-4` (provisional), and never more than four series. Beyond that, use small multiples.

## Type

- **Bitter** (logo and headings). A sturdy contemporary slab serif: it reads as dependable and honest, like a good guidebook, while its warm, rounded details keep it approachable. Weights 700 and 800.
- **Atkinson Hyperlegible** (everything people read and compare). Designed by the Braille Institute for low-vision readers, with clearly different 1/l/I and 0/O shapes. That matters for prices, kWh and kW. Always use tabular numerals.
- **Patrick Hand** (notes only). The shortlist note, labels on the range map, illustrations and empty states. Never for data, buttons, prices or anything someone must read to decide.

All three are OFL-licensed and self-hosted in `fonts/` (tokens.css declares them). The logo is outlined, so it never depends on a font loading. The scale runs from `caption` (14px) through `body` (17px) to `display` (48px); see Typography.

## Layout

- Mobile first. The phone layout is the main one, because many buyers browse listings on the sofa.
- Content max width is 1240px, and the Explore table may break out to 1440px. Reading text stops at 68 characters a line.
- Spacing comes from the 8-step scale (`space-1` 4px to `space-8` 72px). Use 16px gutters on phones and 32px on desktop.
- **Breathing room (rule).** A background, tile, chip, badge or button never touches or crowds its text or mark. Minimum padding: half the cap height of the text inside it on every side, more on tiles and icons (the app icon keeps the logo within its middle 55%). If something has to be smaller, shrink the content, never the padding.
- Left-aligned text. Numbers in tables are right-aligned. Centre only empty states and the hero.
- Radius signals hierarchy: chips and inputs are small (6px), buttons and tooltips medium (10px), cards and the map large (18px), pins and the switch thumb round.
- Elevation is a sticker: a short, solid 2px ink shadow (`shadow-sticker`). Only one floating layer at a time (`shadow-lift`: tooltip, menu, shortlist tray or the taped note).

## Texture

The map is not flat. Faint surface textures give heroes, empty states, Learn headers and illustrations a printed, holiday-map feel: paper grain, contour lines, a map grid, land hatching, a halftone sun and map folds, plus a dotted route divider between big sections. They sit behind content at 5–14% ink and never go behind tables, forms, prices or body copy. Classes: `evs-tex evs-tex--paper` (etc.); see the Texture component.

## Map vocabulary (iconography)

The icons are map symbols, drawn with a 2px ink line and round caps on a 24px grid, with one flat colour fill at most. The full set of 35 is in the Symbols asset group and on the design board.

| Symbol | Means |
|---|---|
| Home pin | Your town, the start of the range route |
| Flag | A place the car reaches |
| Sunflower square with a bolt | A charge stop |
| Tick-road (small mark) | Shortlist |
| Two bolts / three bolts | 400 V / 800 V+ charging |
| Battery with a leaf | Battery chemistry |
| Battery with a fan | Air-cooled pack (a caution on used cars) |
| Compass | /learn and guides |
| Folded map | Explore |

The ⓘ legend is the glossary: it is styled as a map legend box, with the symbol, plain name, one or two sentences, and a "Read more" link to /learn.

## Range route (signature)

Every car page draws its real range as a route from the visitor's town to real places. A solid sky line shows summer range, and a dotted ink line shows winter range. Sunflower squares mark estimated charge stops, and handwritten notes name the places: "Bordeaux, no stop needed".

- The start town comes from a typed place or the country's capital. Never use geolocation without asking.
- Charge stops are estimates from real range and typical motorway charger spacing. We hold no charger map and no point-level charger data, so "Plan this trip properly" hands off to ABRP with the car pre-selected.
- Under the map sits a plain legend in Atkinson: summer km, winter km, the source and the date. The drawing is the delight, and the numbers stay readable without it.
- In Nerd mode, the map adds the conditions of each source test.

## Motion

Motion answers what people do and is quiet otherwise.

- Fast and small: 120–200ms, ease-out, opacity and transform only.
- Adding to the shortlist: the tick-road draws itself into the box (260ms) and the sunflower disc pops on (180ms). The car's chip slides into the tray (200ms). The tray never resets.
- The home hero has the page's one orchestrated moment: the route draws, then the note settles.
- The range route draws its line once, on first view (600ms), then stays still. With reduced motion, it appears drawn.
- No parallax, no scroll-triggered fades, no looping animations near prices.
- `prefers-reduced-motion` turns off all transitions.

## Accessibility checklist

- Text at 4.5:1, and large text, icons, control borders and focus rings at 3:1, in both themes.
- Targets of 48px or more (`tap-target`). Visible focus everywhere.
- Every chart and map has a text equivalent (the legend under the range map, a table behind every chart).
- Meaning never depends on colour alone. Quality tiers, cautions and faults carry an icon and a word.
- Works at 200% zoom and with 6 languages, without cutting off text.

## Don't

- No hand-drawn type or wobbly lines inside tables, prices, forms or specs.
- No stock photos of people plugging in cars, and no leaves on everything.
- No hearts, stars or "favourites": the tick is the only keep-this symbol.
- No green-for-good, red-for-bad without words. No blue-purple gradients, no glow.
- No more than one primary button per view.
- No peak kW shown alone (see the product decision on charging numbers).
