// T-119 (Decision 066): Spain and Italy are served at /es/es and /it/it (+ English), and Spanish
// and Italian appear for those two countries only. Runs on the published release like the others.
import { expect, test } from "@playwright/test";

const ROUTES = [
  { country: "es", lang: "es", name: "España" },
  { country: "it", lang: "it", name: "Italia" },
] as const;

test("ES/IT: /es and /it land on their own language; ES/IT never show up under other countries", async ({ request }) => {
  for (const { country, lang } of ROUTES) {
    const bare = await request.get(`/${country}`, { maxRedirects: 0 });
    expect(bare.status()).toBe(307);
    expect(bare.headers()["location"]).toMatch(new RegExp(`/${country}/${lang}$`));
    expect((await request.get(`/${country}/${lang}`)).status()).toBe(200);
    expect((await request.get(`/${country}/en`)).status()).toBe(200);
  }
  // Decision 066: no /nl/es style routes; an unserved language redirects to the country default.
  const unserved: [string, string][] = [["/nl/es", "/nl/nl"], ["/de/it", "/de/de"], ["/es/it", "/es/es"], ["/it/es", "/it/it"], ["/uk/es", "/uk/en"]];
  for (const [path, to] of unserved) {
    const r = await request.get(path, { maxRedirects: 0 });
    expect(r.status(), path).toBe(308);
    expect(r.headers()["location"], path).toMatch(new RegExp(`${to}$`));
  }
});

test("ES/IT: the country picker lists Spain and Italy and switches to their language", async ({ page }) => {
  await page.goto("/nl/nl");
  const picker = page.locator("header select").filter({ has: page.locator('option[value="es"]') });
  await expect(picker.locator("option")).toHaveText([/NL/, /DE/, /FR/, /BE/, /UK/, /ES · España/, /IT · Italia/]);
  await picker.selectOption("es");
  await expect(page).toHaveURL(/\/es\/es$/);
  await expect(page.locator("html")).toHaveAttribute("lang", "es");
  // The hero's country step lists them too.
  await expect(page.getByTestId("hero-countries").getByRole("link", { name: "Italia" })).toHaveAttribute("href", /^\/it\/it/);
});

test("ES/IT: hreflang and sitemap carry es-ES and it-IT, and no Spanish or Italian elsewhere", async ({ page, request }) => {
  await page.goto("/es/es/learn/real-range");
  await expect(page.locator("html")).toHaveAttribute("lang", "es");
  await expect(page.locator('link[rel="alternate"][hreflang="es-ES"]')).toHaveAttribute("href", /\/es\/es\/learn\/real-range$/);
  await expect(page.locator('link[rel="alternate"][hreflang="it-IT"]')).toHaveAttribute("href", /\/it\/it\/learn\/real-range$/);
  await expect(page.locator('link[rel="alternate"][hreflang="en-ES"]')).toHaveAttribute("href", /\/es\/en\/learn\/real-range$/);
  await expect(page.locator('link[rel="alternate"][hreflang^="es-"]')).toHaveCount(1);
  await expect(page.locator('link[rel="alternate"][hreflang^="it-"]')).toHaveCount(1);
  const sm = await (await request.get("/sitemap.xml")).text();
  for (const p of ["/es/es/learn/real-range</loc>", "/it/it/learn/real-range</loc>", "/es/en/learn</loc>", "/it/en/learn</loc>"]) expect(sm).toContain(p);
  for (const p of ["/nl/es/", "/nl/it/", "/be/es/", "/fr/it/", "/es/it/", "/it/es/"]) expect(sm).not.toContain(p);
});

// Acceptance: a hero walk for ES and IT at two budgets, in their own language, euro prices.
for (const { country, lang } of ROUTES) {
  for (const budget of [20000, 40000]) {
    test(`ES/IT: hero walk ${country}/${lang} at €${budget}`, async ({ page }) => {
      await page.setViewportSize({ width: 360, height: 800 });
      await page.goto(`/${country}/${lang}?role=only&trips=monthly&budget=${budget}`);
      await expect(page.locator("html")).toHaveAttribute("lang", lang);
      await expect(page.getByTestId("hero-card").first()).toBeVisible();
      await expect(page.getByTestId(`hero-budget-${budget}`)).toHaveAttribute("aria-pressed", "true");
      const text = await page.getByTestId("hero").innerText();
      expect(text).not.toMatch(/\bhero\.[a-z]/); // no raw dictionary keys
      expect(text).not.toMatch(/£/);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow).toBeLessThanOrEqual(0);
    });
  }
}
