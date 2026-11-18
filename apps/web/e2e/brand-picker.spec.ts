import { expect, test, type Page } from "@playwright/test";

// T-141: the hero's Ariakit brand picker. Focus regressions were found twice in review, so they
// are pinned here: removing a chip must never drop keyboard focus onto <body>.

const HERO = "/nl/en?role=only&trips=monthly&charge=home&area=town";

async function openRefine(page: Page, query = "") {
  await page.goto(HERO + query);
  await page.getByTestId("hero-refine").locator("summary").click();
  await expect(page.getByTestId("hero-brands-input")).toBeVisible();
}

test("typing narrows the list; Enter picks the first match into the URL and a chip", async ({ page }) => {
  await openRefine(page);
  const input = page.getByTestId("hero-brands-input");
  await input.click();
  await page.keyboard.type("tes");
  await expect(page.getByTestId("hero-brands-list").getByRole("option")).toHaveCount(1);
  await page.keyboard.press("Enter");
  await page.keyboard.press("Escape");
  await expect(page).toHaveURL(/make=tesla/);
  await expect(page.getByTestId("hero-brands").getByRole("button", { name: "Remove Tesla" })).toBeVisible();
});

test("removing a chip moves focus to the next chip, then the previous, then the input", async ({ page }) => {
  await openRefine(page, "&make=kia,tesla,volkswagen");
  const chips = page.getByTestId("hero-brands").getByRole("listitem").getByRole("button");
  await expect(chips).toHaveCount(3);

  await page.getByRole("button", { name: "Remove Tesla" }).press("Enter"); // middle → next
  await expect(page.getByRole("button", { name: "Remove Volkswagen" })).toBeFocused();

  await page.keyboard.press("Enter"); // last → previous
  await expect(page.getByRole("button", { name: "Remove Kia" })).toBeFocused();

  await page.keyboard.press("Enter"); // only chip → the input (not <body>)
  await expect(page.getByTestId("hero-brands-input")).toBeFocused();
  await expect(page).not.toHaveURL(/make=/);
});

test("removing the only excluded brand by click returns focus to its input", async ({ page }) => {
  await openRefine(page, "&xmake=bmw");
  await page.getByTestId("hero-xbrands").getByRole("button", { name: "Remove BMW" }).click();
  await expect(page.getByTestId("hero-xbrands-input")).toBeFocused();
  await expect(page).not.toHaveURL(/xmake=/);
});
