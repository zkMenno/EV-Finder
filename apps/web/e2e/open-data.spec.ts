import { expect, test } from "@playwright/test";

// T-090 / Decision 016: the open data page lists the release bundle with licence and citation.
test("open data page: files with size and sha256, CC BY citation, footer link", async ({ page }) => {
  await page.goto("/nl/en");
  await page.getByTestId("footer-data").click();
  await expect(page).toHaveURL(/\/nl\/en\/data$/);
  const files = page.getByTestId("open-file");
  await expect(files.first()).toHaveText("variants.csv");
  await expect(files.first()).toHaveAttribute("href", /^https:\/\/github\.com\/.+\/releases\/download\/data-v\d+\/open\.variants\.csv$/);
  await expect(page.getByTestId("open-data")).toContainText("sha256");
  await expect(page.getByTestId("open-cite")).toContainText("CC BY 4.0");
});

test("open data page in Dutch", async ({ page }) => {
  await page.goto("/nl/nl/data");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Open data");
  await expect(page.getByTestId("open-cite")).toContainText("Bron:");
});
