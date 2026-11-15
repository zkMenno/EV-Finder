# Texture

Holiday-map surface textures: paper grain, contour lines, a map grid, land hatching, a halftone sun and map folds, plus a dotted route divider.

- Add `evs-tex` plus one modifier to a wrapper: `evs-tex--paper`, `--contour`, `--grid`, `--hatch`, `--halftone`, `--fold`. The texture sits behind the content (a pseudo-element at z-index −1), so text stays crisp. To stack two, nest two wrappers.
- Every texture has a dark-theme version and stays faint: 5–14% ink, so text contrast on the surface is unchanged.
- **Where:** hero bands, empty states, /learn headers and illustrations, the footer, share images, the taped note's map. Up to two textures per view.
- **Never:** behind tables, forms, prices, specs or long body copy; never on buttons or chips.
- Pairings: hero = paper + contour; empty state = paper; learn header = grid; land in illustrations = hatch; sun = halftone; folded-map moments (share image, 404) = fold.
- `evs-route-divider` separates big page sections: a dotted sky route ending at the sun. One or two per page, never between list items.
- Pure CSS and inline SVG; nothing to download. Standalone SVG tiles live in the Textures asset group for designers.
