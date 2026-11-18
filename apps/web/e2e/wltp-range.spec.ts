import { expect, test } from "@playwright/test";

// T-143 (Decision 085): our real range leads; the official WLTP range sits next to it, labelled
// "Official (WLTP)". The range filter and sort default to real range; WLTP is a second control.

/** The official km a line shows (its highest value on a card), from data-km (the text also holds the source popover). */
const kmOf = (s: string | null) => Number(s ?? NaN);

test("filter: the WLTP slider sits in the range group, keeps its value in the URL and only keeps cars at or above it", async ({ page }) => {
  await page.goto("/nl/en/cars");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  const group = page.getByTestId("fg-winter");
  // Real range leads: the winter (real) slider comes first, WLTP second, both in one group.
  const sliders = group.locator('input[type="range"]');
  await expect(sliders).toHaveCount(2);
  await expect(sliders.nth(0)).toHaveAttribute("id", "f-winterMin");
  await expect(sliders.nth(1)).toHaveAttribute("id", "f-wltpMin");
  await expect(group.getByLabel("Official (WLTP): any")).toBeVisible();
  const before = await page.getByTestId("result-count").textContent();

  await page.getByTestId("filter-wltp").fill("500");
  await expect(page).toHaveURL(/[?&]wltp=500(&|$)/);
  await expect(page).not.toHaveURL(/[?&]winter=/);
  await expect(group.getByLabel("Official (WLTP): at least 500 km")).toBeVisible();
  await expect(page.getByTestId("filter-pill").filter({ hasText: "500+ km official (WLTP)" })).toBeVisible();
  await expect(page.getByTestId("result-count")).not.toHaveText(before ?? "");

  // Every card left has an official figure of 500 km or more (no "not known", no back-fill).
  const lines = page.getByTestId("fact-wltp");
  await expect(lines.first()).toBeVisible();
  for (const line of await lines.all()) {
    await expect(line).toHaveAttribute("data-known", "1");
    expect(kmOf(await line.getAttribute("data-km"))).toBeGreaterThanOrEqual(500);
  }

  // The URL state survives a reload.
  await page.reload();
  await expect(page.getByTestId("filter-wltp")).toHaveValue("500");
});

test("sort: the menu offers the WLTP sort after winter range; the range header still sorts by real range", async ({ page }) => {
  await page.goto("/nl/en/cars");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  await page.getByTestId("sort-menu").selectOption("wltp");
  await expect(page).toHaveURL(/[?&]sort=-wltp(&|$)/);
  const first = await page.getByTestId("fact-wltp").nth(0).getAttribute("data-km");
  const second = await page.getByTestId("fact-wltp").nth(1).getAttribute("data-km");
  expect(kmOf(first)).toBeGreaterThanOrEqual(kmOf(second));

  await page.goto("/nl/en/cars?view=table");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  await page.getByRole("button", { name: /Sort by .*real/i }).first().click();
  await expect(page).toHaveURL(/[?&]sort=-range(&|$)/);
});

test("cards and rows: real range first, then 'Official (WLTP)'; a car without WLTP says 'not known'", async ({ page }) => {
  await page.goto("/nl/en/cars");
  const card = page.getByTestId("explore-card").first();
  const facts = card.locator('[data-testid="fact-winter"], [data-testid="fact-summer"], [data-testid="fact-wltp"]');
  await expect(facts.nth(0)).toHaveAttribute("data-testid", "fact-winter");
  await expect(facts.nth(1)).toHaveAttribute("data-testid", "fact-summer");
  await expect(facts.nth(2)).toHaveAttribute("data-testid", "fact-wltp");
  await expect(card.getByTestId("fact-wltp")).toContainText("Official (WLTP)");

  await page.goto("/nl/en/cars?view=table&level=detailed");
  const cell = page.getByTestId("explore-row").first().getByTestId("wltp-range");
  await expect(cell).toContainText("Official (WLTP)");
  // The release has cars with a real range but no official figure: they read "not known", never a number.
  const unknown = page.locator('[data-testid="wltp-range"][data-known="0"]');
  await page.goto("/nl/en/cars?view=table&sort=-range");
  for (let i = 0; i < 6 && (await unknown.count()) === 0; i++) {
    const more = page.getByRole("button", { name: /Show \d+ more cars/ });
    if (!(await more.count())) break;
    await more.click();
  }
  if (await unknown.count()) {
    await expect(unknown.first()).toHaveText(/^Official \(WLTP\)\s*not known$/);
  }
});

test("variant page: real range row first, then 'Official (WLTP)' with a one-sentence ⓘ", async ({ page }) => {
  // Table rows are versions: the first one left by the WLTP filter links to its variant page.
  await page.goto("/nl/en/cars?view=table&wltp=500");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  await page.getByTestId("explore-row").first().locator('a[href*="/ev/"]').first().click();
  await expect(page).toHaveURL(/\/nl\/en\/ev\/[^/]+\/[^/]+\/[^/]+\/[^/?]+/);

  const range = page.locator("table").filter({ has: page.locator("caption", { hasText: "Range" }) });
  const heads = range.locator("tbody th");
  await expect(heads.nth(0)).toContainText("Real-world range");
  await expect(heads.nth(1)).toContainText("Official (WLTP)");
  const value = range.locator("tbody tr").nth(1).getByTestId("wltp-range");
  await expect(value).toHaveAttribute("data-known", "1");
  expect(kmOf(await value.getAttribute("data-km"))).toBeGreaterThanOrEqual(500);

  await heads.nth(1).getByRole("button", { name: "About Official (WLTP)" }).click();
  await expect(page.getByText("our real range is what you can expect in everyday driving")).toBeVisible();
});
