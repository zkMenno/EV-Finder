// Decision 082 (T-137): English only at launch. Every launch country, Spain and Italy included
// (Decision 066), serves /{country}/en/; the other languages redirect there, are not linked and
// are not in the sitemap or hreflang. The language picker is hidden. Runs on the published release.
import { expect, test } from "@playwright/test";
import { HAS_SCORES, NO_SCORES_REASON } from "./release";
import { COUNTRIES } from "./langs";

const HIDDEN = ["nl", "de", "fr", "es", "it"];

test("T-137: all seven countries: /{country} and every hidden language redirect to /{country}/en", async ({ request }) => {
  expect(COUNTRIES).toEqual(["nl", "de", "fr", "be", "uk", "es", "it"]);
  for (const country of COUNTRIES) {
    const bare = await request.get(`/${country}`, { maxRedirects: 0 });
    expect(bare.status(), `/${country}`).toBe(307);
    expect(bare.headers()["location"], `/${country}`).toMatch(new RegExp(`/${country}/en$`));
    // A remembered language cookie no longer wins: it isn't served.
    const cookie = await request.get(`/${country}`, { maxRedirects: 0, headers: { Cookie: "lang=nl" } });
    expect(cookie.headers()["location"], `/${country} with lang=nl`).toMatch(new RegExp(`/${country}/en$`));
    expect((await request.get(`/${country}/en`)).status(), `/${country}/en`).toBe(200);
    for (const lang of HIDDEN) {
      const cases: [string, string][] = [
        [`/${country}/${lang}`, `/${country}/en`],
        [`/${country}/${lang}/learn/real-range?x=1`, `/${country}/en/learn/real-range?x=1`],
      ];
      for (const [path, to] of cases) {
        const r = await request.get(path, { maxRedirects: 0 });
        expect(r.status(), path).toBe(308);
        expect(r.headers()["location"], path).toMatch(new RegExp(`${to.replace(/[?]/g, "\\?")}$`));
      }
    }
  }
  expect((await request.get("/", { maxRedirects: 0 })).headers()["location"]).toMatch(/\/nl\/en$/);
});

test("T-137: no language picker, no banner, html lang en; the country picker lists all seven", async ({ page }) => {
  await page.context().setExtraHTTPHeaders({ "Accept-Language": "nl-NL,nl" });
  await page.goto("/nl/en");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  const selects = page.locator("header select");
  await expect(selects).toHaveCount(1); // country only
  await expect(page.locator('header select option[value="nl"]')).toHaveCount(1);
  await expect(page.locator('header option[value="en"]')).toHaveCount(0);
  await expect(page.getByTestId("lang-banner")).toHaveCount(0);
  const picker = selects.first();
  await expect(picker.locator("option")).toHaveText([/NL/, /DE/, /FR/, /BE/, /UK/, /ES · España/, /IT · Italia/]);
  await picker.selectOption("es");
  await expect(page).toHaveURL(/\/es\/en$/);
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  // The hero's country question (T-132: answer tiles) opens English pages only.
  await page.getByTestId("hero-q-country").getByText("Italy", { exact: true }).click();
  await expect(page).toHaveURL(/^[^?]*\/it\/en\?q=role$/);
});

test("T-137: no internal link points at a hidden language", async ({ page }) => {
  for (const path of ["/nl/en", "/be/en/learn", "/es/en/learn/real-range", "/it/en/data"]) {
    await page.goto(path);
    const hrefs = await page.locator("a[href^='/']").evaluateAll((els) => els.map((e) => e.getAttribute("href") ?? ""));
    expect(hrefs.length, path).toBeGreaterThan(0);
    expect(hrefs.filter((h) => /^\/[a-z]{2}\/(nl|de|fr|es|it)(\/|\?|$)/.test(h)), path).toEqual([]);
  }
});

test("T-137: hreflang and sitemap carry English only (en-ES, en-IT …)", async ({ page, request }) => {
  await page.goto("/es/en/learn/real-range");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(page.locator('link[rel="alternate"][hreflang="en-ES"]')).toHaveAttribute("href", /\/es\/en\/learn\/real-range$/);
  await expect(page.locator('link[rel="alternate"][hreflang="en-IT"]')).toHaveAttribute("href", /\/it\/en\/learn\/real-range$/);
  for (const tag of ["es-ES", "it-IT", "nl-NL", "de-DE", "fr-FR", "fr-BE", "nl-BE", "de-BE"])
    await expect(page.locator(`link[rel="alternate"][hreflang="${tag}"]`), tag).toHaveCount(0);
  const tags = await page.locator('link[rel="alternate"][hreflang]').evaluateAll((els) => els.map((e) => e.getAttribute("hreflang")));
  expect(tags.sort()).toEqual(["en-BE", "en-DE", "en-ES", "en-FR", "en-GB", "en-IT", "en-NL", "x-default"]);
  const sm = await (await request.get("/sitemap.xml")).text();
  for (const c of COUNTRIES) expect(sm).toContain(`/${c}/en/learn/real-range</loc>`);
  expect(sm).not.toMatch(/\/[a-z]{2}\/(nl|de|fr|es|it)(\/|<)/);
});

// Spain and Italy work in English: a hero walk at two budgets, euro prices, no raw keys.
for (const country of ["es", "it"]) {
  for (const budget of [20000, 40000]) {
    test(`T-137: hero walk ${country}/en at €${budget}`, async ({ page }) => {
      test.skip(!HAS_SCORES, NO_SCORES_REASON);
      await page.setViewportSize({ width: 360, height: 800 });
      await page.goto(`/${country}/en?role=only&trips=monthly&budget=${budget}`);
      await expect(page.locator("html")).toHaveAttribute("lang", "en");
      await expect(page.getByTestId("hero-card").first()).toBeVisible();
      await expect(page.getByTestId("hero-summary")).toContainText(`up to €${budget.toLocaleString("en")}`);
      const text = await page.getByTestId("hero").innerText();
      expect(text).not.toMatch(/\bhero\.[a-z]/); // no raw dictionary keys
      expect(text).not.toMatch(/£/);
      expect(text).toMatch(/€/);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow).toBeLessThanOrEqual(0);
    });
  }
}
