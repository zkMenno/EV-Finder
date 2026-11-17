import { expect, test } from "@playwright/test";

// T-130: the landing page links to the catalogue; the catalogue sorts by popularity by default.

test("landing has no full list, only a 'Show all cars' link to the catalogue", async ({ page }) => {
  await page.goto("/nl/en");
  await expect(page.getByTestId("explore-row")).toHaveCount(0);
  await expect(page.getByTestId("explore-card")).toHaveCount(0);
  const link = page.getByTestId("show-all-cars-link");
  await expect(link).toHaveText("Show all cars");
  await expect(link).toHaveAttribute("href", "/nl/en/cars");
  await link.click();
  await expect(page).toHaveURL(/\/nl\/en\/cars/);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("All electric cars");
});

test("catalogue: Most popular first as cards, #n tags in order, How we rank explains the blend", async ({ page }) => {
  await page.goto("/nl/en/cars");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  await expect(page.getByTestId("sort-menu")).toHaveValue("popular");
  await expect(page.getByTestId("explore-cards")).toBeVisible();
  const tags = await page.getByTestId("popular-tag").allInnerTexts();
  expect(tags.length).toBeGreaterThan(3);
  expect(tags[0]).toBe("#1 popular");
  const ranks = tags.map((t) => Number(t.match(/\d+/)![0]));
  expect(ranks, "ranks never go down the list").toEqual([...ranks].sort((a, b) => a - b));
  expect(new Set(ranks).size, "one tag per generation, not per variant").toBe(ranks.length);
  await expect(page.getByTestId("popular-why")).toContainText("Netherlands and the UK");
  await page.getByTestId("popular-why").getByRole("link", { name: "How we rank" }).click();
  await expect(page.getByTestId("how-we-rank")).toBeInViewport();
  await expect(page.getByTestId("how-we-rank")).toContainText("80 % comes from registrations");
  await expect(page.getByTestId("how-we-rank")).toContainText("one person's verdict");
});

test("catalogue: the sort menu writes the URL and survives a reload", async ({ page }) => {
  await page.goto("/nl/en/cars");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  await page.getByTestId("sort-menu").selectOption("price");
  await expect(page).toHaveURL(/[?&]sort=price(&|$)/);
  await expect(page.getByTestId("popular-why")).toHaveCount(0);
  await page.reload();
  await expect(page.getByTestId("sort-menu")).toHaveValue("price");
  await page.getByTestId("sort-menu").selectOption("range");
  await expect(page).toHaveURL(/[?&]sort=-range(&|$)/);
});

test("old Explore links on the landing page move to the catalogue with their state", async ({ page }) => {
  await page.goto("/nl/en?view=table&range=300");
  await expect(page).toHaveURL(/\/nl\/en\/cars\?view=table&range=300$/);
  await expect(page.locator("#f-rangeMin")).toHaveValue("300");
  // Hero links stay on the landing page.
  await page.goto("/nl/en?role=second&budget=20000");
  await expect(page).toHaveURL(/\/nl\/en\?role=second&budget=20000$/);
});

// Every language: long words and native <select> widths differ (FR and ES overflowed at first; T-097 lesson).
test("catalogue fits a 360 px phone without sideways scrolling, in all six languages", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 780 });
  for (const path of ["/nl/en", "/nl/nl", "/de/de", "/fr/fr", "/es/es", "/it/it"]) {
    await page.goto(`${path}/cars`);
    await expect(page.getByTestId("result-count")).not.toContainText("…");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow, `${path}/cars is wider than the phone`).toBeLessThanOrEqual(0);
    const menu = await page.getByTestId("sort-menu").boundingBox();
    expect(menu!.x + menu!.width, `${path}: sort menu sticks out`).toBeLessThanOrEqual(360);
  }
});
