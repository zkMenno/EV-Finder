# Symbols

Map symbols for the interface, on a 24px grid with a 2px ink line (`ink` #16233A in the files) and round caps. Each has at most one flat fill from the palette.

| File | Means |
|---|---|
| home-pin.svg | Your town: the start of the range route |
| flag.svg | A place the car reaches |
| charge-stop.svg | An estimated charge stop (sunflower) |
| voltage-400.svg, voltage-800.svg, voltage-900.svg | Charging voltage class: one, two or three bolts |
| chemistry.svg | Battery chemistry (battery with a leaf) |
| air-cooled.svg | Air-cooled pack, a caution on used cars (battery with a fan) |
| compass.svg | Learn and guides |
| folded-map.svg | Explore |

The ink is baked in as #22335A because images can't inherit colour. For dark mode and inline use in the app, inline the SVG and swap the stroke for `currentColor`, which then follows `ink`. Pair every symbol with a text label; never use one as the only signal.
