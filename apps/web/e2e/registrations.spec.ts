// T-058 / Q-066: RDW cars from a year two generations share (no name or battery clue) are counted
// for the model, so a row has a generation-level and a model-level RDW count for the same period.
// Both lines render (no duplicate React key dropping one), the model-level line says the
// generation is unknown, and neither is summed. Runs on the published release; no fixed counts,
// because the data builder may rebuild it.
import { expect, test, type Locator } from "@playwright/test";

async function expectSharedYearPair(list: Locator, modelLabel: RegExp) {
  const model = list.locator('li[data-level="model"][data-source="rdw"]');
  await expect(model).toHaveCount(1);
  await expect(model).toContainText(modelLabel);
  const period = await model.getAttribute("data-period");
  const gen = list.locator(`li[data-level="generation"][data-source="rdw"][data-period="${period}"]`);
  await expect(gen).toHaveCount(1);
  await expect(gen).not.toContainText(modelLabel);
  // Each (kind, period, level, source) appears once: no line lost or doubled.
  const keys = await list
    .locator("li")
    .evaluateAll((els) => els.map((e) => ["kind", "period", "level", "source"].map((k) => e.getAttribute(`data-${k}`)).join("|")));
  expect(new Set(keys).size).toBe(keys.length);
}

test.describe("registrations: shared-year model-level counts", () => {
  test("generation page shows the generation count and the model-level count apart", async ({ page }) => {
    await page.goto("/nl/en/ev/renault/zoe/ph1");
    await expectSharedYearPair(page.getByTestId("registrations"), /generation unknown, shown on all Renault Zoe generations/);
  });

  test("the same model-level count shows on the other generation and on variant pages", async ({ page }) => {
    await page.goto("/nl/en/ev/renault/zoe/ph2");
    await expectSharedYearPair(page.getByTestId("registrations"), /all Renault Zoe generations/);
    await page.goto("/nl/en/ev/kia/niro-ev/de");
    const variantLink = page.locator('a[href^="/nl/en/ev/kia/niro-ev/de/"]').first();
    await variantLink.click();
    await expectSharedYearPair(page.getByTestId("registrations"), /all Kia Niro EV generations/);
  });

  test("Dutch wording", async ({ page }) => {
    await page.goto("/nl/nl/ev/renault/zoe/ph1");
    await expectSharedYearPair(page.getByTestId("registrations"), /generatie onbekend, getoond bij alle generaties Renault Zoe/);
  });
});
