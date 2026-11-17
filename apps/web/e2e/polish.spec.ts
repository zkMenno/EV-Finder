// Wave 5 polish: glossary links in number popovers, Explore polish (cards at 360 px, sticky header,
// keyboard focus, empty state with a reason), Compare (share link, print view, differences only),
// and the hidden used-price rankings.
import { expect, test } from "@playwright/test";

test("Num popover links its badges to the glossary", async ({ page }) => {
  await page.goto("/nl/en/ev/renault/zoe/ph1/r240");
  const num = page.locator("main table td button[aria-describedby]").first();
  await num.focus();
  const tip = page.locator(`[id="${await num.getAttribute("aria-describedby")}"]`);
  await expect(tip).toBeVisible();
  await expect(tip.getByTestId("num-term-confidence")).toHaveAttribute("href", "/nl/en/learn/confidence");
  await expect(tip.getByTestId("num-term-release")).toHaveAttribute("href", "/nl/en/learn/data-release");
});

test("Explore cards at 360 px: no sideways scroll, every card readable", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  for (const level of ["simple", "detailed", "nerd"]) {
    await page.goto(`/nl/en?view=cards&level=${level}`);
    await expect(page.getByTestId("explore-card").first()).toBeVisible();
    await expect(page.getByTestId("result-count")).not.toContainText("…");
    const [sw, iw] = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
    expect(sw, `page wider than the phone at level ${level}`).toBeLessThanOrEqual(iw);
    const card = await page.getByTestId("explore-card").first().boundingBox();
    expect(card!.x).toBeGreaterThanOrEqual(0);
    expect(card!.x + card!.width).toBeLessThanOrEqual(360);
  }
});

test("Explore table: header row stays visible while scrolling; page itself never scrolls sideways", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/nl/en?view=table");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  const [sw, iw] = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  expect(sw).toBeLessThanOrEqual(iw);
  const scroller = page.getByTestId("explore-scroll");
  await scroller.evaluate((el) => (el.scrollTop = 600));
  const box = await scroller.boundingBox();
  const th = await page.getByTestId("explore-table").locator("thead th").nth(1).boundingBox();
  expect(Math.abs(th!.y - box!.y)).toBeLessThan(4);
});

test("Explore keyboard: logical Tab order into the table with a visible focus ring", async ({ page }) => {
  await page.goto("/nl/en?view=table");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  const scroller = page.getByTestId("explore-scroll");
  await scroller.focus();
  const outline = async () =>
    page.evaluate(() => {
      const s = getComputedStyle(document.activeElement as Element);
      return { style: s.outlineStyle, width: parseFloat(s.outlineWidth) };
    });
  expect(await outline()).toEqual({ style: "solid", width: 3 });
  // Next stops: the sortable headers, then the first row's heart, compare and name link.
  const seen: string[] = [];
  for (let i = 0; i < 40; i++) {
    await page.keyboard.press("Tab");
    const o = await outline();
    expect(o.style, "every Tab stop shows a focus ring").toBe("solid");
    const tid = await page.evaluate(() => (document.activeElement as HTMLElement).dataset.testid ?? document.activeElement!.tagName);
    seen.push(tid);
    if (tid === "compare-toggle") break;
  }
  expect(seen).toContain("compare-toggle");
  // The headers come before any row control.
  expect(seen.indexOf("BUTTON")).toBeLessThan(seen.indexOf("compare-toggle"));
});

test("Explore empty state names the most restrictive filter and removes it", async ({ page }) => {
  await page.goto("/nl/en?range=900&volt=800v");
  const empty = page.getByTestId("explore-empty");
  await expect(empty).toContainText(/No cars match: remove the “Min real range \(km\)” filter to see \d+/);
  await empty.getByTestId("explore-empty-remove").click();
  await expect(page).not.toHaveURL(/range=900/);
  await expect(page).toHaveURL(/volt=800v/);
  await expect(page.getByTestId("explore-row").first()).toBeVisible();
});

test("Compare: share copies the link, differences only keeps the price mode, print view hides chrome", async ({ page, context, baseURL }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"], { origin: new URL(baseURL!).origin });
  const url = "/nl/en/compare?ids=renault-zoe-ph1-r240,renault-zoe-ph2-r135&pay=loan";
  await page.goto(url);
  const table = page.getByTestId("compare-table");
  const allRows = await table.locator("tbody tr[data-differs], tbody tr:not([data-differs]):has(td)").count();

  // Share: the exact page URL lands on the clipboard and the status says so.
  await page.getByTestId("compare-share").click();
  await expect(page.getByRole("status").filter({ hasText: /copied/i })).toBeVisible();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(new URL(url, baseURL).href);

  // Differences only: fewer rows, every row differs, price mode kept; and back.
  await page.getByTestId("compare-diff-toggle").click();
  await expect(page).toHaveURL(/diff=1/);
  await expect(page).toHaveURL(/pay=loan/);
  const diffRows = table.locator("tbody tr:has(td)");
  const n = await diffRows.count();
  expect(n).toBeGreaterThan(0);
  expect(n).toBeLessThan(allRows);
  for (let i = 0; i < n; i++) await expect(diffRows.nth(i).locator("td[data-differs]").first()).toBeAttached();
  await page.getByTestId("compare-diff-toggle").click();
  await expect(page).not.toHaveURL(/diff=1/);

  // Print view: no header, nav, tray or buttons; the table fits the page width.
  await page.emulateMedia({ media: "print" });
  await expect(page.locator("body > header")).toBeHidden();
  await expect(page.getByTestId("compare-share")).toBeHidden();
  await expect(page.getByTestId("compare-diff-toggle")).toBeHidden();
  await expect(table).toBeVisible();
  const [tw, vw] = await page.evaluate(() => [document.querySelector("[data-testid=compare-table]")!.scrollWidth, document.documentElement.clientWidth]);
  expect(tw).toBeLessThanOrEqual(vw);
});

test("Used-price rankings are hidden while no list has 5 priced cars (release 1)", async ({ page }) => {
  test.skip(process.env.E2E_PARKED !== "1", "rankings are parked (Decision 051)");
  for (const cap of ["15k", "20k", "25k"]) {
    const res = await page.goto(`/nl/en/top/best-used-under-${cap}`);
    expect(res?.status()).toBe(404);
  }
  await page.goto("/nl/en/top");
  await expect(page.getByTestId("used-ranking-link")).toHaveCount(0);
  const sitemap = await (await page.request.get("/sitemap.xml")).text();
  expect(sitemap).not.toContain("best-used");
});
