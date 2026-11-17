// axe-core accessibility check (Wave 5 polish): key pages × both themes (Day trip / Night drive).
// Fails on critical and serious violations; moderate and minor ones are recorded in
// audits/A-04-accessibility.md (the summary per page is attached to the test report).
import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

// width: phone checks at 360 px (T-096: the Dutch card view only showed its label problems there).
const ALL_PAGES: { name: string; path: string; ready: (p: Page) => Promise<void>; parked?: boolean; width?: number }[] = [
  {
    name: "explore-table",
    path: "/nl/en?view=table",
    ready: async (p) => {
      await expect(p.getByTestId("explore-row").first()).toBeVisible();
      await expect(p.getByTestId("result-count")).not.toContainText("…");
    },
  },
  {
    name: "explore-cards",
    path: "/nl/en?view=cards",
    ready: async (p) => {
      await expect(p.getByTestId("result-count")).not.toContainText("…");
    },
  },
  { name: "explore-nl-nerd-table", path: "/nl/nl?view=table&level=nerd", ready: async (p) => void (await expect(p.getByTestId("result-count")).not.toContainText("…")) },
  { name: "generation", path: "/nl/en/ev/renault/zoe/ph1", ready: async (p) => void (await expect(p.locator("h1")).toBeVisible()) },
  { name: "variant", path: "/nl/en/ev/renault/zoe/ph1/r240", ready: async (p) => void (await expect(p.locator("h1")).toBeVisible()) },
  {
    name: "compare",
    path: "/nl/en/compare?ids=renault-zoe-ph1-r240,renault-zoe-ph2-r135",
    ready: async (p) => void (await expect(p.locator("h1")).toBeVisible()),
  },
  // T-096: the hero with answers (cards, compare buttons, Nerd table) in EN and NL.
  { name: "hero-en-nerd", path: "/nl/en?role=only&trips=monthly&level=nerd", ready: async (p) => void (await expect(p.getByTestId("hero-nerd").first()).toBeVisible()) },
  { name: "hero-nl", path: "/nl/nl?role=second&budget=20000", ready: async (p) => void (await expect(p.getByTestId("hero-card").first()).toBeVisible()) },
  { name: "hero-nl-360", width: 360, path: "/nl/nl?role=second&budget=20000", ready: async (p) => void (await expect(p.getByTestId("hero-card").first()).toBeVisible()) },
  { name: "hero-en-nerd-360", width: 360, path: "/nl/en?role=only&trips=monthly&level=nerd", ready: async (p) => void (await expect(p.getByTestId("hero-nerd").first()).toBeVisible()) },
  // Dutch compare buttons: "Vergelijk" must be inside the name (Label in Name), cards and variant page.
  { name: "explore-cards-nl", path: "/nl/nl?view=cards", ready: async (p) => void (await expect(p.getByTestId("result-count")).not.toContainText("…")) },
  { name: "explore-cards-nl-360", width: 360, path: "/nl/nl?view=cards", ready: async (p) => void (await expect(p.getByTestId("result-count")).not.toContainText("…")) },
  { name: "variant-nl", path: "/nl/nl/ev/renault/zoe/ph1/r240", ready: async (p) => void (await expect(p.locator("h1")).toBeVisible()) },
  { name: "open-data", path: "/nl/en/data", ready: async (p) => void (await expect(p.locator("h1")).toBeVisible()) },
  { name: "learn-article", path: "/nl/en/learn/winter-range", ready: async (p) => void (await expect(p.locator("h1")).toBeVisible()) },
  { name: "rankings", parked: true, path: "/nl/en/top/fastest-dc", ready: async (p) => void (await expect(p.locator("h1")).toBeVisible()) },
  // T-061: known issues (Nerd: code + sample columns), years badge detail, charging charts.
  { name: "generation-known-issues-nerd", parked: true, path: "/nl/nl/ev/skoda/enyaq/gen1?level=nerd", ready: async (p) => void (await expect(p.getByTestId("years-nerd")).toBeVisible()) },
  {
    name: "charging-de",
    parked: true,
    path: "/de/en/charging",
    ready: async (p) => {
      await expect(p.getByTestId("charging-chart").first()).toBeVisible();
      await p.getByText("Show the numbers as a table").first().click();
    },
  },
  { name: "charging-uk-nerd", parked: true, path: "/uk/en/charging?level=nerd", ready: async (p) => void (await expect(p.getByTestId("charging-chart").first()).toBeVisible()) },
  { name: "charging-none", parked: true, path: "/fr/fr/charging", ready: async (p) => void (await expect(p.getByTestId("charging-none")).toBeVisible()) },
];
// Parked features (Decision 051) are only checked when built with PARKED=1 (E2E_PARKED=1).
const PAGES = ALL_PAGES.filter((p) => !p.parked || process.env.E2E_PARKED === "1");

for (const theme of ["light", "dark"] as const) {
  for (const pg of PAGES) {
    test(`axe: ${pg.name} (${theme})`, async ({ page }, info) => {
      await page.emulateMedia({ colorScheme: theme });
      if (pg.width) await page.setViewportSize({ width: pg.width, height: 800 });
      await page.goto(pg.path);
      await pg.ready(page);
const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]).analyze();
      const summary = results.violations.map((v) => ({
        id: v.id,
        impact: v.impact,
        nodes: v.nodes.length,
        help: v.help,
        targets: v.nodes.slice(0, 3).map((n) => n.target.join(" ")),
      }));
      await info.attach("axe-summary.json", { body: JSON.stringify({ page: pg.name, theme, summary }, null, 2), contentType: "application/json" });
      if (process.env.AXE_REPORT) console.log(`AXE ${pg.name} ${theme} ${JSON.stringify(summary)}`);
      const blocking = summary.filter((v) => v.impact === "critical" || v.impact === "serious");
      expect(blocking, `critical/serious axe violations on ${pg.path} (${theme})`).toEqual([]);
    });
  }
}

test("theme toggle: Night drive is remembered across reloads and pages", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "light" });
  await page.goto("/nl/en");
  const toggle = page.getByTestId("theme-toggle");
  await expect(toggle).toHaveAttribute("aria-pressed", "false");
  await toggle.click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(toggle).toHaveAttribute("aria-pressed", "true");
  const bg = () => page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  expect(await bg()).toBe("rgb(17, 26, 43)");
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  // Static page too (CSP: /theme-init.js is same-origin, not inline).
  await page.goto("/nl/en/learn/winter-range");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  expect(await bg()).toBe("rgb(17, 26, 43)");
  await page.getByTestId("theme-toggle").click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  expect(await bg()).toBe("rgb(255, 255, 255)");
});

test("theme follows the system when nothing is stored", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await page.goto("/nl/en/about");
  await expect(page.locator("html")).not.toHaveAttribute("data-theme", /./);
  expect(await page.evaluate(() => getComputedStyle(document.body).backgroundColor)).toBe("rgb(17, 26, 43)");
  await expect(page.getByTestId("theme-toggle")).toHaveAttribute("aria-pressed", "true");
});
