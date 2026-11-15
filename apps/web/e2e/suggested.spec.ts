import { expect, test } from "@playwright/test";

// T-067: Explore's "Suggested" sort follows the profile picked in the hero.
test("suggested sort appears with a profile, sorts, and explains itself", async ({ page }) => {
  await page.goto("/nl/en?role=only&trips=monthly&view=table");
  const toggle = page.getByTestId("suggested-toggle");
  await expect(toggle).toContainText("Road-tripper");
  await toggle.click();
  await expect(toggle).toHaveAttribute("aria-pressed", "true");
  await expect(page).toHaveURL(/sort=-?suggested/);
  await page.getByTestId("suggested").getByRole("button", { name: /Why this order/ }).click();
  await expect(page.getByTestId("suggested-why")).toContainText("fast-charging speed");
});

test("suggested sort follows a new answer in the hero without a reload", async ({ page }) => {
  await page.goto("/nl/en?role=only&trips=monthly&sort=-suggested");
  await expect(page.getByTestId("suggested-toggle")).toContainText("Road-tripper");
  await page.getByText("A second car").click();
  await expect(page.getByTestId("suggested-toggle")).toContainText("Runabout");
});

test("without a profile the sort asks for one", async ({ page }) => {
  await page.goto("/nl/en?sort=-suggested");
  await expect(page.getByTestId("suggested-none")).toBeVisible();
});
