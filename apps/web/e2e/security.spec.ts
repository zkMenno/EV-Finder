import { expect, test, type Page } from "@playwright/test";

// A-01 / A-02 web items: strict CSP (no 'unsafe-inline' for scripts) on static and dynamic pages,
// and pages still work under it (no violations, client components hydrate).

function watchViolations(page: Page): string[] {
  const out: string[] = [];
  page.on("console", (m) => {
    if (/Content Security Policy|Refused to (execute|load)/i.test(m.text())) out.push(m.text());
  });
  return out;
}

async function scriptSrc(page: Page, path: string): Promise<string> {
  const res = await page.goto(path);
  expect(res?.status(), path).toBe(200);
  const csp = res!.headers()["content-security-policy"] ?? "";
  return csp.split("; ").find((d) => d.startsWith("script-src")) ?? "";
}

test("Static pages: hash-based CSP, no nonce, no 'unsafe-inline'; the page hydrates", async ({ page }) => {
  const violations = watchViolations(page);
  const src = await scriptSrc(page, "/nl/en/learn/real-range");
  expect(src).toMatch(/'sha256-[A-Za-z0-9+/=]+'/);
  expect(src).not.toContain("unsafe-inline");
  expect(src).not.toContain("nonce-");
  // Hydrated: the language switcher (client component) navigates.
  await page.getByRole("combobox", { name: /Language/ }).selectOption("nl");
  await expect(page).toHaveURL(/\/nl\/nl\/learn\/real-range$/);
  expect(violations).toEqual([]);
});

test("Dynamic pages: a fresh nonce per request, no 'unsafe-inline'; Explore works", async ({ page }) => {
  const violations = watchViolations(page);
  const a = await scriptSrc(page, "/nl/en");
  expect(a).toMatch(/'nonce-[A-Za-z0-9+/=]+'/);
  expect(a).not.toContain("unsafe-inline");
  await expect(page.getByTestId("result-count")).not.toContainText("…");
  await page.getByTestId("compare-toggle").first().click();
  await expect(page.getByTestId("compare-tray").getByRole("listitem")).toHaveCount(1);
  const b = await scriptSrc(page, "/nl/en");
  expect(b).not.toBe(a);
  expect(violations).toEqual([]);
});

test("Security headers are set", async ({ request }) => {
  const h = (await request.get("/nl/nl/top")).headers();
  expect(h["x-content-type-options"]).toBe("nosniff");
  expect(h["x-frame-options"]).toBe("DENY");
  expect(h["referrer-policy"]).toBe("strict-origin-when-cross-origin");
  expect(h["content-security-policy"]).toContain("frame-ancestors 'none'");
  expect(h["x-powered-by"]).toBeUndefined();
});
