// A-05 F2 / F10: the proxy runs for every page request (no header can skip it), always sets a
// CSP without 'unsafe-inline' for scripts, and challenges staff requests whatever they carry.
import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { resetCspManifestCache } from "@/lib/csp-manifest";
import { config, proxy } from "./proxy";

const req = (path: string, headers: Record<string, string> = {}) => new NextRequest(new URL(path, "http://localhost:3000"), { headers });
const scriptSrc = (csp: string | null) => (csp ?? "").split("; ").find((d) => d.startsWith("script-src")) ?? "";

beforeEach(() => {
  vi.spyOn(console, "error").mockImplementation(() => {});
  resetCspManifestCache();
});
afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
  resetCspManifestCache();
});

describe("proxy matcher", () => {
  it("has no header conditions that a client could use to skip it", () => {
    for (const m of config.matcher) expect(typeof m).toBe("string");
    expect(JSON.stringify(config)).not.toMatch(/missing|prefetch/i);
  });
});

describe("staff challenge", () => {
  const PREFETCH: Record<string, string>[] = [{}, { purpose: "prefetch" }, { "next-router-prefetch": "1", rsc: "1" }, { "sec-purpose": "prefetch" }];

  it.each(PREFETCH)("401 without credentials, whatever prefetch headers are sent (%o)", (h) => {
    vi.stubEnv("STAFF_PAGES", "1");
    vi.stubEnv("STAFF_BASIC_AUTH", "u:secretpw");
    const res = proxy(req("/staff/review", h));
    expect(res.status).toBe(401);
    expect(res.headers.get("www-authenticate")).toMatch(/^Basic/);
  });

  it("lets the right credentials through, with a CSP and no-store", () => {
    vi.stubEnv("STAFF_PAGES", "1");
    vi.stubEnv("STAFF_BASIC_AUTH", "u:secretpw");
    const res = proxy(req("/staff/review", { authorization: `Basic ${btoa("u:secretpw")}`, purpose: "prefetch" }));
    expect(res.status).toBe(200);
    expect(res.headers.get("cache-control")).toBe("no-store");
    expect(scriptSrc(res.headers.get("content-security-policy"))).toMatch(/'nonce-/);
  });
});

describe("CSP fails closed (F10)", () => {
  it("production without the hash manifest: strict nonce policy, never 'unsafe-inline'", () => {
    vi.stubEnv("NODE_ENV", "production");
    const cwd = process.cwd();
    process.chdir("/"); // no .next/server/csp-hashes.json
    try {
      for (const path of ["/nl/en", "/nl/en/learn/real-range"]) {
        const src = scriptSrc(proxy(req(path, { purpose: "prefetch" })).headers.get("content-security-policy"));
        expect(src).toMatch(/^script-src 'self' 'nonce-[A-Za-z0-9+/=]+'$/);
        expect(src).not.toContain("unsafe-inline");
      }
    } finally {
      process.chdir(cwd);
    }
  });

  it("a public page requested with `Purpose: prefetch` still gets the CSP", () => {
    const res = proxy(req("/nl/en", { purpose: "prefetch" }));
    expect(res.headers.get("content-security-policy")).toContain("frame-ancestors 'none'");
  });
});
