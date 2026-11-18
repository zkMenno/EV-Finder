# Brand fonts (self-hosted)

Byte-for-byte copies of `docs/design/fonts/` (UX owns those; `src/app/fonts.test.ts` fails when
they drift). Loaded by `src/app/fonts.ts` through `next/font/local`.

| File | Family | Licence |
|---|---|---|
| atkinson-hyperlegible-latin-400-normal / 400-italic / 700-normal | Atkinson Hyperlegible (Braille Institute) | SIL Open Font License 1.1: `OFL-AtkinsonHyperlegible.txt` |
| bitter-latin-700-normal / 800-normal | Bitter (The Bitter Project Authors) | SIL Open Font License 1.1: `OFL-Bitter.txt` |

Latin subset (Fontsource builds): covers English, € and the other launch-country names. Add
latin-ext before launching in Central Europe or Türkiye (docs/design/README.md).

The OFL texts are verbatim from github.com/google/fonts (`ofl/atkinsonhyperlegible/OFL.txt`, `ofl/bitter/OFL.txt`); OFL §2 asks for the copyright notice and the licence with every copy.
