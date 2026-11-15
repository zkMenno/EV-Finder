import { expect, test } from "@playwright/test";

// T-026: "Find a charger / plan a trip" block. Links come from e2e/fixtures/charging-links.json
// (CHARGING_LINKS_FILE in playwright.config.ts) until T-024 fills config/countries/*.yaml.
const fixtureOn = process.env.E2E_CHARGING_LINKS_FILE !== "";

test("Country page and learn pages show the link block; links are text, new tab, noopener, UTM", async ({ page }) => {
  test.skip(!fixtureOn, "no charging link fixture");
  await page.goto("/nl?lang=en");
  const block = page.getByTestId("charging-links");
  await expect(block).toBeVisible();
  await expect(block.getByRole("heading", { name: "Find a charger / plan a trip" })).toBeVisible();
  const links = block.getByTestId("charging-link");
  await expect(links).toHaveCount(4);
  await expect(links.first()).toContainText("Chargemap");
  for (const l of await links.all()) {
    await expect(l).toHaveAttribute("target", "_blank");
    await expect(l).toHaveAttribute("rel", /noopener/);
    await expect(l).toHaveAttribute("rel", /nofollow/);
    await expect(l).toHaveAttribute("href", /utm_source=evfinder&utm_medium=referral&utm_campaign=charging_links/);
    expect(await l.locator("img").count()).toBe(0);
  }

  await page.goto("/nl/learn/real-range?lang=en");
  await expect(page.getByTestId("charging-links").getByTestId("charging-link")).toHaveCount(4);
});

test("A country without links renders no block", async ({ page }) => {
  await page.goto("/de?lang=en");
  await expect(page.getByTestId("result-count")).toBeVisible();
  await expect(page.getByTestId("charging-links")).toHaveCount(0);
});

test("Model pages: plain ABRP link in the footer, no duplicate ABRP in the block; fits 360 px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 740 });
  await page.goto("/nl?lang=en&view=table");
  const href = await page.getByTestId("explore-row").first().getByRole("rowheader").getByRole("link").getAttribute("href");
  const modelHref = href!.split("/").slice(0, 5).join("/");
  await page.goto(`${modelHref}?lang=en`);
  const block = page.getByTestId("charging-links");
  await expect(block).toBeVisible();
  const abrp = block.getByTestId("abrp-link");
  await expect(abrp).toHaveAttribute("href", /^https:\/\/abetterrouteplanner\.com\/\?utm_source=evfinder/);
  await expect(abrp).toHaveAttribute("target", "_blank");
  await expect(abrp).toHaveAttribute("rel", /noopener/);
  if (fixtureOn) await expect(block.getByTestId("charging-link")).toHaveCount(3);
  await expect(block.getByTestId("charging-link").filter({ hasText: /Routeplanner/ })).toHaveCount(0);
  const box = await block.boundingBox();
  expect(box!.x + box!.width).toBeLessThanOrEqual(361);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(360);

  // Variant pages get the same footer.
  await page.goto(`${href}?lang=en`);
  await expect(page.getByTestId("abrp-link")).toBeVisible();
});
