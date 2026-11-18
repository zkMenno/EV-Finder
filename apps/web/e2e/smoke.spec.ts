import { expect, test } from "@playwright/test";

test("Explore (/cars, T-130): filter, add 2 to compare, reload, tray keeps 2", async ({ page, baseURL }) => {
  const origin = new URL(baseURL!).origin;
  const foreign: string[] = [];
  page.on("request", (req) => {
    const u = req.url();
    if (!u.startsWith(origin) && !u.startsWith("data:")) foreign.push(u);
  });

  await page.goto("/nl/nl/cars?view=table");
  // Server-rendered rows are there before the client takes over.
  await expect(page.getByTestId("explore-row").first()).toBeVisible();
  // Full list fetched from our own origin.
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  const shown = async () => Number((await page.getByTestId("result-count").innerText()).match(/\d+/)![0]);
  const before = await shown();

  // Apply a filter: min real range 300 km.
  await page.locator("#f-rangeMin").fill("300");
  await expect(page).toHaveURL(/[?&]range=300/);
  await expect.poll(shown).toBeLessThan(before);

  // Add two cars to compare.
  const toggles = page.getByTestId("compare-toggle");
  await toggles.nth(0).click();
  await toggles.nth(1).click();
  const tray = page.getByTestId("compare-tray");
  await expect(tray.getByRole("listitem")).toHaveCount(2);

  // Reload: filter (URL) and tray (localStorage) both survive.
  await page.reload();
  await expect(page.locator("#f-rangeMin")).toHaveValue("300");
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);
  await expect(page.getByTestId("compare-tray").getByRole("link")).toHaveAttribute("href", /^\/nl\/nl\/compare\?ids=.+,.+/);

  // The tray also survives navigation to another page in the country layout.
  await page.goto("/nl/nl/learn/real-range");
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);

  expect(foreign, "browser must only call our own origin").toEqual([]);
});

test("Language switch keeps filters and the compare tray; country switch keeps the path (Decision 015)", async ({ page }) => {
  await page.goto("/nl/nl/cars?view=table&range=300");
  await expect(page.locator("html")).toHaveAttribute("lang", "nl");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  const toggles = page.getByTestId("compare-toggle");
  await toggles.nth(0).click();
  await toggles.nth(1).click();
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);

  // Only served languages are offered (NL: Dutch + English).
  const lang = page.getByRole("combobox", { name: /Taal|Language/ });
  await expect(lang.locator("option")).toHaveCount(2);
  await lang.selectOption("en");
  await expect(page).toHaveURL(/\/nl\/en\/cars\?view=table&range=300$/);
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(page.locator("#f-rangeMin")).toHaveValue("300");
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);
  await expect(page.getByTestId("compare-tray").getByRole("link")).toHaveAttribute("href", /^\/nl\/en\/compare\?ids=/);

  // Country switch keeps English where served (UK: English only) and the query.
  await page.getByRole("combobox", { name: /Country|Land/ }).selectOption("uk");
  await expect(page).toHaveURL(/\/uk\/en\/cars\?view=table&range=300$/);
  await expect(page.getByLabel(/new price \(GBP\)/i)).toBeVisible();
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);

  // Belgium serves NL, FR, DE + EN; switching back keeps English.
  await page.getByRole("combobox", { name: /Country|Land/ }).selectOption("be");
  await expect(page).toHaveURL(/\/be\/en\/cars\?view=table&range=300$/);
  await expect(page.getByRole("combobox", { name: /Taal|Language/ }).locator("option")).toHaveCount(4);
});

