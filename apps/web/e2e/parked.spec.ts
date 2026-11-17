import { expect, test } from "@playwright/test";

// Decision 051: parked features stay in the code but are off unless built with PARKED=1.
test.skip(process.env.E2E_PARKED === "1", "this build has parked features on");

test("parked features are hidden: rankings, charging page and links, known issues, registrations", async ({ page, request }) => {
  expect((await request.get("/nl/en/top")).status()).toBe(404);
  expect((await request.get("/nl/en/top/fastest-dc")).status()).toBe(404);
  expect((await request.get("/de/en/charging")).status()).toBe(404);
  await page.goto("/nl/en");
  await expect(page.getByTestId("charging-links")).toHaveCount(0);
  await page.goto("/nl/en/ev/renault/zoe/ph1");
  await expect(page.locator("h1")).toBeVisible();
  await expect(page.getByTestId("known-issues")).toHaveCount(0);
  await expect(page.getByTestId("charging-links")).toHaveCount(0);
  const sitemap = await (await request.get("/sitemap.xml")).text();
  expect(sitemap).not.toMatch(/\/[a-z]{2}\/[a-z]{2}\/(top|charging)(<|\/)/);
});
