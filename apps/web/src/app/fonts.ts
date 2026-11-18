// Brand fonts (docs/design/tokens.json "type"): Atkinson Hyperlegible for text and numbers,
// Bitter for headings. Self-hosted through next/font/local: the files are copies of
// docs/design/fonts (OFL, latin subset; src/fonts/README.md), served from our own origin under
// /_next/static/media, so the CSP's font-src 'self' holds and nothing calls a third party.
//
// preload: false on purpose. The landing page and Explore must stay under 200 KB first-load
// (JS ~170 KB gzip); preloading both Atkinson weights would add ~35 KB to every first load.
// display: swap + next/font's size-adjusted fallback face show text at once and keep the
// layout from jumping when the font arrives. The browser fetches only the faces a page uses.
import localFont from "next/font/local";

export const fontText = localFont({
  src: [
    { path: "../fonts/atkinson-hyperlegible-latin-400-normal.woff2", weight: "400", style: "normal" },
    { path: "../fonts/atkinson-hyperlegible-latin-400-italic.woff2", weight: "400", style: "italic" },
    { path: "../fonts/atkinson-hyperlegible-latin-700-normal.woff2", weight: "700", style: "normal" },
  ],
  variable: "--font-text",
  display: "swap",
  preload: false,
  fallback: ["Segoe UI", "system-ui", "-apple-system", "Roboto", "Helvetica Neue", "Arial", "sans-serif"],
});

export const fontDisplay = localFont({
  src: [
    { path: "../fonts/bitter-latin-700-normal.woff2", weight: "700", style: "normal" },
    { path: "../fonts/bitter-latin-800-normal.woff2", weight: "800", style: "normal" },
  ],
  variable: "--font-display",
  display: "swap",
  preload: false,
  fallback: ["Georgia", "serif"],
  adjustFontFallback: "Times New Roman",
});

/** Put on <html> in every root layout: defines --font-text and --font-display. */
export const fontVars = `${fontText.variable} ${fontDisplay.variable}`;
