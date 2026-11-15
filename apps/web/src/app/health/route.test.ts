import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { resetCspManifestCache } from "@/lib/csp-manifest";
import { GET } from "./route";

let dir: string;
const saved = process.env.CATALOGUE_DIR;

beforeEach(() => {
  dir = mkdtempSync(path.join(tmpdir(), "ev-health-"));
  process.env.CATALOGUE_DIR = dir;
});

afterEach(() => {
  rmSync(dir, { recursive: true, force: true });
  if (saved === undefined) delete process.env.CATALOGUE_DIR;
  else process.env.CATALOGUE_DIR = saved;
});

function publish(n: number) {
  mkdirSync(path.join(dir, String(n)));
  writeFileSync(
    path.join(dir, String(n), "catalogue.json"),
    JSON.stringify({ release: n, generated_at: "2026-11-15T00:00:00Z", rows: [], sources: [] }),
  );
  writeFileSync(path.join(dir, "latest"), `${n}\n`);
}

describe("GET /health", () => {
  it("returns 200 JSON with the published release number", async () => {
    publish(7);
    const res = GET();
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toMatch(/application\/json/);
    expect(res.headers.get("cache-control")).toMatch(/no-store/);
    const body = await res.json();
    expect(body.status).toBe("ok");
    expect(body.release).toBe(7);
    expect(Number.isNaN(Date.parse(body.time))).toBe(false);
  });

  it("reports release null while the dev fixture is in use", async () => {
    const body = await GET().json();
    expect(body).toMatchObject({ status: "ok", release: null });
  });

  it("A-05 F10: answers 503 in production when the CSP hash manifest is missing", async () => {
    publish(4);
    const cwd = process.cwd();
    vi.stubEnv("NODE_ENV", "production");
    vi.spyOn(console, "error").mockImplementation(() => {});
    process.chdir(dir); // no .next/server/csp-hashes.json here
    resetCspManifestCache();
    try {
      const res = GET();
      expect(res.status).toBe(503);
      expect((await res.json()).status).toBe("unhealthy");
      // With the manifest in place it is healthy again.
      mkdirSync(path.join(dir, ".next/server"), { recursive: true });
      writeFileSync(path.join(dir, ".next/server/csp-hashes.json"), JSON.stringify({ notFound: [], pages: {} }));
      resetCspManifestCache();
      expect(GET().status).toBe(200);
    } finally {
      process.chdir(cwd);
      vi.unstubAllEnvs();
      vi.restoreAllMocks();
      resetCspManifestCache();
    }
  });

  it("exposes only status, release and time; no paths or env", async () => {
    publish(3);
    const text = await GET().text();
    expect(Object.keys(JSON.parse(text)).sort()).toEqual(["release", "status", "time"]);
    expect(text).not.toContain(dir);
    expect(text).not.toContain("CATALOGUE_DIR");
  });
});
