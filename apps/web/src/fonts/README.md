# Brand fonts (self-hosted)

Byte-for-byte copies of `docs/design/fonts/` (UX owns those; `src/app/fonts.test.ts` fails when
they drift). Loaded by `src/app/fonts.ts` through `next/font/local`.

| File | Family | Licence |
|---|---|---|
| atkinson-hyperlegible-latin-400-normal / 400-italic / 700-normal | Atkinson Hyperlegible (Braille Institute) | SIL Open Font License 1.1 |
| bitter-latin-700-normal / 800-normal | Bitter (Huerta Tipográfica) | SIL Open Font License 1.1 |

Latin subset (Fontsource builds): covers English, € and the other launch-country names. Add
latin-ext before launching in Central Europe or Türkiye (docs/design/README.md).
