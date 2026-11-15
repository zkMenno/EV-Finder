import { describe, expect, it } from "vitest";
import { inlineScriptHashes, buildManifest } from "../../scripts/csp-hashes.mjs";
import { buildCsp, cspFor, makeNonce, manifestKey } from "./csp";
import { checkStaff, safeEqual } from "./staff-auth";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { createHash } from "node:crypto";

const sha = (s: string) => `sha256-${createHash("sha256").update(s).digest("base64")}`;

describe("CSP (no 'unsafe-inline' for scripts)", () => {
  it("nonce policy for dynamic pages, own origin only", () => {
    const n = makeNonce();
    expect(n).toMatch(/^[A-Za-z0-9+/]{22}==$/);
    expect(makeNonce()).not.toBe(n);
    const csp = buildCsp({ nonce: n });
    expect(csp).toContain(`script-src 'self' 'nonce-${n}'`);
    expect(csp).toContain("connect-src 'self'");
    expect(csp).toContain("frame-ancestors 'none'");
    expect(csp.split("; ").find((d) => d.startsWith("script-src"))).not.toContain("unsafe-inline");
    expect(csp).not.toContain("unsafe-eval");
    expect(buildCsp({ dev: true })).toContain("'unsafe-eval'");
  });
  it("static paths get their hashes and no nonce; others a nonce + the 404 hashes", () => {
    const m = { notFound: ["sha256-nf"], pages: { "/nl/nl/top": ["sha256-a", "sha256-b"] } };
    const s = cspFor("/nl/nl/top/", m, { nonce: "N" });
    expect(s.nonce).toBeNull();
    expect(s.csp).toContain("script-src 'self' 'sha256-a' 'sha256-b'");
    const d = cspFor("/nl/nl", m, { nonce: "N" });
    expect(d.csp).toContain("'nonce-N' 'sha256-nf'");
    expect(manifestKey("/be/fr/learn/caf%C3%A9")).toBe("/be/fr/learn/café");
  });
  it("hashes exactly the inline scripts of a prerendered page", () => {
    const html = `<html><script src="/_next/a.js" async=""></script><script>self.__next_f=[]</script><script id="_R_">x()</script><script></script></html>`;
    expect(inlineScriptHashes(html)).toEqual([sha("self.__next_f=[]"), sha("x()")]);
    const dir = mkdtempSync(path.join(tmpdir(), "csp-"));
    mkdirSync(path.join(dir, "nl/nl"), { recursive: true });
    writeFileSync(path.join(dir, "nl/nl/top.html"), html);
    writeFileSync(path.join(dir, "_not-found.html"), "<script>nf()</script>");
    const m = buildManifest(dir);
    expect(m.pages["/nl/nl/top"]).toHaveLength(2);
    expect(m.notFound).toEqual([sha("nf()")]);
  });
});

describe("staff guard (Q-035)", () => {
  const basic = (s: string) => `Basic ${Buffer.from(s).toString("base64")}`;
  it("off unless STAFF_PAGES=1", () => {
    expect(checkStaff(basic("a:b"), {})).toBe("off");
  });
  it("fails closed without credentials configured", () => {
    expect(checkStaff(basic("a:b"), { STAFF_PAGES: "1" })).toBe("challenge");
    expect(checkStaff(basic("a:b"), { STAFF_PAGES: "1", STAFF_BASIC_AUTH: "nocolon" })).toBe("challenge");
  });
  it("accepts only the exact user:pass", () => {
    const env = { STAFF_PAGES: "1", STAFF_BASIC_AUTH: "staff:s3cret" };
    expect(checkStaff(basic("staff:s3cret"), env)).toBe("ok");
    expect(checkStaff(basic("staff:s3cre"), env)).toBe("challenge");
    expect(checkStaff(null, env)).toBe("challenge");
    expect(checkStaff("Bearer x", env)).toBe("challenge");
    expect(safeEqual("a", "a")).toBe(true);
    expect(safeEqual("a", "ab")).toBe(false);
  });
});
