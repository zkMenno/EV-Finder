import { expect, test } from "@playwright/test";

// /learn index + articles from content/learn (coordinator follow-up (c)).
test("Learn index lists guides and terms; an article renders with ⓘ terms, draft banner and sources", async ({ page }) => {
  await page.goto("/nl/nl/learn");
  await expect(page.locator("html")).toHaveAttribute("lang", "nl");
  await expect(page.getByTestId("learn-articles").getByRole("listitem")).toHaveCount(6);
  await page.getByTestId("learn-articles").getByRole("link", { name: "Winterbereik uitgelegd" }).click();
  await expect(page).toHaveURL(/\/nl\/nl\/learn\/winter-range$/);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Winterbereik uitgelegd");
  await expect(page.getByTestId("learn-draft")).toBeVisible();
  await expect(page.getByTestId("learn-sources").getByRole("listitem").first()).toBeVisible();
  // Inline glossary marker → shown text + ⓘ popover linking to the term's learn page.
  const term = page.locator('[data-term="heat-pump"]').first();
  // The popover closes on scroll (use-popover), so scroll first, then hover.
  await term.scrollIntoViewIfNeeded();
  await term.getByRole("button").hover();
  await expect(term.getByRole("tooltip")).toBeVisible();
  await expect(term.getByRole("tooltip").getByRole("link")).toHaveAttribute("href", "/nl/nl/learn/heat-pump");
});

test("A language without a file falls back to English with a notice", async ({ page }) => {
  // winter-range has a French file since T-082 (#35); chemistries is still EN + NL only.
  await page.goto("/be/fr/learn/chemistries");
  await expect(page.locator("html")).toHaveAttribute("lang", "fr");
  await expect(page.getByTestId("learn-fallback")).toBeVisible();
  await expect(page.getByTestId("learn-article")).toHaveAttribute("lang", "en");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Battery types (chemistries) explained");
});
