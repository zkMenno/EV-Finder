import { expect, test } from "@playwright/test";

test("Explore: filter, add 2 to compare, reload, tray keeps 2", async ({ page, baseURL }) => {
  const origin = new URL(baseURL!).origin;
  const foreign: string[] = [];
  page.on("request", (req) => {
    const u = req.url();
    if (!u.startsWith(origin) && !u.startsWith("data:")) foreign.push(u);
  });

  await page.goto("/nl/en");
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
  await expect(page.getByTestId("compare-tray").getByRole("link")).toHaveAttribute("href", /^\/nl\/en\/compare\?ids=.+,.+/);

  // The tray also survives navigation to another page in the country layout.
  await page.goto("/nl/en/learn/real-range");
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);

  expect(foreign, "browser must only call our own origin").toEqual([]);
});

test("Country switch keeps the path, filters and the compare tray (Decision 015 + 082)", async ({ page }) => {
  await page.goto("/nl/en?range=300");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  const toggles = page.getByTestId("compare-toggle");
  await toggles.nth(0).click();
  await toggles.nth(1).click();
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);
  // Decision 082: English only, so there is no language picker.
  await expect(page.getByRole("combobox", { name: /Language/ })).toHaveCount(0);

  await page.getByRole("combobox", { name: /Country/ }).selectOption("uk");
  await expect(page).toHaveURL(/\/uk\/en\?range=300$/);
  await expect(page.getByLabel(/new price \(GBP\)/i)).toBeVisible();
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);

  await page.getByRole("combobox", { name: /Country/ }).selectOption("be");
  await expect(page).toHaveURL(/\/be\/en\?range=300$/);
  await expect(page.locator("#f-rangeMin")).toHaveValue("300");
  await expect(page.getByTestId("compare-tray").getByRole("link")).toHaveAttribute("href", /^\/be\/en\/compare\?ids=/);
});

test("Language URLs: old URLs redirect to English, <html lang>, hreflang, no header-based redirect", async ({ page, request }) => {
  const old = await request.get("/nl/learn?lang=en", { maxRedirects: 0 });
  expect(old.status()).toBe(308);
  expect(old.headers()["location"]).toMatch(/\/nl\/en\/learn$/);
  const oldNoLang = await request.get("/be/learn/real-range", { maxRedirects: 0 });
  expect(oldNoLang.status()).toBe(308);
  expect(oldNoLang.headers()["location"]).toMatch(/\/be\/en\/learn\/real-range$/);
  expect((await request.get("/xx/en")).status()).toBe(404);
  // Accept-Language never redirects a served page.
  const fr = await request.get("/be/en/learn", { maxRedirects: 0, headers: { "Accept-Language": "fr-BE,fr" } });
  expect(fr.status()).toBe(200);

  // Static learn page: right <html lang>, hreflang for every served pair + x-default.
  await page.goto("/be/en/learn/real-range");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  // 7 served pairs (one English page per launch country, Decision 082) + x-default.
  expect(await page.locator('link[rel="alternate"][hreflang]').count()).toBe(8);
  await expect(page.locator('link[rel="alternate"][hreflang="x-default"]')).toHaveAttribute("href", /\/nl\/en\/learn\/real-range$/);
  await expect(page.locator('link[rel="alternate"][hreflang="en-BE"]')).toHaveAttribute("href", /\/be\/en\/learn\/real-range$/);

  const sm = await (await request.get("/sitemap.xml")).text();
  expect(sm).toContain("/be/en/learn/real-range</loc>");
  expect(sm).not.toContain("/compare");
});

test("Explore rows link to variant pages; header links to Rankings and Compare", async ({ page }) => {
  await page.goto("/nl/en");
  const nav = page.getByRole("navigation", { name: /Hoofdmenu|Main/ });
  // Rankings are parked (Decision 051): the header links to them only when they are switched on.
  if (process.env.E2E_PARKED === "1") await expect(nav.getByRole("link", { name: "Rankings" })).toHaveAttribute("href", "/nl/en/top");
  else await expect(nav.getByRole("link", { name: "Rankings" })).toHaveCount(0);
  await expect(nav.getByRole("link", { name: "Compare", exact: true })).toHaveAttribute("href", "/nl/en/compare");

  const first = page.getByTestId("explore-row").first().getByRole("rowheader").getByRole("link");
  const href = await first.getAttribute("href");
  expect(href).toMatch(/^\/nl\/en\/ev\/[^/]+\/[^/]+\/[^/]+\/[^/]+$/);
  await first.click();
  await expect(page).toHaveURL(new RegExp(`${href}$`));
  expect(href).toMatch(/^\/nl\/en\/ev\//);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
});

// Off by default (404 without STAFF_PAGES=1) is unit-tested (src/lib/staff-guard.test.ts); the e2e
// server turns staff pages on with test credentials (playwright.config.ts).
test("Staff pages need the staff credentials (401 without)", async ({ request }) => {
  const res = await request.get("/staff/review");
  expect(res.status()).toBe(401);
});
