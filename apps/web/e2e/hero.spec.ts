import { expect, test } from "@playwright/test";
import { HAS_SCORES, NO_SCORES_REASON } from "./release";

// T-080: the landing-page hero ranks the published release for each profile.
const PROFILES: [string, string][] = [
  ["road-tripper", "role=only&trips=monthly&charge=home"],
  ["daily driver", "role=main&trips=never&charge=home"],
  ["runabout", "role=second&charge=home"],
  ["kerbside charger", "role=only&trips=often&charge=public_only&area=city"],
];

for (const [name, qs] of PROFILES) {
  test(`hero: ${name} gets a top 10 with the first 5 as the shortlist`, async ({ page }) => {
    test.skip(!HAS_SCORES, NO_SCORES_REASON);
    await page.goto(`/nl/en?${qs}`);
    await expect(page.getByTestId("hero-card")).toHaveCount(10);
    await expect(page.getByTestId("hero-shortlist").getByTestId("hero-card")).toHaveCount(5);
    await expect(page.getByTestId("hero-more").getByTestId("hero-card")).toHaveCount(5);
    await expect(page.getByTestId("hero-why").first()).not.toBeEmpty();
  });
}

test("hero: picking answers builds the profile and the URL", async ({ page }) => {
  await page.goto("/nl/en");
  await expect(page.getByTestId("hero-results")).toContainText("Answer the questions");
  await page.getByText("A second car").click();
  await expect(page.getByTestId("hero-profile")).toContainText("Runabout");
  await expect(page).toHaveURL(/role=second/);
  // Ranked cards with release scores; without them the hero says so (Decision 065).
  await expect(page.getByTestId(HAS_SCORES ? "hero-card" : "hero-no-scores").first()).toBeVisible();
});

test("hero: without release scores it says 'ranking not available yet' and ranks nothing (Decision 065)", async ({ page }) => {
  test.skip(HAS_SCORES, "the release under test has shortlist_scores.json");
  await page.goto("/nl/en?role=only&trips=monthly&charge=home&budget=15000");
  await expect(page.getByTestId("hero-no-scores")).toContainText("Ranking not available yet");
  await expect(page.getByTestId("hero-card")).toHaveCount(0);
  await page.goto("/nl/nl?role=second");
  await expect(page.getByTestId("hero-no-scores")).toContainText("Ranglijst nog niet beschikbaar");
});

test("hero: changing the budget re-ranks without a reload", async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.goto("/nl/en?role=only&trips=monthly&cond=new");
  await expect(page.getByTestId("hero-card")).toHaveCount(10);
  const marker = await page.evaluate(() => {
    (window as unknown as { __noReload: boolean }).__noReload = true;
    return true;
  });
  expect(marker).toBe(true);
  const before = await page.getByTestId("hero-count").innerText();
  await page.getByTestId("hero-budget-40000").click();
  await expect(page.getByTestId("hero-count")).not.toHaveText(before);
  await expect(page).toHaveURL(/budget=40000/);
  expect(await page.evaluate(() => (window as unknown as { __noReload?: boolean }).__noReload)).toBe(true);
  // New cars with a known price stay within budget.
  for (const p of await page.getByTestId("hero-price").allInnerTexts()) {
    const m = /New: €([\d,]+)/.exec(p);
    if (m) expect(Number(m[1]!.replace(/,/g, ""))).toBeLessThanOrEqual(40000);
  }
});

test("hero: removing a profile filter and adding to compare", async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.goto("/nl/en?role=only&trips=monthly");
  const chips = page.getByTestId("hero-presets").getByRole("button");
  const n = await chips.count();
  await chips.first().click();
  await expect(page.getByTestId("hero-presets").getByRole("button")).toHaveCount(n - 1);
  await expect(page).toHaveURL(/pxoff=/);
  await page.getByTestId("hero-compare").first().click();
  await expect(page.getByTestId("hero-compare").first()).toHaveAttribute("aria-pressed", "true");
});

test("hero: works at 360 px without sideways scrolling, NL strings", async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/nl/nl?role=second&budget=20000");
  await expect(page.getByTestId("hero-card")).toHaveCount(10);
  await expect(page.getByTestId("hero-shortlist")).toContainText("Jouw shortlist");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(0);
});

test("hero: Nerd shows how the score is built", async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.goto("/nl/en?role=only&trips=monthly&level=nerd");
  await expect(page.getByTestId("hero-nerd").first()).toContainText("Score");
  // The scores are the release's own (Decision 065), and Nerd mode says so.
  await expect(page.getByTestId("hero-nerd-source").first()).toContainText("shortlist_scores.json");
});

test("hero: links the launch /learn guides that exist", async ({ page }) => {
  await page.goto("/nl/en?role=main&trips=never");
  const learn = page.getByTestId("hero-learn");
  await expect(learn.getByRole("link", { name: "Winter range explained" })).toHaveAttribute("href", "/nl/en/learn/winter-range");
  await expect(learn.getByRole("link")).toHaveCount(3);
  // T-082 published the battery guide as batteries-health.
  await expect(learn.getByRole("link").nth(2)).toHaveAttribute("href", "/nl/en/learn/batteries-health");
});

test("hero: the keep-8 checkbox is named by its label only (the ⓘ sits outside it)", async ({ page }) => {
  await page.goto("/nl/en?role=main&trips=never");
  await expect(page.getByRole("checkbox", { name: "I want to keep it 8 years or more", exact: true })).toHaveCount(1);
});

test("hero: Dutch Nerd score table fits a 360 px phone (verify-web found 7 px overflow)", async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/nl/nl?role=only&trips=monthly&level=nerd");
  await expect(page.getByTestId("hero-nerd").first()).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(0);
  // Numbers stay whole ("1.161,6", never "1.161," / "6") and the table isn't cut off in its card.
  const table = await page.evaluate(() => {
    const box = document.querySelector('[data-testid="hero-nerd"] table')!.parentElement!;
    const cells = [...box.querySelectorAll("td")].filter((td) => /\d/.test(td.textContent ?? ""));
    const lines = (td: Element) => {
      const r = document.createRange();
      r.selectNodeContents(td);
      return new Set([...r.getClientRects()].map((x) => Math.round(x.top))).size;
    };
    return { clipped: box.scrollWidth - box.clientWidth, numberCells: cells.length, split: cells.filter((td) => lines(td) > 1).length };
  });
  expect(table.numberCells).toBeGreaterThan(0);
  expect(table.split).toBe(0);
  expect(table.clipped).toBeLessThanOrEqual(0);
});
