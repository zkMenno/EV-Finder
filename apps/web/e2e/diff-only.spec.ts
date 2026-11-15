import { expect, test } from "@playwright/test";

// T-045: "Differences only" on generation pages hides spec rows every variant shares.
test("generation page: differences only hides shared rows and lives in the URL", async ({ page }) => {
  await page.goto("/nl/en/ev/hyundai/ioniq-5/gen1");
  const toggle = page.getByTestId("diff-only");
  await expect(toggle).toBeVisible();
  const table = page.getByTestId("spec-diff");
  const same = table.locator("tr[data-same]");
  const n = await same.count();
  expect(n).toBeGreaterThan(0);
  await expect(same.first()).toBeVisible();
  await toggle.click();
  await expect(toggle).toHaveAttribute("aria-pressed", "true");
  await expect(same.first()).toBeHidden();
  await expect(page).toHaveURL(/diff=1/);
  await page.reload();
  await expect(page.getByTestId("diff-only")).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByTestId("variant-deltas")).toContainText("real range");
});