test("Language URLs: redirects, <html lang>, hreflang, no header-based redirect", async ({ page, request, browser }) => {
  // /{country} → config default (temporary); old URLs → default language (permanent).
  const bare = await request.get("/de", { maxRedirects: 0 });
  expect(bare.status()).toBe(307);
  expect(bare.headers()["location"]).toMatch(/\/de\/de$/);
  const old = await request.get("/nl/learn?lang=en", { maxRedirects: 0 });
  expect(old.status()).toBe(308);
  expect(old.headers()["location"]).toMatch(/\/nl\/en\/learn$/);
  const oldNoLang = await request.get("/be/learn/real-range", { maxRedirects: 0 });
  expect(oldNoLang.status()).toBe(308);
  expect(oldNoLang.headers()["location"]).toMatch(/\/be\/nl\/learn\/real-range$/);
  // A language the country doesn't serve redirects to its default; unknown countries 404.
  const unserved = await request.get("/uk/nl/learn", { maxRedirects: 0 });
  expect(unserved.status()).toBe(308);
  expect((await request.get("/xx/en")).status()).toBe(404);
  // Accept-Language never redirects.
  const fr = await request.get("/be/nl/learn", { maxRedirects: 0, headers: { "Accept-Language": "fr-BE,fr" } });
  expect(fr.status()).toBe(200);

  // Static learn page: right <html lang>, hreflang for every served pair + x-default.
  await page.goto("/be/fr/learn/real-range");
  await expect(page.locator("html")).toHaveAttribute("lang", "fr");
  const alts = page.locator('link[rel="alternate"][hreflang]');
  // 15 served pairs (7 countries' own languages + EN; ES and IT since T-119) + x-default.
  expect(await alts.count()).toBe(16);
  await expect(page.locator('link[rel="alternate"][hreflang="x-default"]')).toHaveAttribute("href", /\/nl\/en\/learn\/real-range$/);
  await expect(page.locator('link[rel="alternate"][hreflang="de-BE"]')).toHaveAttribute("href", /\/be\/de\/learn\/real-range$/);

  // Browser prefers French on a Dutch Belgian page: a dismissible banner, no redirect.
  const ctx = await browser.newContext({ locale: "fr-BE" });
  const p = await ctx.newPage();
  await p.goto("/be/nl/top");
  const banner = p.getByTestId("lang-banner");
  await expect(banner).toBeVisible();
  await expect(p).toHaveURL(/\/be\/nl\/top$/);
  await expect(banner.getByRole("link")).toHaveAttribute("href", "/be/fr/top");
  await banner.getByRole("button").click();
  await expect(banner).toHaveCount(0);
  await p.reload();
  await expect(p.getByTestId("lang-banner")).toHaveCount(0);
  await ctx.close();

  // sitemap.xml lists only served pairs.
  const sm = await (await request.get("/sitemap.xml")).text();
  expect(sm).toContain("/be/fr/learn/real-range</loc>");
  expect(sm).not.toContain("/nl/de/");
  expect(sm).not.toContain("/compare");
});

test("Explore rows link to variant pages; header links to All cars, Rankings and Compare", async ({ page }) => {
  await page.goto("/nl/nl/cars?view=table");
  const nav = page.getByRole("navigation", { name: /Hoofdmenu|Main/ });
  // Rankings are parked (Decision 051): the header links to them only when they are switched on.
  if (process.env.E2E_PARKED === "1") await expect(nav.getByRole("link", { name: "Ranglijsten" })).toHaveAttribute("href", "/nl/nl/top");
  else await expect(nav.getByRole("link", { name: "Ranglijsten" })).toHaveCount(0);
  await expect(nav.getByRole("link", { name: "Vergelijken" })).toHaveAttribute("href", "/nl/nl/compare");
  await expect(nav.getByRole("link", { name: "Alle auto's" })).toHaveAttribute("href", "/nl/nl/cars");

  const first = page.getByTestId("explore-row").first().getByRole("rowheader").getByRole("link");
  const href = await first.getAttribute("href");
  expect(href).toMatch(/^\/nl\/nl\/ev\/[^/]+\/[^/]+\/[^/]+\/[^/]+$/);
  await first.click();
  await expect(page).toHaveURL(new RegExp(`${href}$`));
  expect(href).toMatch(/^\/nl\/nl\/ev\//);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
});

// Off by default (404 without STAFF_PAGES=1) is unit-tested (src/lib/staff-guard.test.ts); the e2e
// server turns staff pages on with test credentials (playwright.config.ts).
test("Staff pages need the staff credentials (401 without)", async ({ request }) => {
  const res = await request.get("/staff/review");
  expect(res.status()).toBe(401);
});
