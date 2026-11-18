import { expect, test } from "@playwright/test";
import { ENGLISH_ONLY, ENGLISH_ONLY_REASON } from "./langs";

// /learn index + articles from content/learn (coordinator follow-up (c)).
test("Learn index lists guides and terms; an article renders with ⓘ terms, draft banner and sources", async ({ page }) => {
  await page.goto("/nl/en/learn");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(page.getByTestId("learn-articles").getByRole("listitem")).toHaveCount(6);
  await page.getByTestId("learn-articles").getByRole("link", { name: "Winter range explained" }).click();
  await expect(page).toHaveURL(/\/nl\/en\/learn\/winter-range$/);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Winter range explained");
  await expect(page.getByTestId("learn-draft")).toBeVisible();
  await expect(page.getByTestId("learn-sources").getByRole("listitem").first()).toBeVisible();
  // Inline glossary marker → shown text + ⓘ popover linking to the term's learn page.
  const term = page.locator('[data-term="heat-pump"]').first();
  // The popover closes on scroll (use-popover), so scroll first, then hover.
  await term.scrollIntoViewIfNeeded();
  await term.getByRole("button").hover();
  await expect(term.getByRole("tooltip")).toBeVisible();
  await expect(term.getByRole("tooltip").getByRole("link")).toHaveAttribute("href", "/nl/en/learn/heat-pump");
});

// T-082 added FR for winter-range, so the fallback check uses an EN+NL-only guide.
test("A language without a file falls back to English with a notice", async ({ page }) => {
  // Needs a served non-English language (French for Belgium); hidden at launch (Decision 082).
  test.skip(ENGLISH_ONLY, ENGLISH_ONLY_REASON);
  await page.goto("/be/fr/learn/chemistries");
  await expect(page.locator("html")).toHaveAttribute("lang", "fr");
  await expect(page.getByTestId("learn-fallback")).toBeVisible();
  await expect(page.getByTestId("learn-article")).toHaveAttribute("lang", "en");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Battery types (chemistries) explained");
});
