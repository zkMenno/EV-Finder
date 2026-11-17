import { expect, test } from "@playwright/test";

// T-080: the landing-page hero ranks the published release for each profile.
const PROFILES: [string, string][] = [
  ["road-tripper", "role=only&trips=monthly&charge=home"],
  ["daily driver", "role=main&trips=never&charge=home"],
  ["runabout", "role=second&charge=home"],
  ["kerbside charger", "role=only&trips=often&charge=public_only&area=city"],
];

for (const [name, qs] of PROFILES) {
  test(`hero: ${name} gets a top 10 with the first 5 as the shortlist`, async ({ page }) => {
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
  await expect(page.getByTestId("hero-card").first()).toBeVisible();
  await expect(page).toHaveURL(/role=second/);
});

test("hero: changing the budget re-ranks without a reload", async ({ page }) => {
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
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/nl/nl?role=second&budget=20000");
  await expect(page.getByTestId("hero-card")).toHaveCount(10);
  await expect(page.getByTestId("hero-shortlist")).toContainText("Jouw shortlist");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(0);
});

test("hero: Nerd shows how the score is built", async ({ page }) => {
  await page.goto("/nl/en?role=only&trips=monthly&level=nerd");
  await expect(page.getByTestId("hero-nerd").first()).toContainText("Score");
});

test("hero: Nerd value column shows the car's own fast-charge figure in km (T-097)", async ({ page }) => {
  await page.goto("/nl/en?role=only&trips=monthly&level=nerd");
  const card = page.getByTestId("hero-card").first();
  const cell = card.getByTestId("hero-nerd-value-dc-speed");
  await expect(cell).toContainText("km");
  const nerd = (await cell.textContent()) ?? "";
  // Same figure as the card's own "fast charging (N km in 20 min)" line, not the ×3 km/h score unit.
  const why = (await card.getByTestId("hero-why").textContent()) ?? "";
  const own = why.match(/([\d,.]+) km in 20 min/)?.[1];
  expect(own, `card why line: ${why}`).toBeTruthy();
  expect(nerd).toBe(`${own} km in 20 min`);
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

// Every served language, every card: German compounds and units are wider than Dutch (T-097 review
// found 18 px). Only routes that are served (countries config); /nl/de would 308 to /nl/nl, so the
// test fails if a route redirects. ES/IT join once T-119 serves them.
for (const route of ["nl/nl", "nl/en", "de/de", "fr/fr", "be/fr", "be/de"]) test(`hero: ${route} Nerd score table fits a 360 px phone (verify-web found 7 px overflow)`, async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto(`/${route}?role=only&trips=monthly&level=nerd`);
  expect(new URL(page.url()).pathname, "route was redirected, so this language isn't really tested").toBe(`/${route}`);
  await expect(page.getByTestId("hero-nerd").first()).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(0);
  // Numbers stay whole ("1.161,6", never "1.161," / "6") and the table isn't cut off in its card.
  // A value's unit may wrap ("387 km" / "in 20 min", T-097), so this measures each number, not each cell.
  const table = await page.evaluate(() => {
    const boxes = [...document.querySelectorAll('[data-testid="hero-nerd"] table')].map((t) => t.parentElement!);
    const cells = boxes.flatMap((box) => [...box.querySelectorAll("td")]).filter((td) => /\d/.test(td.textContent ?? ""));
    let split = 0;
    for (const td of cells) {
      const walker = document.createTreeWalker(td, NodeFilter.SHOW_TEXT);
      for (let n = walker.nextNode(); n; n = walker.nextNode()) {
        for (const m of (n.textContent ?? "").matchAll(/\d[\d.,\u202f\u00a0]*/g)) {
          const r = document.createRange();
          r.setStart(n, m.index!);
          r.setEnd(n, m.index! + m[0].length);
          if (new Set([...r.getClientRects()].map((x) => Math.round(x.top))).size > 1) split++;
        }
      }
    }
    return { clipped: Math.max(...boxes.map((b) => b.scrollWidth - b.clientWidth)), numberCells: cells.length, split };
  });
  expect(table.numberCells).toBeGreaterThan(0);
  expect(table.split).toBe(0);
  expect(table.clipped).toBeLessThanOrEqual(0);
});
