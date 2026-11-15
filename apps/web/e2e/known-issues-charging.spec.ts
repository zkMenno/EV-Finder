// T-061: known issues (RDW APK defects) on generation pages, EPA range on variant/compare pages,
// generation-year badges (Wikidata), and the charging statistics page. Runs on the published
// release (data/releases/latest), like the static pages it checks.
import { expect, test } from "@playwright/test";

const RDW = "Dutch vehicle register (RDW open data, CC0)";

test.describe("known issues", () => {
  test("cohorts compare only with all EVs of the same year; source wording per Q-037", async ({ page }) => {
    await page.goto("/nl/en/ev/renault/zoe/ph1");
    const ki = page.getByTestId("known-issues");
    await expect(ki.getByRole("heading", { level: 2 })).toContainText("Known issues");
    const cohorts = ki.getByTestId("ki-cohort");
    expect(await cohorts.count()).toBeGreaterThan(0);
    for (const c of await cohorts.all()) {
      const year = await c.getAttribute("data-year");
      // The only baseline in a cohort is its own first-registration year.
      await expect(c.getByTestId("ki-any")).toContainText(`all EVs of ${year}`);
      await expect(c.getByTestId("ki-table").locator("thead")).toContainText(`All EVs of ${year}`);
      const other = String(Number(year) + 1);
      await expect(c.getByTestId("ki-any")).not.toContainText(`of ${other}`);
    }
    await expect(ki.getByTestId("ki-source")).toContainText(RDW);
    await expect(ki).not.toContainText("Bron: RDW");
    await expect(ki).toContainText("Dutch wording");
    // Labels are RDW's Dutch text, marked as Dutch for screen readers.
    await expect(ki.locator('[lang="nl"]').first()).toBeVisible();
  });

  test("young cohorts with few reports say so and show no rates", async ({ page }) => {
    await page.goto("/nl/en/ev/tesla/model-y/gen1");
    const hidden = page.getByTestId("ki-cohort-hidden").filter({ has: page.locator("h3") });
    await expect(hidden.first()).toBeVisible();
    await expect(hidden.first()).toContainText("Not enough inspections yet");
    await expect(hidden.first().getByTestId("ki-table")).toHaveCount(0);
    await expect(hidden.first().getByTestId("ki-any")).toHaveCount(0);
  });

  test("Simple shows the top 3 codes, Nerd adds codes and sample sizes", async ({ page }) => {
    await page.goto("/nl/en/ev/renault/zoe/ph1?level=simple");
    const first = page.getByTestId("ki-cohort").first();
    await expect(first.getByTestId("ki-defect")).toHaveCount(3);
    await expect(page.getByTestId("ki-nerd")).toHaveCount(0);
    await page.goto("/nl/en/ev/renault/zoe/ph1?level=nerd");
    const nerd = page.getByTestId("ki-cohort").first();
    expect(await nerd.getByTestId("ki-defect").count()).toBeGreaterThan(3);
    await expect(nerd.getByTestId("ki-nerd")).toContainText("Sampled cars");
    await expect(nerd.getByRole("columnheader", { name: "Code" })).toBeVisible();
    await expect(page.getByTestId("ki-method")).toContainText("Rate basis");
  });

  test("Dutch page is translated", async ({ page }) => {
    await page.goto("/nl/nl/ev/renault/zoe/ph1");
    await expect(page.getByTestId("known-issues").getByRole("heading", { level: 2 })).toContainText("Bekende gebreken bij de APK");
    await expect(page.getByTestId("ki-cohort").first().getByTestId("ki-any")).toContainText("alle EV's uit");
  });
});

