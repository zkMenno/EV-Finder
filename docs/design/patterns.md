# Page and interaction patterns

How the main screens are put together. Components are linked by name; they are documented one by one under Components.

## Global frame

- **Header (desktop):** logo left, then Explore, Rankings, Learn, Charging; search; the detail switch; the Shortlist button with its sunflower count badge, then sign in. Header and footer take `paper`, and the hero band takes `paper-sea`.
- **Tab bar (phones):** Explore, Compare, Shortlist (tick icon + badge), Learn, fixed at the bottom and 60px high. Search sits at the top of Explore, not in the tab bar.
- **Shortlist tray:** docked above the tab bar on phones and bottom-right on desktop. It is the shortlist itself (up to 12 cars); Compare takes up to 4 at a time. It never resets, even across sessions.
- **Footer:** sources and licences (CC BY 4.0 data, AGPL code), languages, "Report a data issue", about. Ink on `paper-sea`, with a small hand-drawn coastline as the only decoration.

## Explore (landing page)

```
[ Hero, paper-sea: "Compare EVs. Make your shortlist." + town input + "Show cars" | taped shortlist note ]
[ filters (chips row on phones, side panel ≥1024px) ][ table / cards toggle ][ detail switch ]
[ Explore table: name | used price range | new price | real range | charge 10–80% | ... ]
[ shortlist tray ]
```

- The table is the default from 768px up, and cards are the default on phones. The toggle is remembered.
- The first column (the car) is sticky when scrolling sideways. The header row is sticky when scrolling down.
- Sort by tapping a header, with an arrow and `aria-sort`. Filters show a count ("12 filters, 214 cars") and one "Clear filters".
- Simple mode shows 5 columns, Detailed 9 and Nerd all of them. The columns add on the right, so nothing jumps.

## Car page (model generation)

```
[ breadcrumb ]  [ h1 car + years ]  [ Add to shortlist ]
[ money block: used price range, monthly cost vs petrol (number style), "See listings" primary ]
[ range route map ]
[ charging: km in 20 min, minutes 10–80%, 400 V / 800 V symbol, "fast on older chargers" ]
[ battery: chemistry, cooling, health checks (Aviloo, Car-Pass) ]
[ known issues (inspection data) ]  [ versions table ]  [ sources (Nerd: expanded) ]
```

- "See listings" is the one primary action. It opens the marketplace search in a new tab, with an external-link icon and the site name ("See listings on AutoScout24").
- Every number has a plain label, the technical term underneath and an ⓘ legend.
- Caution chips (air-cooled pack, single source, estimate) sit right next to the number they qualify.

## Compare

- Up to 4 cars side by side. Rows follow the car page order: money, range, charging, battery, issues.
- The best value in a row gets a sunflower-tint cell plus the word "Best". Never colour alone.
- On phones, two cars at a time with a swipe between pairs, and the first column stays sticky.

## Shortlist page

```
[ ShortlistNote header: "My shortlist", picked and ruled-out cars with your reasons ]
[ Compare 3 cars (primary) ] [ Share your shortlist ] [ sort: your order | price | range ]
[ CarCards in your order, drag handle + "Move up / Move down" buttons, your note under each ]
[ Ruled out (collapsed): struck-through cards with the reason ]
```

- The order is yours (drag, or the Move buttons for keyboard and touch), so the numbers 1, 2, 3 are real ranks.
- Each card has a note field, "Why this one?". Your words appear on the taped note.
- Suggested reasons from our data ("air-cooled battery") are offered as chips you can add, labelled "from our data".
- Share makes a read-only link and a share image: the taped note on the map, with the lockup.

## Learn

- Reading layout: body-lg, 68ch measure, headings in Bitter.
- This is where doodles live: a small illustration per article (a car on a road, a charge stop, a battery cutaway) in the map palette.

## Menus and popovers

- One floating layer at a time: the legend tooltip, a dropdown menu or the language picker.
- Open on click or tap, not hover alone. Close on Escape, on an outside tap or on reselect. Focus moves in and returns to the trigger.
- Menus use `surface`, a 1.5px ink border, `radius-md` and `shadow-lift`. Items are 48px high with an ink-2 icon on the left.

## Buttons

- **Primary** (`action` fill): one per view. "See listings", "Show cars", "Save shortlist".
- **Secondary** (outlined): everything else that matters. "Share your shortlist", "Rule out". "Add to shortlist" is its own toggle (ShortlistButton).
- **Ghost** (link style): low-stakes actions. "Clear filters", "Read more".
- An icon sits only before a label, never alone without an aria-label. External links get the external-link icon after the label.
- No disabled buttons. Keep them active and explain on press: "Add a car first, then compare."

## Interaction states

| State | Treatment |
|---|---|
| Hover | Background shifts one step (`paper-sea` on rows, `action-hover` on primary) |
| Focus | 3px `focus` outline, 2px offset, on every control |
| Pressed | 1px down, no colour flash |
| Selected | `aria-pressed` or `aria-current`, a sunflower or sky underline plus bold text |
| Loading | A skeleton in `surface-sunk` for tables; "Finding cars…" in text for long waits |
| Error | `danger-tint` panel, icon, what happened, what to do |
| Empty | An illustration, one sentence, one action |

## Forms and filters

- Labels always above the field, never placeholder-only. Hints in ink-3 under the field.
- Range sliders always show the value as text next to them, and there is always a typed input as an alternative.
- Errors appear under the field on blur or submit, never while typing.
