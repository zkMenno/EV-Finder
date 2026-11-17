Copies of the home-hero scenes from docs/design/assets/Illustrations (UX owns the originals;
re-copy when they change). They live here so the web build bundles them into .next/static
(the Docker image ships no public/ folder). Decorative: rendered with alt="".

Parallax (2026-11-17): `pnpm scenes` (scripts/scenes.mjs) copies the flat scenes and `layers/`
for village, city, highway and canal, and writes src/components/parallax/scenes.generated.ts
from docs/design/assets/Illustrations/layers/manifest.json. Never edit the copies by hand;
src/components/parallax/scenes.test.ts fails when they drift from the design system.
