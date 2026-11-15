# Where this comes from

This folder mirrors the EV Shortlist design system: https://claude.ai/artifact/EiqvMW5NcFgxFq6c5YHuPP

- Owner: UX workstream (`workstreams/UX/`). Other lanes: don't edit here; write to `workstreams/UX/INBOX.md`.
- For builders, this repo copy is the one to read. Start with `README.md`, then `patterns.md`, then `components/<Name>/README.md`.
- `tokens.json` is the token source (Design System format: lists of `{name, value, usage}`, colours per theme `light`/`dark`). Generate CSS custom properties from it: `:root, [data-theme="light"]` and `[data-theme="dark"]` blocks, plus `--font-display`, `--font-text`, `--font-hand` and the spacing, radius and size tokens.
- `components/bundle.css` is real, usable CSS (class prefix `evs-`), and `components/*/preview.html` are reference markups (they assume tokens.css and bundle.css are loaded).
- `fonts/` holds the self-hosted OFL fonts (latin subset). `assets/Logo/` and `assets/Symbols/` hold the SVGs.
- The brand name comes from config (`brand.name`, Decision 018). The logo SVGs say "EV Shortlist"; swap them if the name changes.

Last synced: 2026-11-15 (design system v3: road-sign plate logo).
