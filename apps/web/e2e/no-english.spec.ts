import { readFileSync } from "node:fs";
import { expect, test, type Page } from "@playwright/test";

type Dict = Record<string, string>;
const dict = (lang: string): Dict =>
  JSON.parse(readFileSync(new URL(`../src/i18n/${lang}.json`, import.meta.url), "utf8")) as Dict;
const en = dict("en");

// Taxonomy text (glossary labels and tooltips, chemistries, cooling, voltage classes) comes from
// the published data release, not from the dictionaries. Release 1 was built when the taxonomy
// had EN + NL only, so that text stays English on DE/FR pages until the next release is built
// (Q-070; T-117 added the DE/FR/ES/IT glossary drafts to data/taxonomy/glossary_terms.yaml).
// It is removed from the page text before the dictionary check and reported as an annotation.
const RELEASES = new URL("../../../data/releases/", import.meta.url);
const latest = readFileSync(new URL("latest", RELEASES), "utf8").trim();
const catalogue = JSON.parse(
  readFileSync(new URL(`${latest}/catalogue.json`, RELEASES), "utf8"),
) as { taxonomy?: unknown };
function enStrings(x: unknown, out: Set<string>): Set<string> {
  if (Array.isArray(x)) x.forEach((v) => enStrings(v, out));
  else if (x && typeof x === "object") {
    const o = x as Record<string, unknown>;
    if (typeof o.en === "string" && o.en.length > 3) out.add(o.en);
    Object.values(o).forEach((v) => enStrings(v, out));
  }
  return out;
}
const TAXONOMY_EN = [...enStrings(catalogue.taxonomy, new Set())].sort(
  (a, b) => b.length - a.length,
);

// T-117 (A-35 B5): German and French pages show no English UI strings. The check uses the
// dictionaries themselves: every public English string that the target language translates
// differently must not appear in the page's visible text or its aria-labels. Brand and model
// names, units and codes are never dictionary strings, so they pass on their own; the allow-list
// below covers English UI words that also occur inside car names.

const PAGES = [
  { name: "hero, Explore and footer", path: "" },
  { name: "generation page", path: "/ev/hyundai/ioniq-5/gen1" },
  { name: "variant page", path: "/ev/audi/e-tron/ge/s" },
  { name: "compare page", path: "/compare?ids=audi-e-tron-ge-s,renault-zoe-ph1-r240" },
];

// English dictionary strings that may appear because they are part of a car or trim name.
const ALLOWED = new Set(["Performance", "Range", "Variant"]);

/** Literal pieces of an English string worth searching for (placeholders split it). */
function needles(enDict: Dict, target: Dict): Map<string, string> {
  const out = new Map<string, string>();
  for (const [key, value] of Object.entries(enDict)) {
    if (key.startsWith("staff.") || key.startsWith("_")) continue;
    if (target[key] === value) continue; // same word in both languages (SUV, Coupé, WLTP…)
    for (const raw of value.split(/\{\w+\}/)) {
      const piece = raw.trim().replace(/^[\s·:;,.()–-]+|[\s·:;,.()–-]+$/g, "");
      // Needs real words: at least 4 letters, not a unit or a code.
      if ((piece.match(/[A-Za-z]/g) ?? []).length < 4) continue;
      if (ALLOWED.has(piece)) continue;
      if (Object.values(target).some((v) => v.includes(piece))) continue; // the translation uses it too
      if (!out.has(piece)) out.set(piece, key);
    }
  }
  return out;
}

const escape = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

async function pageText(page: Page): Promise<string> {
  const visible = await page.locator("body").innerText();
  const labels = await page.$$eval("[aria-label]", (els) =>
    els.map((e) => e.getAttribute("aria-label") ?? ""),
  );
  return `${visible}\n${labels.join("\n")}`;
}

for (const lang of ["de", "fr"] as const) {
  const search = needles(en, dict(lang));
  test.describe(`${lang} pages`, () => {
    // A German or French reader's browser: no "also available in English" banner.
    test.use({ locale: `${lang}-${lang.toUpperCase()}` });
    for (const pg of PAGES) {
      test(`/${lang}/${lang} ${pg.name} shows no English UI strings`, async ({ page }) => {
        const res = await page.goto(`/${lang}/${lang}${pg.path}`);
        expect(res?.status(), "page loads").toBeLessThan(400);
        await expect(page.locator("html")).toHaveAttribute("lang", lang);
        await page.waitForLoadState("networkidle");
        let text = await pageText(page);
        const fromRelease = TAXONOMY_EN.filter((s) => text.includes(s));
        for (const s of fromRelease) text = text.split(s).join("\n");
        test
          .info()
          .annotations.push({
            type: "taxonomy text from the data release (EN until rebuilt)",
            description: String(fromRelease.length),
          });
        const found: string[] = [];
        for (const [piece, key] of search) {
          if (new RegExp(`(^|[^A-Za-z])${escape(piece)}([^A-Za-z]|$)`).test(text))
            found.push(`${key}: "${piece}"`);
        }
        expect(found, "English UI strings on the page").toEqual([]);
      });
    }
  });
}
