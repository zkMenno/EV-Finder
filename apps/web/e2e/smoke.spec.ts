import { expect, test } from "@playwright/test";

test("Explore: filter, add 2 to compare, reload, tray keeps 2", async ({ page, baseURL }) => {
  const origin = new URL(baseURL!).origin;
  const foreign: string[] = [];
  page.on("request", (req) => {
    const u = req.url();
    if (!u.startsWith(origin) && !u.startsWith("data:")) foreign.push(u);
  });

  await page.goto("/nl");
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
  await expect(page.getByTestId("compare-tray").getByRole("link")).toHaveAttribute("href", /\/nl\/compare\?ids=.+,.+/);

  // The tray also survives navigation to another page in the country layout.
  await page.goto("/nl/learn/real-range");
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(2);

  expect(foreign, "browser must only call our own origin").toEqual([]);
});

test("Language and country switchers keep the rest of the URL", async ({ page }) => {
  await page.goto("/nl?range=300");
  await page.getByLabel(/Taal|Language/).selectOption("en");
  await expect(page).toHaveURL(/\/nl\?range=300&lang=en/);
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await page.getByLabel(/Country|Land/).selectOption("uk");
  await expect(page).toHaveURL(/\/uk\?range=300&lang=en/);
  // UK prices in GBP.
  await expect(page.getByLabel(/new price \(GBP\)/i)).toBeVisible();
});