test.describe("EPA range", () => {
  test("variant page shows EPA as its own row, separate from WLTP", async ({ page }) => {
    await page.goto("/nl/en/ev/audi/e-tron/ge/s");
    const epa = page.getByRole("row", { name: /EPA range \(US test\)/ });
    const wltp = page.getByRole("row", { name: /Official range \(WLTP\)/ });
    await expect(epa).toHaveCount(1);
    await expect(wltp).toHaveCount(1);
    await expect(epa).toContainText("298");
    await expect(wltp).toContainText("357");
  });

  test("compare shows the EPA row; Explore keeps WLTP only", async ({ page }) => {
    await page.goto("/nl/en/compare?ids=audi-e-tron-ge-s,renault-zoe-ph1-r240");
    await expect(page.getByRole("row", { name: /EPA range \(US test\)/ })).toHaveCount(1);
    await page.goto("/nl/en?view=table&level=nerd");
    await expect(page.getByTestId("explore-row").first()).toBeVisible();
    await expect(page.getByRole("columnheader", { name: /EPA/ })).toHaveCount(0);
    await expect(page.getByRole("columnheader", { name: /Real-world range/ }).first()).toBeVisible();
  });
});

test.describe("generation-year badges", () => {
  test("corroborated, disagrees (Nerd detail) and not yet checked stay consistent across pages", async ({ page }) => {
    await page.goto("/nl/en/ev/hyundai/ioniq-5/gen1");
    await expect(page.getByTestId("years-badge")).toHaveAttribute("data-kind", "corroborated");
    await expect(page.getByTestId("years-badge")).toContainText("years checked against Wikidata");

    await page.goto("/nl/en/ev/skoda/enyaq/gen1");
    await expect(page.getByTestId("years-badge")).toHaveAttribute("data-kind", "disagrees");
    await expect(page.getByTestId("years-nerd")).toHaveCount(0);
    await page.goto("/nl/en/ev/skoda/enyaq/gen1?level=nerd");
    await expect(page.getByTestId("years-nerd")).toContainText("2017");

    await page.goto("/nl/en/ev/audi/e-tron/ge");
    await expect(page.getByTestId("years-badge")).toHaveAttribute("data-kind", "unchecked");
    await page.goto("/nl/en/ev/audi/e-tron/ge/s");
    await expect(page.getByTestId("years-badge")).toHaveAttribute("data-kind", "unchecked");
    await page.goto("/nl/en/ev/skoda/enyaq");
    await expect(page.getByTestId("years-badge").first()).toHaveAttribute("data-kind", "disagrees");
  });
});

test.describe("charging statistics page", () => {
  test("Germany: over time + by power band, table fallback, source, licence and period", async ({ page }) => {
    await page.goto("/de/en/charging");
    await expect(page.locator("h1")).toContainText("Charging network in numbers");
    const block = page.getByTestId("charging-block").first();
    await expect(block.getByTestId("charging-chart")).toHaveCount(2);
    await expect(block.getByTestId("charging-chart").first()).toHaveAttribute("role", "img");
    await expect(block.getByTestId("chart-legend")).toBeVisible();
    await block.getByText("Show the numbers as a table").click();
    const table = block.getByTestId("charging-table");
    await expect(table).toBeVisible();
    expect(await table.locator("tbody tr").count()).toBeGreaterThan(30);
    const src = block.getByTestId("charging-source");
    await expect(src).toContainText("Bundesnetzagentur");
    await expect(src).toContainText("CC BY 4.0");
    await expect(src).toContainText("2017");
  });

  test("UK: one block per metric and definition, OGL credit", async ({ page }) => {
    await page.goto("/uk/en/charging");
    const blocks = page.getByTestId("charging-block");
    expect(await blocks.count()).toBeGreaterThanOrEqual(2);
    await expect(blocks.first().getByTestId("charging-source")).toContainText("Open Government Licence");
    // Series notes from the source (e.g. the July 2026 data clean-up) are listed once per chart.
    await expect(blocks.first().getByTestId("charging-notes")).toContainText("charge point operator");
    await page.goto("/uk/en/charging?level=simple");
    await expect(page.getByTestId("charging-chart").first()).toBeVisible();
    await expect(page.getByTestId("charging-notes")).toHaveCount(0);
  });

  test("other countries: no open data yet", async ({ page }) => {
    await page.goto("/fr/fr/charging");
    await expect(page.getByTestId("charging-none")).toBeVisible();
    await expect(page.getByTestId("charging-chart")).toHaveCount(0);
  });

  test("linked from the charging links block on Explore", async ({ page }) => {
    await page.goto("/nl/en");
    const link = page.getByTestId("charging-stats-link");
    await expect(link).toHaveAttribute("href", "/nl/en/charging");
  });
});
