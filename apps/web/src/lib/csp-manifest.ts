// The CSP hash manifest (.next/server/csp-hashes.json, written by scripts/csp-hashes.mjs after
// `next build`). Read once per process. Server only (node:fs).
//
// Fails closed (A-05 F10): without the manifest, production never falls back to
// 'unsafe-inline'. The proxy serves the strict nonce-only policy (static pages lose their inline
// scripts but stay safe) and /health answers 503, so the Docker healthcheck, Caddy and the
// AppInfra watchdog see a broken deploy instead of a silently weaker site. Dev needs no manifest.
import { readFileSync } from "node:fs";
import path from "node:path";
import type { CspHashManifest } from "./csp";

export const CSP_MANIFEST_PATH = path.join(".next", "server", "csp-hashes.json");

function isManifest(v: unknown): v is CspHashManifest {
  if (!v || typeof v !== "object") return false;
  const m = v as Record<string, unknown>;
  return Array.isArray(m.notFound) && !!m.pages && typeof m.pages === "object";
}

/** Parse the manifest file; null when it is missing or malformed. */
export function readCspManifest(file: string = path.join(process.cwd(), CSP_MANIFEST_PATH)): CspHashManifest | null {
  try {
    const v: unknown = JSON.parse(readFileSync(file, "utf8"));
    return isManifest(v) ? v : null;
  } catch {
    return null;
  }
}

let cached: CspHashManifest | null | undefined;

/** The manifest, read once per process (null when missing; logged once outside dev). */
export function cspManifest(env: Record<string, string | undefined> = process.env): CspHashManifest | null {
  if (cached !== undefined) return cached;
  cached = readCspManifest();
  if (!cached && env.NODE_ENV !== "development")
    console.error(`csp: ${CSP_MANIFEST_PATH} missing or unreadable (run \`pnpm build\`); serving the strict nonce-only policy and failing /health`);
  return cached;
}

/** For tests: forget the cached manifest. */
export function resetCspManifestCache(): void {
  cached = undefined;
}

/** /health readiness: false only in production when the manifest is missing. */
export function cspReady(manifest: CspHashManifest | null, env: Record<string, string | undefined> = process.env): boolean {
  return manifest !== null || env.NODE_ENV !== "production";
}
