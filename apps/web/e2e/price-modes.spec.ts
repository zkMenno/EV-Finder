import { expect, test } from "@playwright/test";

// T-043 / Decision 017: price modes, the loan calculator and the lease placeholder.

test("Explore: loan mode is in the URL and remembered; NL asks for a rate (no sourced default)", async ({ page }) => {
  await page.goto("/nl/nl/cars?view=table");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  const mode = page.getByTestId("pay-mode");
  await mode.getByRole("button", { name: "Lening per maand" }).click();
  await expect(page).toHaveURL(/[?&]pay=loan/);
  const box = page.getByTestId("loan-box");
  await expect(box).toBeVisible();
  // CCD2 warning in Dutch, and "estimate, not an offer".
  await expect(page.getByTestId("loan-warning")).toContainText("Let op! Geld lenen kost geld.");
  await expect(page.getByTestId("loan-warning")).toContainText("geen aanbod");
  // No NL rate with a source: the field is empty and asks; no monthly figures yet.
  await expect(page.getByTestId("loan-apr")).toHaveValue("");
  await expect(box).toContainText("vul er een in");
  await expect(page.getByTestId("explore-table")).not.toContainText("/maand");

  // Enter a rate: monthly estimates appear, with term/deposit labelled as assumptions.
  await page.getByTestId("loan-apr").fill("7");
  await page.getByTestId("loan-apr").press("Enter");
  await expect(page.getByTestId("explore-table")).toContainText("/maand");
  await expect(box).toContainText("aanname, pas aan");
  await expect(page.getByTestId("loan-assumptions")).toContainText("48 maanden");

  // Reload: mode (URL) and rate (localStorage) come back; without ?pay the remembered mode wins.
  await page.reload();
  await expect(page.getByTestId("loan-apr")).toHaveValue("7");
  await page.goto("/nl/nl/cars?view=table");
  await expect(page.getByTestId("pay-mode").getByRole("button", { pressed: true })).toHaveText("Lening per maand");
  await expect(page).toHaveURL(/[?&]pay=loan/);
});

test("Variant page (DE): sourced APR, monthly amount, total over the term; Nerd shows formula + source", async ({ page }) => {
  await page.goto("/de/en/cars?view=table");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  const href = await page.getByTestId("explore-row").first().getByRole("rowheader").getByRole("link").getAttribute("href");
  await page.goto(`${href}?pay=loan&level=nerd`);
  const panel = page.getByTestId("price-panel");
  await expect(panel.getByTestId("loan-box")).toBeVisible();
  await expect(page.getByTestId("loan-apr")).toHaveValue("8.91");
  await expect(panel).toContainText("typical national rate");
  const monthly = panel.getByTestId("loan-monthly");
  if (await monthly.count()) {
    await expect(monthly).toContainText("€");
    await expect(panel.getByTestId("loan-total")).toContainText("€");
  } else {
    await expect(panel).toContainText("No price for this car");
  }
  await expect(page.getByTestId("loan-nerd")).toContainText("(1 + APR)^(1/12)");
  await expect(page.getByTestId("loan-nerd")).toContainText("MIR.M.DE");
  await expect(page.getByTestId("loan-warning")).toContainText("Borrowing money costs money.");
});

test("Lease mode: a labelled placeholder, no figures; none at all in the UK", async ({ page }) => {
  await page.goto("/nl/en/cars?view=table&pay=lease");
  await expect(page.getByTestId("lease-notice")).toBeVisible();
  await expect(page.getByTestId("lease-link-placeholder")).toHaveText("Lease offers for this car");
  await expect(page.getByTestId("explore-table")).not.toContainText("€");
  await page.goto("/uk/en/cars?view=table&pay=lease");
  await expect(page.getByTestId("lease-notice")).toHaveText(/not available in the UK/);
  await expect(page.getByTestId("lease-link-placeholder")).toHaveCount(0);
});

test("Compare: one loan box, a monthly estimate per car", async ({ page }) => {
  await page.goto("/fr/en/compare?ids=nissan-leaf-ze1-40kwh,renault-zoe-ph2-r135&pay=loan");
  await expect(page.getByTestId("loan-box")).toHaveCount(1);
  await expect(page.getByTestId("loan-per-car").getByRole("listitem")).toHaveCount(2);
});
