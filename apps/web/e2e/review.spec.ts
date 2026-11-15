// Reviewer checks (T-015 / T-017, overnight 1). Runs on the dev fixture like smoke.spec.ts.
import { expect, test, type Page } from "@playwright/test";

/** Record every request the browser makes that is not to our origin. */
function watchForeign(page: Page, origin: string): string[] {
  const foreign: string[] = [];
  page.on("request", (req) => {
    const u = req.url();
    if (!u.startsWith(origin) && !u.startsWith("data:") && !u.startsWith("blob:")) foreign.push(u);
  });
  return foreign;
}

async function exploreReady(page: Page) {
  await expect(page.getByTestId("explore-row").first()).toBeVisible();
  await expect(page.getByTestId("result-count")).not.toContainText("…");
}

test("T-017: every page talks only to our own origin", async ({ page, baseURL }) => {
  const origin = new URL(baseURL!).origin;
  const foreign = watchForeign(page, origin);

  await page.goto("/nl");
  await exploreReady(page);
  // Open a provenance popover and a glossary ⓘ (they must not load anything foreign either).
  await page.getByTestId("explore-row").first().locator("td button").first().hover();

  const variantHref = await page.getByTestId("explore-row").first().getByRole("rowheader").getByRole("link").getAttribute("href");
  expect(variantHref).toBeTruthy();
  const parts = variantHref!.split("/");
  const generationHref = parts.slice(0, -1).join("/");
  const modelHref = parts.slice(0, -2).join("/");
  const ids = await page.getByTestId("compare-toggle").count();
  expect(ids).toBeGreaterThan(1);

  for (const path of [
    variantHref!,
    generationHref,
    modelHref,
    "/nl/compare?ids=nissan-leaf-ze1-40kwh,renault-zoe-ze50-r135",
    "/nl/learn/real-range",
    "/nl/top",
    "/nl/top/fastest-dc",
    "/uk?lang=en",
  ]) {
    const res = await page.goto(path);
    expect(res?.status(), path).toBe(200);
    await page.waitForLoadState("networkidle");
  }

  expect(foreign, "browser must only call our own origin").toEqual([]);
});

test("T-010: compare tray survives a country switch and drives the compare page", async ({ page }) => {
  await page.goto("/nl");
  await exploreReady(page);
  const toggles = page.getByTestId("compare-toggle");
  await toggles.nth(0).click();
  await toggles.nth(1).click();
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);
  const labels = await page.getByTestId("compare-tray").getByRole("listitem").allInnerTexts();

  // Another country: same tray, compare link uses the new country.
  await page.goto("/de");
  const tray = page.getByTestId("compare-tray");
  await expect(tray.getByRole("listitem")).toHaveCount(2);
  const link = tray.getByRole("link");
  await expect(link).toHaveAttribute("href", /^\/de\/compare\?ids=[^,]+,[^,]+$/);
  await link.click();
  await expect(page).toHaveURL(/\/de\/compare\?ids=/);
  const table = page.getByTestId("compare-table");
  await expect(table).toBeVisible();
  for (const l of labels) await expect(table.locator("thead")).toContainText(l.replace(/×/g, "").trim().split("\n")[0]!.trim());

  // Reload the compare page: tray still there.
  await page.reload();
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);
});

test("T-008: Explore URL state round-trips (filters, sort, view, level) through a reload", async ({ page }) => {
  const url = "/nl?range=200&sort=-range&view=cards&level=nerd";
  await page.goto(url);
  await expect(page.getByTestId("explore-cards")).toBeVisible();
  await expect(page.locator("#f-rangeMin")).toHaveValue("200");
  await expect(page.getByTestId("level-switch").getByRole("button", { pressed: true })).toHaveText(/Nerd/);
  // Hydration must not rewrite the URL away from what was shared.
  await expect(page).toHaveURL(/range=200/);
  await expect(page).toHaveURL(/sort=-range/);
  await expect(page).toHaveURL(/view=cards/);
  await expect(page).toHaveURL(/level=nerd/);

  await page.reload();
  await expect(page.getByTestId("explore-cards")).toBeVisible();
  await expect(page.locator("#f-rangeMin")).toHaveValue("200");
  await expect(page.getByTestId("level-switch").getByRole("button", { pressed: true })).toHaveText(/Nerd/);
});

test("T-008: keyboard — skip link, visible focus, sort, add to compare, remove from tray", async ({ page }) => {
  await page.goto("/nl?lang=en");
  await exploreReady(page);

  // First Tab lands on the skip link, which becomes visible with a focus outline.
  await page.keyboard.press("Tab");
  const skip = page.getByRole("link", { name: /skip/i });
  await expect(skip).toBeFocused();
  await expect(skip).toBeInViewport();
  const outline = await skip.evaluate((el) => getComputedStyle(el).outlineStyle + " " + getComputedStyle(el).outlineWidth);
  expect(outline).toMatch(/solid 3px/);

  // Sort with the keyboard: aria-sort follows.
  const sortBtn = page.getByRole("button", { name: /Sort by .*real/i }).first();
  await sortBtn.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("th[aria-sort='ascending'], th[aria-sort='descending']")).toHaveCount(1);

  // Add to compare with Space, remove from the tray with Enter.
  const toggle = page.getByTestId("compare-toggle").first();
  await toggle.focus();
  await page.keyboard.press("Space");
  await expect(toggle).toHaveAttribute("aria-pressed", "true");
  const tray = page.getByTestId("compare-tray");
  await expect(tray.getByRole("listitem")).toHaveCount(1);
  await tray.getByRole("listitem").getByRole("button").focus();
  await page.keyboard.press("Enter");
  await expect(tray).toHaveCount(0);
});

test("T-008: Explore shows no DC figures for a car without DC data (Zoe R240)", async ({ page }) => {
  await page.goto("/nl?level=nerd&lang=en");
  await exploreReady(page);
  const more = page.getByRole("button", { name: /^\+ \d+$/ });
  while (await more.count()) await more.click();
  const row = page.getByTestId("explore-row").filter({ hasText: "R240 22 kWh" });
  await expect(row).toHaveCount(1);

  const headers = await page.getByTestId("explore-table").locator("thead th").allInnerTexts();
  const idx400 = headers.findIndex((h) => /older chargers/i.test(h));
  const idxDc = headers.findIndex((h) => /20 min/i.test(h));
  expect(idx400).toBeGreaterThan(0);
  expect(idxDc).toBeGreaterThan(0);
  const cells = row.locator("th, td");
  await expect(cells.nth(idx400)).toHaveText("—");
  await expect(cells.nth(idxDc)).toHaveText("—");
});

test("T-009/T-010: spec sheets show no 400 V charger behaviour for a car without DC data", async ({ page }) => {
  // Known bug (review 2026-11-15): Explore hides "On 400 V chargers" when dc_peak_kw is missing,
  // but SpecValue (variant, generation, compare) still prints "native". Remove test.fail once fixed.
  test.fail();
  await page.goto("/nl/compare?ids=renault-zoe-x10-r240&lang=en");
  const row = page.getByTestId("compare-table").getByRole("row").filter({ hasText: /On 400 V chargers/ });
  // Either the row is dropped (all cars lack DC data) or it shows "—".
  if (await row.count()) await expect(row.locator("td").first()).toHaveText("—");
});
