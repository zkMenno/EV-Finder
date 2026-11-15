# Texture

Holiday-map surface textures: paper grain, contour lines, a map grid, land hatching, a halftone sun and map folds, plus a dotted route divider.

- **Default (Menno, 2026-11-15): every plain coloured background gets the travel-map texture (map print + landscape).** Hero bands, section bands on `paper-sea`, tips and callouts on `sunflower-tint`, empty states on `meadow-tint` or `paper-sea`, the footer: `evs-tex evs-tex--map` (left-aligned content: contours on the right edge and a bottom strip) or `evs-tex evs-tex--map-frame` (centred content: both side edges and a bottom strip). Paper grain covers the whole surface; contour lines stay at the edge(s); a strip of soft hills with a dotted sky route runs along the bottom (the class reserves 88px bottom padding, 68px on phones); a small sun sits in the top-right corner. Add `evs-tex--no-sun` when the block already shows an illustration with its own sun (hero, empty state). Nothing runs behind text. Not on white cards, tables, forms, buttons, chips or status tints (danger, success, warning).
- Add `evs-tex` plus one modifier to a wrapper: `evs-tex--paper`, `--contour`, `--grid`, `--hatch`, `--halftone`, `--fold`. The texture sits behind the content (a pseudo-element at z-index −1), so text stays crisp. To stack two, nest two wrappers.
- Every texture has a dark-theme version and stays faint: 5–14% ink, so text contrast on the surface is unchanged.
- **Where:** hero bands, empty states, /learn headers and illustrations, the footer, share images, the taped note's map. Up to two textures per view.
- **Never:** behind tables, forms, prices, specs or long body copy; never on buttons or chips.
- Pairings: hero = map; empty state = map-frame; tip/callout = map; learn header = grid; land in illustrations = hatch; sun = halftone; folded-map moments (share image, 404) = fold.
- `evs-route-divider` separates big page sections: a dotted sky route ending at the sun. One or two per page, never between list items.
- Pure CSS and inline SVG; nothing to download. Standalone SVG tiles live in the Textures asset group for designers.
