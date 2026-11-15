// Reviewer checks (T-015 / T-017, overnight 1). Runs on the published release like smoke.spec.ts.
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

  await page.goto("/nl/nl");
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
    "/nl/nl/compare?ids=nissan-leaf-ze1-40kwh,renault-zoe-ph2-r135",
    "/nl/nl/learn/real-range",
    ...(process.env.E2E_PARKED === "1" ? ["/nl/nl/top", "/nl/nl/top/fastest-dc"] : ["/nl/nl/learn"]),
    "/uk/en",
  ]) {
    const res = await page.goto(path);
    expect(res?.status(), path).toBe(200);
    await page.waitForLoadState("networkidle");
  }

  expect(foreign, "browser must only call our own origin").toEqual([]);
});

test("T-010: compare tray survives a country switch and drives the compare page", async ({ page }) => {
  await page.goto("/nl/nl");
  await exploreReady(page);
  const toggles = page.getByTestId("compare-toggle");
  await toggles.nth(0).click();
  await toggles.nth(1).click();
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);
  const labels = await page.getByTestId("compare-tray").getByRole("listitem").allInnerTexts();

  // Another country: same tray, compare link uses the new country.
  await page.goto("/de/de");
  const tray = page.getByTestId("compare-tray");
  await expect(tray.getByRole("listitem")).toHaveCount(2);
  const link = tray.getByRole("link");
  await expect(link).toHaveAttribute("href", /^\/de\/de\/compare\?ids=[^,]+,[^,]+$/);
  await link.click();
  await expect(page).toHaveURL(/\/de\/de\/compare\?ids=/);
  const table = page.getByTestId("compare-table");
  await expect(table).toBeVisible();
  for (const l of labels) await expect(table.locator("thead")).toContainText(l.replace(/×/g, "").trim().split("\n")[0]!.trim());

  // Reload the compare page: tray still there.
  await page.reload();
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);
});

test("T-008: Explore URL state round-trips (filters, sort, view, level) through a reload", async ({ page }) => {
  const url = "/nl/nl?range=200&sort=-range&view=cards&level=nerd";
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
  await page.goto("/nl/en");
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
  await page.goto("/nl/en?level=nerd");
  await exploreReady(page);
  const more = page.getByTestId("show-more");
  while (await more.count()) await more.click();
  const row = page.getByTestId("explore-row").filter({ hasText: "R240 (22 kWh)" });
  await expect(row).toHaveCount(1);

  const headers = await page.getByTestId("explore-table").locator("thead th").allInnerTexts();
  const idx400 = headers.findIndex((h) => /older chargers/i.test(h));
  const idxDc = headers.findIndex((h) => /20 min/i.test(h));
  expect(idx400).toBeGreaterThan(0);
  expect(idxDc).toBeGreaterThan(0);
  const cells = row.locator("th, td");
  // "—" for sighted users, words for screen readers.
  await expect(cells.nth(idx400)).toHaveText("—no DC charging data");
  await expect(cells.nth(idx400).locator(".sr-only")).toHaveText("no DC charging data");
  await expect(cells.nth(idxDc)).toHaveText("—no data");
  await expect(cells.nth(idx400)).not.toContainText(/native|booster/);
});

test("T-009/T-010: spec sheets show no 400 V charger behaviour for a car without DC data", async ({ page }) => {
  // Compare: Zoe R240 (no DC data) next to Zoe phase 2 R135 (46 kW): the 400 V row stays for the R135 only.
  await page.goto("/nl/en/compare?ids=renault-zoe-ph1-r240,renault-zoe-ph2-r135");
  const row = page.getByTestId("compare-table").getByRole("row").filter({ hasText: /On 400 V chargers/ }).first();
  await expect(row.locator("td").nth(0)).toHaveText(/—no DC charging data$/);
  await expect(row.locator("td").nth(1)).toHaveText(/native/);

  // Variant page: no "native" anywhere in the charging table.
  await page.goto("/nl/en/ev/renault/zoe/ph1/r240");
  const vrow = page.getByRole("row").filter({ hasText: /^On 400 V chargers/ });
  await expect(vrow.first().locator("td")).toHaveText("—no DC charging data");
  await expect(page.getByRole("row").filter({ hasText: /^Power on 400 V chargers/ }).first().locator("td")).toHaveText("—no DC charging data");
  // (Generation key facts: phase 1 mixes variants with and without DC data, so the release has no
  // all-no-DC generation to check; the rule itself is unit-tested in src/lib/dc.test.ts.)
});

