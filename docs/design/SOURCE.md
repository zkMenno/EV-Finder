# Where this comes from

Design board with mockups, logo sheet, elements, icons and textures: https://claude.ai/artifact/7oaYaK26i6xQBogFuuctMp (visual reference; this folder stays the source of truth for values and rules).

This folder mirrors the EV Shortlist design system: https://claude.ai/artifact/EiqvMW5NcFgxFq6c5YHuPP

- Owner: UX workstream (`workstreams/UX/`). Other lanes: don't edit here; write to `workstreams/WS0/INBOX.md`.
- For builders, this repo copy is the one to read. Start with `README.md`, then `patterns.md`, then `components/<Name>/README.md`.
- `tokens.json` is the token source (Design System format: lists of `{name, value, usage}`, colours per theme `light`/`dark`). Generate CSS custom properties from it: `:root, [data-theme="light"]` and `[data-theme="dark"]` blocks, plus `--font-display`, `--font-text`, `--font-hand` and the spacing, radius and size tokens.
- `components/bundle.css` is real, usable CSS (class prefix `evs-`), and `components/*/preview.html` are reference markups (they assume tokens.css and bundle.css are loaded).
- `fonts/` holds the self-hosted OFL fonts (latin subset). `assets/Logo/`, `assets/Symbols/`, `assets/Textures/` and `assets/Illustrations/` hold the SVGs.
- The brand name comes from config (`brand.name`, Decision 018). The logo SVGs say "EV Shortlist"; swap them if the name changes.

Last synced: 2026-11-15 (design system v6: solarpunk illustrations, village + city scenes, 10 illustration colours, hero "Used EVs got good.").
