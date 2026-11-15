// A-05 F3: production canonical / hreflang / sitemap URLs never point at localhost.
import { spawnSync } from "node:child_process";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { DEV_APP_URL, resolveAppUrl } from "../../scripts/app-url.mjs";
import { siteUrl } from "./site-paths";

const PROD = { NODE_ENV: "production" };
const SCRIPT = path.resolve(__dirname, "../../scripts/check-app-url.mjs");

describe("APP_URL rules", () => {
  it("production build without APP_URL fails loudly", () => {
    expect(() => resolveAppUrl(PROD)).toThrow(/APP_URL is not set/);
    expect(() => siteUrl({ ...PROD, APP_URL: "  " })).toThrow(/APP_URL is not set/);
  });

  it("production build rejects local or plain-http origins", () => {
    for (const u of ["http://localhost:3000", "https://localhost", "https://127.0.0.1:3000", "http://ev.example.com", "https://[::1]"])
      expect(() => resolveAppUrl({ ...PROD, APP_URL: u }), u).toThrow(/public https origin/);
  });

  it("rejects paths, queries and junk in any mode", () => {
    for (const u of ["https://ev.example.com/nl", "https://ev.example.com/?x=1", "ftp://ev.example.com", "not a url", "https://u:p@ev.example.com"])
      expect(() => resolveAppUrl({ APP_URL: u }), u).toThrow();
  });

  it("production with a public https origin: normalised, no trailing slash", () => {
    expect(siteUrl({ ...PROD, APP_URL: "https://ev.example.com/" })).toBe("https://ev.example.com");
    expect(siteUrl({ ...PROD, APP_URL: "https://EV.example.com:8443" })).toBe("https://ev.example.com:8443");
  });

  it("dev, unit tests and CI test builds may fall back to localhost", () => {
    expect(siteUrl({})).toBe(DEV_APP_URL);
    expect(siteUrl({ NODE_ENV: "development" })).toBe(DEV_APP_URL);
    expect(siteUrl({ ...PROD, CI: "true" })).toBe(DEV_APP_URL);
    expect(siteUrl({ ...PROD, APP_URL_TEST_BUILD: "1" })).toBe(DEV_APP_URL);
    expect(siteUrl({ ...PROD, CI: "true", APP_URL: "http://localhost:3100" })).toBe("http://localhost:3100");
  });

  it("the pre-build check exits non-zero without APP_URL and passes with one", () => {
    // Typed as ProcessEnv (Next requires NODE_ENV there); the child gets exactly these vars.
    const base = { PATH: process.env.PATH ?? "" } as unknown as NodeJS.ProcessEnv;
    const bad = spawnSync(process.execPath, [SCRIPT], { env: base, encoding: "utf8" });
    expect(bad.status).toBe(1);
    expect(bad.stderr).toMatch(/APP_URL is not set/);
    const ok = spawnSync(process.execPath, [SCRIPT], { env: { ...base, APP_URL: "https://ev.example.com" }, encoding: "utf8" });
    expect(ok.status).toBe(0);
    expect(ok.stdout).toContain("https://ev.example.com");
  });
});
