// T-143 follow-up (pre-existing): at 1280 px a Nerd row's "Sources" popover that opens upward sat
// under the table's sticky header. The row header cell is sticky with its own z-index, so the
// popover (fixed, z-50) was stacked inside it, below the column headers. It must be on top.
import { expect, test } from "@playwright/test";

test("Sources popover that opens upward is not covered by the sticky table header (1280 px)", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto("/nl/en/cars?view=table&level=nerd");
  await expect(page.getByTestId("explore-row").first()).toBeVisible();
  await expect(page.getByTestId("result-count")).not.toContainText("…");

  // Put the table's header near the bottom of the window, so the first row's popover has no room
  // below and opens upward, across the header.
  const scroller = page.getByTestId("explore-scroll");
  const top = await scroller.evaluate((el) => el.getBoundingClientRect().top + window.scrollY);
  await page.evaluate((y) => window.scrollTo(0, y), top - 680);
  // The popover closes on scroll: let the scroll event fire before opening it.
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  const sources = page.getByTestId("explore-row").first().getByTestId("row-sources");
  await sources.focus(); // focus, not hover: a tall popover can cover its own button and close on mouseleave
  const pop = page.locator(`[id="${await sources.getAttribute("aria-describedby")}"]`);
  await expect(pop).toBeVisible();

  const head = await page.getByTestId("explore-table").locator("thead th").nth(1).boundingBox();
  const box = await pop.boundingBox();
  expect(head && box).toBeTruthy();
  // The popover opened upward and overlaps the header row …
  expect(box!.y).toBeLessThan(head!.y + head!.height);
  expect(box!.y + box!.height).toBeGreaterThan(head!.y);
  // … and wins there: the topmost element in the overlap belongs to the popover.
  const x = box!.x + box!.width / 2;
  const y = Math.max(box!.y, head!.y) + Math.min(head!.height, box!.y + box!.height - Math.max(box!.y, head!.y)) / 2;
  const onTop = await page.evaluate(
    ([px, py, id]) => !!document.elementFromPoint(px as number, py as number)?.closest(`[id="${id}"]`),
    [x, y, await sources.getAttribute("aria-describedby")] as const,
  );
  expect(onTop, "the sticky header covers the Sources popover").toBe(true);
});
