// After `next build`: hash every inline <script> of every prerendered page, so static pages get a
// strict hash-based CSP without 'unsafe-inline' (src/lib/csp.ts, src/proxy.ts). Writes
// .next/server/csp-hashes.json (and the same file into the standalone output).
//
//   node scripts/csp-hashes.mjs
/* global console, process */
import { createHash } from "node:crypto";
import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
export const NEXT_DIR = path.resolve(here, "../.next");
export const MANIFEST = "csp-hashes.json";

/** sha256 hashes ('sha256-…', CSP form) of the inline scripts in one HTML document. */
export function inlineScriptHashes(html) {
  const out = [];
  const re = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
  for (let m = re.exec(html); m; m = re.exec(html)) {
    if (/\bsrc\s*=/.test(m[1])) continue;
    if (!m[2]) continue;
    out.push(`sha256-${createHash("sha256").update(m[2], "utf8").digest("base64")}`);
  }
  return [...new Set(out)];
}

function* htmlFiles(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* htmlFiles(p);
    else if (e.name.endsWith(".html")) yield p;
  }
}

/** { notFound, pages: { "/nl/nl/top": [...] } } from .next/server/app. */
export function buildManifest(appDir) {
  const pages = {};
  let notFound = [];
  for (const file of htmlFiles(appDir)) {
    const rel = path.relative(appDir, file).split(path.sep).join("/").replace(/\.html$/, "");
    const hashes = inlineScriptHashes(readFileSync(file, "utf8"));
    if (rel === "_not-found" || rel === "_global-error") {
      notFound = [...new Set([...notFound, ...hashes])];
      continue;
    }
    pages[rel === "index" ? "/" : `/${rel}`] = hashes;
  }
  return { notFound, pages };
}

/**
 * Prerendered catalogue pages that came out as 404s (e.g. the release changed during the build).
 * A model / generation / variant / learn path is only prerendered because the catalogue listed
 * it, so a 404 there means the build saw inconsistent data.
 */
export function baked404s(appDir) {
  const bad = [];
  for (const file of htmlFiles(appDir)) {
    const rel = path.relative(appDir, file).split(path.sep).join("/");
    if (!/^[a-z]{2}\/[a-z]{2}\/(ev|learn|top)\//.test(rel)) continue;
    const meta = file.replace(/\.html$/, ".meta");
    if (!existsSync(meta)) continue;
    if (JSON.parse(readFileSync(meta, "utf8")).status === 404) bad.push(`/${rel.replace(/\.html$/, "")}`);
  }
  return bad;
}

function main() {
  const appDir = path.join(NEXT_DIR, "server/app");
  if (!existsSync(appDir)) throw new Error(`${appDir} not found: run next build first`);
  const bad = baked404s(appDir);
  if (bad.length) {
    console.error(`csp-hashes: ${bad.length} prerendered catalogue pages are 404s (release changed during the build?), e.g. ${bad.slice(0, 3).join(", ")}. Rebuild.`);
    process.exit(1);
  }
  const json = JSON.stringify(buildManifest(appDir));
  const targets = [path.join(NEXT_DIR, "server", MANIFEST)];
  const standalone = path.join(NEXT_DIR, "standalone/apps/web/.next/server");
  if (existsSync(standalone)) targets.push(path.join(standalone, MANIFEST));
  for (const t of targets) writeFileSync(t, json);
  const n = Object.keys(JSON.parse(json).pages).length;
  console.log(`csp-hashes: ${n} static pages hashed → ${targets.map((t) => path.relative(process.cwd(), t)).join(", ")}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