test("T-008: table Tab stops — name link, heart and compare per row; Nerd adds one sources button", async ({ page }) => {
  await page.goto("/nl/en?level=detailed");
  await exploreReady(page);
  const row = page.getByTestId("explore-row").first();
  const stops = await row.evaluate((tr) =>
    [...tr.querySelectorAll<HTMLElement>("a[href], button, input, [tabindex]")].filter((el) => el.tabIndex >= 0 && !el.hidden).length,
  );
  expect(stops).toBe(3);
  // Numbers still open their provenance on hover.
  await row.locator("td button").first().hover();
  await expect(page.getByRole("tooltip").filter({ hasText: /Source|No source/ }).first()).toBeVisible();

  await page.goto("/nl/en?level=nerd");
  await exploreReady(page);
  const nerdRow = page.getByTestId("explore-row").first();
  const nerdStops = await nerdRow.evaluate((tr) =>
    [...tr.querySelectorAll<HTMLElement>("a[href], button, input, [tabindex]")].filter((el) => el.tabIndex >= 0).length,
  );
  expect(nerdStops).toBe(4);
  const sources = nerdRow.getByTestId("row-sources");
  await expect(sources).toHaveAccessibleName(/^Sources for /);
  await sources.focus();
  await expect(page.locator(`[id="${await sources.getAttribute("aria-describedby")}"]`)).toBeVisible();
});

test("T-008: show-more has a full name; a full tray keeps the compare toggle reachable (aria-disabled)", async ({ page }) => {
  await page.goto("/nl/en");
  await exploreReady(page);
  // The dev fixture (38 cars) fits in one page; with a real release (E2E_CATALOGUE_DIR) the button shows.
  const more = page.getByTestId("show-more");
  if (await more.count()) await expect(more).toHaveAccessibleName(/^Show \d+ more cars$/);

  const toggles = page.getByTestId("compare-toggle");
  for (let i = 0; i < 4; i++) await toggles.nth(i).click();
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(4);
  const fifth = toggles.nth(4);
  await expect(fifth).toHaveAttribute("aria-disabled", "true");
  // Not the `disabled` attribute (that would drop it from the Tab order).
  expect(await fifth.evaluate((el) => (el as HTMLButtonElement).disabled)).toBe(false);
  await expect(fifth).toHaveAccessibleDescription(/up to 4 cars/);
  await fifth.focus();
  await expect(fifth).toBeFocused();
  await page.keyboard.press("Space");
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(4);
});

test("About page: linked in the footer, explains the site, credits the release's sources", async ({ page }) => {
  for (const path of ["/nl/en", "/nl/en/top", "/nl/en/learn/real-range"]) {
    await page.goto(path);
    await expect(page.getByTestId("footer-about")).toHaveAttribute("href", "/nl/en/about");
  }
  await page.getByTestId("footer-about").click();
  await expect(page).toHaveURL(/\/nl\/en\/about/);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(/^About /);
  await expect(page.getByRole("heading", { name: "Credits / data sources" })).toBeVisible();
  await expect(page.getByText(/AGPL-3\.0/)).toBeVisible();
  await expect(page.getByText(/CC BY 4\.0/).first()).toBeVisible();
  // The about page is static, built from whatever release the build saw (the dev fixture has one
  // source, release 1 several); each source is unit-tested in credits.test.ts.
  expect(await page.getByTestId("credits").locator("tbody tr").count()).toBeGreaterThanOrEqual(1);

  await page.goto("/nl/nl/about");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(/^Over /);
  await expect(page.getByRole("heading", { name: "Bronvermelding / databronnen" })).toBeVisible();
});
