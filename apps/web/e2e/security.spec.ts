import { expect, test, type Page } from "@playwright/test";
import { E2E_STAFF_AUTH } from "../playwright.config";

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
  // Hydrated: the country switcher (client component) navigates. (No language switcher while
  // English is the only language, Decision 082.)
  await page.getByRole("combobox", { name: /Country/ }).selectOption("be");
  await expect(page).toHaveURL(/\/be\/en\/learn\/real-range$/);
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
  const h = (await request.get("/nl/en/top")).headers();
  expect(h["x-content-type-options"]).toBe("nosniff");
  expect(h["x-frame-options"]).toBe("DENY");
  expect(h["referrer-policy"]).toBe("strict-origin-when-cross-origin");
  expect(h["content-security-policy"]).toContain("frame-ancestors 'none'");
  expect(h["x-powered-by"]).toBeUndefined();
});

// A-05 F2: a request header must never skip the proxy (CSP, staff challenge). The staff layout and
// page check the credentials again themselves, so even a skipped proxy would give a 404.
const PREFETCH_HEADERS: Record<string, string>[] = [
  { purpose: "prefetch" },
  { "sec-purpose": "prefetch" },
  { "next-router-prefetch": "1", rsc: "1" },
  { purpose: "prefetch", "next-router-prefetch": "1", rsc: "1" },
];

test("Staff review: prefetch headers never bypass the staff guard", async ({ request }) => {
  for (const headers of PREFETCH_HEADERS) {
    const res = await request.get("/staff/review", { headers, maxRedirects: 0 });
    expect([401, 404], JSON.stringify(headers)).toContain(res.status());
    const body = await res.text();
    expect(body).not.toContain("Review queue");
    expect(body).not.toMatch(/um-[0-9a-f]{6,}/);
  }
});

test("Staff review: the right credentials get the page, with a CSP", async ({ request }) => {
  const authorization = `Basic ${Buffer.from(E2E_STAFF_AUTH).toString("base64")}`;
  const res = await request.get("/staff/review", { headers: { authorization } });
  expect(res.status()).toBe(200);
  expect(res.headers()["content-security-policy"]).toMatch(/script-src 'self' 'nonce-/);
  expect(res.headers()["cache-control"]).toContain("no-store");
  const wrong = await request.get("/staff/review", { headers: { authorization: `Basic ${Buffer.from("e2e:wrong").toString("base64")}` } });
  expect(wrong.status()).toBe(401);
});

test("Public pages requested with prefetch headers still carry the CSP", async ({ request }) => {
  for (const path of ["/nl/en", "/nl/en/learn/real-range", "/nl/en/top"]) {
    for (const headers of PREFETCH_HEADERS) {
      const res = await request.get(path, { headers, maxRedirects: 0 });
      const csp = res.headers()["content-security-policy"] ?? "";
      expect(csp, `${path} ${JSON.stringify(headers)}`).toContain("frame-ancestors 'none'");
      const src = csp.split("; ").find((d) => d.startsWith("script-src")) ?? "";
      expect(src).toMatch(/'(nonce|sha256)-/);
      expect(src).not.toContain("unsafe-inline");
    }
  }
});

test("Canonical and hreflang use APP_URL, never localhost (A-05 F3)", async ({ request }) => {
  // CI's build is a test build (CI=true) and may run without APP_URL; it then keeps localhost.
  test.skip(!!process.env.CI && !process.env.APP_URL, "CI test build without APP_URL");
  const html = await (await request.get("/nl/en/learn/real-range")).text();
  expect(html).toMatch(/<link rel="canonical" href="https:\/\/[^"]+\/nl\/en\/learn\/real-range"/);
  expect(html).toMatch(/<link rel="alternate" hrefLang="x-default" href="https:\/\//);
  expect(html).not.toMatch(/https?:\/\/localhost/);
  const sitemap = await (await request.get("/sitemap.xml")).text();
  expect(sitemap).toContain("<loc>https://");
  expect(sitemap).not.toContain("localhost");
});
