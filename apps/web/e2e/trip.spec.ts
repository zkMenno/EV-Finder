import { expect, test } from "@playwright/test";

// T-036: trip fit quick check, with TRIP_FIT=1 (playwright.config.ts) and the fixture matrix.
const flagOff = process.env.E2E_TRIP_FIT === "0";

test("TRIP_FIT=0 hides the whole trip UI (run with E2E_TRIP_FIT=0)", async ({ page }) => {
  test.skip(!flagOff, "flag on in this run");
  await page.goto("/nl/en/cars?view=table&trip=1");
  await expect(page.getByTestId("result-count")).toBeVisible();
  await expect(page.getByTestId("trip-bar")).toHaveCount(0);
  await expect(page.getByTestId("trip-col")).toHaveCount(0);
});

test("Trip check: profile + trip → result card, Explore column, winter filter, kept in the browser only", async ({ page, baseURL }) => {
  test.skip(flagOff, "trip fit flag off");
  const origin = new URL(baseURL!).origin;
  const foreign: string[] = [];
  page.on("request", (req) => {
    const u = req.url();
    if (!u.startsWith(origin) && !u.startsWith("data:")) foreign.push(u);
  });

  await page.goto("/nl/en/cars?view=table");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  // Hidden until opened: no column, no panel.
  await expect(page.getByTestId("trip-col")).toHaveCount(0);
  await page.getByTestId("trip-open").click();
  const panel = page.getByTestId("trip-panel");
  await expect(panel).toBeVisible();

  // Profile picker: one tap per question (all optional).
  await panel.getByText("Main car", { exact: true }).click();
  await panel.getByText("Monthly", { exact: true }).click();
  await panel.getByText("Home", { exact: true }).click();
  await panel.getByText("Mixed", { exact: true }).click();
  await panel.getByText("Keep 8+ years", { exact: true }).click();

  await page.locator("#trip-km").fill("120");
  await page.locator("#trip-town").selectOption("nl-groningen");

  const card = page.getByTestId("trip-result");
  await expect(card).toBeVisible();
  await expect(page.getByTestId("trip-estimate-label")).toContainText("fixture matrix");
  await expect(page.getByTestId("trip-winter-km")).toBeVisible();
  await expect(page.getByTestId("trip-summer-km")).toBeVisible();
  await expect(page.getByTestId("trip-wltp-km")).toBeVisible();
  await expect(card).toContainText("Groningen");

  // Explore column with ✓ / ⚠ / ✗ (text, not colour alone).
  await expect(page.getByTestId("trip-col")).toBeVisible();
  await expect(page.getByTestId("trip-cell").first()).toBeVisible();

  // A long trip: some cars fail, stay visible, greyed, with the reason.
  await page.locator("#trip-km").fill("250");
  const failing = page.locator('[data-testid="explore-row"][data-trip="fail"]');
  await expect(failing.first()).toBeVisible();
  await expect(failing.first().getByTestId("trip-reason")).toContainText("Short by about");
  const shown = async () => Number((await page.getByTestId("result-count").innerText()).match(/\d+/)![0]);
  const before = await shown();

  // Filter "does my trips in winter": failing cars go, the URL carries only trip=1.
  await page.getByLabel("Only cars that do my trips in winter").check();
  await expect(page).toHaveURL(/[?&]trip=1/);
  await expect.poll(shown).toBeLessThan(before);
  expect(await shown()).toBeGreaterThan(0);
  await expect(failing).toHaveCount(0);
  expect(page.url()).not.toMatch(/groningen|250|km=/i);

  // Stored in localStorage: a town id and numbers, never coordinates.
  const stored = await page.evaluate(() => window.localStorage.getItem("ev-finder:trip:v1"));
  const parsed = JSON.parse(stored!) as Record<string, unknown>;
  expect(parsed.townId).toBe("nl-groningen");
  expect(parsed.roundTripKm).toBe(250);
  expect(Object.keys(parsed)).not.toEqual(expect.arrayContaining(["lat"]));

  // Nerd level shows the rung and the per-band Wh/km.
  await page.getByTestId("level-switch").getByRole("button", { name: "Nerd" }).click();
  await expect(page.getByTestId("trip-nerd")).toContainText("fixture-matrix");

  // Reload: the trip (localStorage) and the filter (URL) come back without reopening the panel.
  await page.reload();
  await expect(page.getByTestId("trip-chip")).toContainText("250");
  await expect(page.getByTestId("trip-col")).toBeVisible();
  await expect(page.getByLabel("Only cars that do my trips in winter")).toBeChecked();

  expect(foreign, "browser must only call our own origin").toEqual([]);
});

test("Trip check works at 360 px", async ({ page }) => {
  test.skip(flagOff, "trip fit flag off");
  await page.setViewportSize({ width: 360, height: 740 });
  await page.goto("/nl/en/cars");
  await page.getByTestId("trip-open").click();
  await page.locator("#trip-km").fill("80");
  await expect(page.getByTestId("trip-result")).toBeVisible();
  const box = await page.getByTestId("trip-panel").boundingBox();
  expect(box!.x + box!.width).toBeLessThanOrEqual(361);
  // Cards view on narrow screens shows the verdict too.
  await expect(page.getByTestId("explore-card").first().getByTestId("trip-cell")).toBeVisible();
});
