# ShortlistButton

The toggle that puts a car on your shortlist. Tapping it draws the tick-road into the empty box and drops the sunflower disc on the end.

- A toggle button with `aria-pressed`. Off: "Add to shortlist", empty rounded box. On: "On your shortlist", the tick-road, `sunflower-tint` background.
- Motion: the road draws on in 260ms, then the disc pops in (180ms, slight overshoot) after 200ms. Turning it off reverses. Reduced motion shows the end state at once.
- Icon-only version (`evs-pick--icon`, 48px) on car cards and table rows, with an aria-label naming the car: "Add Kia e-Niro to shortlist".
- Toast after adding: "Added to your shortlist", with an Undo link. After removing: "Removed from your shortlist", with Undo.
- The tick replaces the heart everywhere. There are no separate favourites: the shortlist is the one place cars are kept.
