#!/usr/bin/env node
// Fetch the current catalogue release by its manifest (T-064, Decision 035). Written by WS1;
// WS2 reviews. No dependencies: Node 22 fetch + crypto.
//
// Release files live in GitHub Release assets (tag data-v<n>). Git keeps
// data/releases/<n>/manifest.json with each file's size and sha256. This script reads
// data/releases/latest, then downloads every file the manifest lists that is missing (or, with
// CATALOGUE_SOURCE=manifest, also re-checks files already on disk), verifies size + sha256,
// and moves it into place atomically. A mismatch fails the build; nothing unverified is kept.
//
//   CATALOGUE_SOURCE=auto      (default) fetch only when a listed file is missing
//   CATALOGUE_SOURCE=manifest  verify every file, re-download any that don't match
//   CATALOGUE_SOURCE=local     do nothing (CATALOGUE_DIR / dev fixture, offline work)
//   CATALOGUE_DIR              releases folder (default ../../data/releases), same as the loader
//   CATALOGUE_RELEASE          fetch this release number instead of `latest` (rollback preview)
//   CATALOGUE_FILES            comma-separated paths the web needs (a trailing / = a folder);
//                              default "catalogue.json,charging_stats.json,used_prices.json" (what
//                              the loader reads today). Add "catalogue/" when pages use the split files.
//   FETCH_RELEASE_ALLOW_HTTP_LOCAL=1  allow an http://127.0.0.1 download_url (local manual tests only)

/* global process, console, Buffer, fetch, setTimeout */
import { createHash } from "node:crypto";
import { createReadStream, existsSync, mkdirSync, readFileSync, renameSync, rmSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";

const mode = process.env.CATALOGUE_SOURCE ?? "auto";
const dir = process.env.CATALOGUE_DIR ?? path.resolve(process.cwd(), "../../data/releases");
const files = (process.env.CATALOGUE_FILES ?? "catalogue.json,charging_stats.json,used_prices.json").split(",").map((x) => x.trim()).filter(Boolean);
const PARALLEL = 6;

function wanted(rel) {
  return files.some((f) => (f.endsWith("/") ? rel.startsWith(f) : rel === f));
}
const RETRIES = 3;

function fail(msg) {
  console.error(`fetch-release: ${msg}`);
  process.exit(1);
}

function sha256(file) {
  return new Promise((resolve, reject) => {
    const h = createHash("sha256");
    createReadStream(file).on("data", (c) => h.update(c)).on("end", () => resolve(h.digest("hex"))).on("error", reject);
  });
}

async function matches(file, entry) {
  if (!existsSync(file)) return false;
  if (statSync(file).size !== entry.bytes) return false;
  return (await sha256(file)) === entry.sha256;
}

function safePath(rel) {
  if (!rel || rel.startsWith("/") || rel.includes("\\") || rel.split("/").includes("..")) fail(`unsafe path in manifest: ${rel}`);
  return rel;
}

async function download(url, dest, entry) {
  let lastErr;
  for (let attempt = 1; attempt <= RETRIES; attempt++) {
    const tmp = path.join(path.dirname(dest), `.${path.basename(dest)}.part-${process.pid}`);
    try {
      const res = await fetch(url, { redirect: "follow" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const buf = Buffer.from(await res.arrayBuffer());
      if (buf.length !== entry.bytes) throw new Error(`${buf.length} bytes, manifest says ${entry.bytes}`);
      const got = createHash("sha256").update(buf).digest("hex");
      if (got !== entry.sha256) throw new Error("sha256 mismatch");
      writeFileSync(tmp, buf);
      renameSync(tmp, dest);
      return;
    } catch (e) {
      lastErr = e;
      rmSync(tmp, { force: true });
      if (attempt < RETRIES) await new Promise((r) => setTimeout(r, 500 * attempt));
    }
  }
  fail(`${entry.path}: ${lastErr?.message ?? lastErr} (${url})`);
}

async function main() {
  if (mode === "local") return;
  if (mode !== "auto" && mode !== "manifest") fail(`unknown CATALOGUE_SOURCE=${mode}`);
  const latestFile = path.join(dir, "latest");
  const n = (process.env.CATALOGUE_RELEASE ?? (existsSync(latestFile) ? readFileSync(latestFile, "utf8") : "")).trim();
  if (!n) return; // no release yet: the loader uses the dev fixture
  if (!/^\d+$/.test(n)) fail(`release must be a number, got "${n}"`);
  const rdir = path.join(dir, n);
  const mfile = path.join(rdir, "manifest.json");
  if (!existsSync(mfile)) {
    if (mode === "manifest") fail(`${mfile} missing`);
    return; // a release from before T-064, fully in git
  }
  const m = JSON.parse(readFileSync(mfile, "utf8"));
  if (m.schema !== "ev-release-manifest/1") fail(`unknown manifest schema ${m.schema}`);
  if (String(m.release) !== n) fail(`manifest is for release ${m.release}, expected ${n}`);
  const base = m.storage?.download_url;
  if (typeof base !== "string" || !(base.startsWith("https://") || (process.env.FETCH_RELEASE_ALLOW_HTTP_LOCAL === "1" && base.startsWith("http://127.0.0.1:"))) || !base.includes("{asset}")) fail("manifest has no https download_url");

  const todo = [];
  for (const e of m.files) {
    if (!wanted(e.path)) continue;
    const dest = path.join(rdir, safePath(e.path));
    if (mode === "auto" && existsSync(dest)) continue;
    if (await matches(dest, e)) continue;
    if (e.in_git) fail(`${e.path} is kept in git but doesn't match the manifest (edited by hand?)`);
    todo.push({ e, dest, url: base.replace("{asset}", encodeURIComponent(e.asset)) });
  }
  // Name what the release has, and warn about wanted files it lacks (QA A-35: release 1 has no
  // used_prices.json, but the log said "ready (… used_prices.json)", which hid a stale release).
  const listed = files.filter((f) => m.files.some((e) => (f.endsWith("/") ? e.path.startsWith(f) : e.path === f)));
  const absent = files.filter((f) => !listed.includes(f));
  if (absent.length) console.warn(`fetch-release: release ${n} has no ${absent.join(", ")} (not in its manifest); pages that need it show "not known yet"`);
  if (!todo.length) {
    console.log(`fetch-release: release ${n} ready (${listed.join(", ") || "nothing wanted"})`);
    return;
  }
  console.log(`fetch-release: release ${n}: downloading ${todo.length} file(s)`);
  let i = 0;
  async function worker() {
    while (i < todo.length) {
      const job = todo[i++];
      mkdirSync(path.dirname(job.dest), { recursive: true });
      await download(job.url, job.dest, job.e);
    }
  }
  await Promise.all(Array.from({ length: Math.min(PARALLEL, todo.length) }, worker));
  console.log(`fetch-release: release ${n} verified (sha256)`);
}

main().catch((e) => fail(e?.stack ?? String(e)));
