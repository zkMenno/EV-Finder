// Verify the web app the way a buyer uses it (T-126): walks the flows in e2e/feature-map.yaml on a
// production build, checks each expected result, takes screenshots (360 + 1280 px, light + dark,
// plus one non-English language) and writes verify-report/verify-report.md and summary.md (the
// evidence pack for the PR body). How and when to run it: apps/web/.claude/skills/verify/SKILL.md.
//
//   pnpm --filter @ev/web verify                 every feature, on the published release
//   pnpm --filter @ev/web verify --changed       only features whose triggers match the diff
//   options: --base <ref> (default origin/main) · --only id,id · --fixture (dev fixture build)
//            --url http://localhost:3100 (use a running server) · --port 3199 · --repeat 3
//            --no-shots · --lang nl (second language for screenshots) · --out <dir>
//
// Needs a build first: `APP_URL=https://ev.example.com pnpm --filter @ev/web build`
// (with --fixture: build with CATALOGUE_DIR pointing at an empty folder, see SKILL.md).
/* global process, console, setTimeout, fetch, URL, document, window */
import { spawn, execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import * as yaml from "js-yaml";

const here = path.dirname(fileURLToPath(import.meta.url));
const WEB = path.resolve(here, "..");
const REPO = path.resolve(WEB, "../..");
export const MAP_FILE = path.join(WEB, "e2e/feature-map.yaml");

// ── Pure helpers (unit-tested in src/lib/verify-map.test.ts) ─────────────────────────────────

/** Glob (relative to apps/web) → RegExp. Supports **, *, ? and [...] (use [[] for a literal "["). */
export function globToRegExp(glob) {
  let re = "";
  for (let i = 0; i < glob.length; i++) {
    const c = glob[i];
    if (c === "*" && glob[i + 1] === "*") {
      if (glob[i + 2] === "/") {
        re += "(?:.*/)?";
        i += 2;
      } else {
        re += ".*";
        i += 1;
      }
    } else if (c === "*") re += "[^/]*";
    else if (c === "?") re += "[^/]";
    else if (c === "[") {
      const end = glob.indexOf("]", i + 2);
      if (end < 0) re += "\\[";
      else {
        re += "[" + glob.slice(i + 1, end).replace(/\\/g, "\\\\") + "]";
        i = end;
      }
    } else re += c.replace(/[.+^${}()|\\]/g, "\\$&");
  }
  return new RegExp("^" + re + "$");
}

/** `@name` → [data-testid="name"], except in XPath selectors (where @ is an attribute). */
export function expandSelector(sel) {
  if (/^\(?\/\//.test(sel.trim())) return sel;
  return sel.replace(/(^|[\s(,>+~])@([a-z0-9-]+)/g, (_m, pre, id) => `${pre}[data-testid="${id}"]`);
}

/** Which features a list of changed paths (relative to apps/web) should walk. */
export function selectFeatures(map, changed) {
  const all = map.features ?? [];
  const everything = (map.defaults?.always_all ?? []).map(globToRegExp);
  if (changed.some((f) => everything.some((re) => re.test(f)))) return { features: all, reason: "a shared file changed" };
  const picked = all.filter((ft) => (ft.triggers ?? []).map(globToRegExp).some((re) => changed.some((f) => re.test(f))));
  return { features: picked, reason: picked.length ? "triggers matched" : "no feature's triggers matched" };
}

/** Validates the map; returns a list of problems (empty = fine). */
export function checkMap(map) {
  const problems = [];
  const ids = new Set();
  const STEP = new Set(["goto", "click", "fill", "select", "follow", "wait"]);
  const EXP = new Set(["count", "visible", "text", "attr", "url", "lang"]);
  for (const [i, f] of (map?.features ?? []).entries()) {
    const at = `features[${i}] ${f?.id ?? "?"}`;
    if (typeof f?.id !== "string" || !/^[a-z0-9-]+$/.test(f.id)) problems.push(`${at}: id must be kebab-case`);
    if (ids.has(f?.id)) problems.push(`${at}: duplicate id`);
    ids.add(f?.id);
    if (typeof f?.title !== "string") problems.push(`${at}: needs a title`);
    if (!Array.isArray(f?.triggers) || !f.triggers.length) problems.push(`${at}: needs triggers`);
    if (!Array.isArray(f?.steps) || !f.steps.length || !f.steps[0]?.goto) problems.push(`${at}: steps must start with goto`);
    for (const s of f?.steps ?? []) {
      const k = Object.keys(s ?? {});
      if (k.length !== 1 || !STEP.has(k[0])) problems.push(`${at}: unknown step ${JSON.stringify(s)}`);
    }
    if (!Array.isArray(f?.expect) || !f.expect.length) problems.push(`${at}: needs at least one expectation`);
    for (const e of f?.expect ?? []) {
      const kind = Object.keys(e ?? {}).find((k) => EXP.has(k));
      if (!kind) problems.push(`${at}: expectation without a known check ${JSON.stringify(e)}`);
      if (typeof e?.what !== "string" || typeof e?.why !== "string") problems.push(`${at}: every expectation needs what + why`);
      if (e?.on && !["release", "fixture"].includes(e.on)) problems.push(`${at}: on must be release or fixture`);
      if (kind === "count" && e.eq === undefined && e.min === undefined && e.max === undefined) problems.push(`${at}: count needs eq, min or max`);
      if (kind === "text" && e.contains === undefined && e.match === undefined) problems.push(`${at}: text needs contains or match`);
      if (kind === "attr" && (typeof e.name !== "string" || typeof e.match !== "string")) problems.push(`${at}: attr needs name and match`);
    }
  }
  return problems;
}

export function loadMap(file = MAP_FILE) {
  return yaml.load(readFileSync(file, "utf8"), { schema: yaml.CORE_SCHEMA });
}

/** Dictionary keys that may never be shown raw ("hero.card.price"). */
export function rawKeysIn(text, keys) {
  const found = new Set();
  for (const m of text.matchAll(/\b[a-z][a-zA-Z0-9]*(?:\.[a-zA-Z0-9_-]+)+\b/g)) if (keys.has(m[0])) found.add(m[0]);
  return [...found];
}

// ── Runner ───────────────────────────────────────────────────────────────────────────────────

function args(argv) {
  const o = { changed: false, base: "origin/main", only: null, fixture: false, url: null, port: 3199, repeat: 1, shots: true, lang: "nl", out: path.join(WEB, "verify-report") };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => argv[++i];
    if (a === "--changed") o.changed = true;
    else if (a === "--base") o.base = next();
    else if (a === "--only") o.only = next().split(",");
    else if (a === "--fixture") o.fixture = true;
    else if (a === "--url") o.url = next().replace(/\/$/, "");
    else if (a === "--port") o.port = Number(next());
    else if (a === "--repeat") o.repeat = Math.max(1, Number(next()));
    else if (a === "--no-shots") o.shots = false;
    else if (a === "--lang") o.lang = next();
    else if (a === "--out") o.out = path.resolve(next());
    else if (a !== "--") throw new Error(`unknown option ${a}`);
  }
  return o;
}

function git(...a) {
  return execFileSync("git", a, { cwd: REPO, encoding: "utf8" }).trim();
}

/** Changed files vs the base (committed + uncommitted + untracked), relative to apps/web. */
function changedFiles(base) {
  const lines = new Set();
  for (const out of [git("diff", "--name-only", `${base}...HEAD`), git("diff", "--name-only", "HEAD"), git("ls-files", "--others", "--exclude-standard")])
    for (const l of out.split("\n")) if (l) lines.add(l);
  return [...lines].map((f) => path.relative(WEB, path.join(REPO, f)).split(path.sep).join("/"));
}

async function waitFor(url, ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    try {
      if ((await fetch(url)).ok) return true;
    } catch {
      /* not up yet */
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  return false;
}

function startServer(o) {
  const catDir = o.fixture ? mkdtempSync(path.join(tmpdir(), "ev-verify-fixture-")) : path.join(REPO, "data/releases");
  const env = {
    ...process.env,
    APP_URL: process.env.APP_URL ?? "https://ev.example.com",
    CATALOGUE_DIR: catDir,
    PARKED: process.env.PARKED ?? "0",
    CHARGING_LINKS_FILE: process.env.CHARGING_LINKS_FILE ?? "e2e/fixtures/charging-links.json",
  };
  const child = spawn("pnpm", ["exec", "next", "start", "-p", String(o.port)], { cwd: WEB, env, stdio: "ignore", detached: true });
  return { child, catDir };
}

const firstLine = (e) => String(e?.message ?? e).split("\n").find((l) => l.trim()) ?? String(e);

function describeExpect(e) {
  if ("count" in e) return [e.eq !== undefined ? `exactly ${e.eq}` : null, e.min !== undefined ? `at least ${e.min}` : null, e.max !== undefined ? `at most ${e.max}` : null].filter(Boolean).join(", ");
  if ("text" in e) return e.contains !== undefined ? `text containing “${e.contains}”` : `text matching /${e.match}/`;
  if ("attr" in e) return `${e.name} matching /${e.match}/`;
  if ("url" in e) return `address matching /${e.url}/`;
  if ("lang" in e) return `<html lang="${e.lang}">`;
  return "visible";
}

async function check(page, e, timeout) {
  if ("count" in e) {
    const loc = page.locator(expandSelector(e.count));
    const ok = (n) => (e.eq === undefined || n === e.eq) && (e.min === undefined || n >= e.min) && (e.max === undefined || n <= e.max);
    let n = await loc.count();
    const end = Date.now() + timeout;
    while (!ok(n) && Date.now() < end) {
      await page.waitForTimeout(250);
      n = await loc.count();
    }
    return { ok: ok(n), found: `${n}` };
  }
  if ("visible" in e) {
    try {
      await page.locator(expandSelector(e.visible)).first().waitFor({ state: "visible", timeout });
      return { ok: true, found: "visible" };
    } catch {
      return { ok: false, found: "not on the page" };
    }
  }
  if ("text" in e) {
    const loc = page.locator(expandSelector(e.text)).first();
    let t;
    const end = Date.now() + timeout;
    const ok = (s) => (e.contains !== undefined ? s.includes(e.contains) : new RegExp(e.match).test(s));
    do {
      try {
        t = (await loc.innerText({ timeout: 1000 })).replace(/\s+/g, " ").trim();
      } catch {
        t = "";
      }
      if (ok(t)) return { ok: true, found: t.slice(0, 120) };
      await page.waitForTimeout(250);
    } while (Date.now() < end);
    return { ok: false, found: t ? `“${t.slice(0, 120)}”` : "nothing (element missing)" };
  }
  if ("attr" in e) {
    const loc = page.locator(expandSelector(e.attr)).first();
    const end = Date.now() + timeout;
    let v;
    do {
      v = (await loc.count()) ? await loc.getAttribute(e.name) : null;
      if (v !== null && new RegExp(e.match).test(v)) return { ok: true, found: v.slice(0, 120) };
      await page.waitForTimeout(250);
    } while (Date.now() < end);
    return { ok: false, found: v === null ? "no such element or attribute" : `“${v.slice(0, 120)}”` };
  }
  if ("url" in e) {
    const re = new RegExp(e.url);
    const end = Date.now() + timeout;
    while (!re.test(page.url()) && Date.now() < end) await page.waitForTimeout(250);
    return { ok: re.test(page.url()), found: page.url().replace(/^https?:\/\/[^/]+/, "") };
  }
  if ("lang" in e) {
    // Switching language navigates: wait for the new page instead of reading the old one.
    const end = Date.now() + timeout;
    let v = await page.locator("html").getAttribute("lang");
    while (v !== e.lang && Date.now() < end) {
      await page.waitForTimeout(250);
      v = await page.locator("html").getAttribute("lang").catch(() => null);
    }
    return { ok: v === e.lang, found: `lang="${v}"` };
  }
  return { ok: false, found: "unknown check" };
}

async function runStep(page, s, base, timeout) {
  const [kind, val] = Object.entries(s)[0];
  if (kind === "goto") return page.goto(base + val, { waitUntil: "load" });
  if (kind === "wait") return page.locator(expandSelector(val)).first().waitFor({ state: "visible", timeout });
  if (kind === "click") return page.locator(expandSelector(val)).first().click({ timeout });
  if (kind === "fill") return page.locator(expandSelector(val[0])).first().fill(String(val[1]), { timeout });
  if (kind === "select") return page.locator(expandSelector(val[0])).first().selectOption(String(val[1]), { timeout });
  if (kind === "follow") {
    const before = page.url();
    await page.locator(expandSelector(val)).first().click({ timeout });
    const end = Date.now() + timeout;
    while (page.url() === before && Date.now() < end) await page.waitForTimeout(100);
    if (page.url() === before) throw new Error("the link didn't open a new page");
    return page.waitForLoadState("load");
  }
  throw new Error(`unknown step ${kind}`);
}

/** Page-wide checks on every page the walk ends on: no page error, no raw keys, right <html lang>. */
async function globalChecks(page, keys, errors) {
  const out = [];
  if (errors.length) out.push({ ok: false, what: "the page", why: "a script crashed in the browser", found: errors[0] });
  const text = await page.evaluate(() => document.body.innerText);
  const raw = rawKeysIn(text, keys);
  if (raw.length) out.push({ ok: false, what: "the page text", why: "untranslated dictionary keys are shown to the buyer", found: raw.slice(0, 5).join(", ") });
  const lang = await page.locator("html").getAttribute("lang");
  const m = /^\/[a-z]{2}\/([a-z]{2})(?:\/|$|\?)/.exec(new URL(page.url()).pathname + "/");
  if (m && lang !== m[1]) out.push({ ok: false, what: "<html lang>", why: "screen readers and search engines get the wrong language", found: `lang="${lang}" on a /${m[1]} page` });
  return out;
}

function altLangUrl(url, lang) {
  return url.replace(/^(https?:\/\/[^/]+\/[a-z]{2})\/en(?=\/|\?|$)/, `$1/${lang}`);
}

async function main() {
  const o = args(process.argv.slice(2));
  const map = loadMap();
  const problems = checkMap(map);
  if (problems.length) {
    console.error("verify: e2e/feature-map.yaml has problems:\n" + problems.join("\n"));
    process.exit(2);
  }
  const timeout = map.defaults?.timeout_ms ?? 10000;
  let features = map.features;
  let reason = "all features";
  let changed = [];
  if (o.changed) {
    changed = changedFiles(o.base);
    ({ features, reason } = selectFeatures(map, changed));
  }
  if (o.only) features = features.filter((f) => o.only.includes(f.id));
  mkdirSync(o.out, { recursive: true });
  const commit = git("rev-parse", "--short", "HEAD");
  const dataLabel = o.fixture ? "dev fixture" : `release ${readFileSync(path.join(REPO, "data/releases/latest"), "utf8").trim()}`;
  if (!features.length) {
    const msg = `# Verify report\n\nCommit ${commit}, base ${o.base}: **no user-facing feature touched** (${reason}; ${changed.length} changed files). Nothing to walk.\n`;
    writeFileSync(path.join(o.out, "verify-report.md"), msg);
    writeFileSync(path.join(o.out, "summary.md"), msg);
    console.log(msg);
    return;
  }
  if (!o.url && !existsSync(path.join(WEB, ".next/BUILD_ID"))) {
    console.error("verify: no production build. Run `APP_URL=https://ev.example.com pnpm --filter @ev/web build` first (see SKILL.md).");
    process.exit(2);
  }
  const dict = JSON.parse(readFileSync(path.join(WEB, "src/i18n/en.json"), "utf8"));
  const keys = new Set(Object.keys(dict));

  let server = null;
  const base = o.url ?? `http://localhost:${o.port}`;
  if (!o.url) {
    server = startServer(o);
    if (!(await waitFor(`${base}/health`, 60000))) {
      console.error(`verify: the app didn't start on ${base} within 60 s`);
      process.kill(-server.child.pid);
      process.exit(2);
    }
  }
  const { chromium } = await import("@playwright/test");
  const browser = await chromium.launch();
  const shotChecksById = new Map();
  const results = []; // { run, feature, ok, steps: [], checks: [], ms, finalUrl }
  try {
    for (let run = 1; run <= o.repeat; run++) {
      for (const f of features) {
        const t0 = Date.now();
        const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, colorScheme: "light" });
        const page = await ctx.newPage();
        const errors = [];
        page.on("pageerror", (e) => errors.push(firstLine(e)));
        const steps = [];
        let failedStep = null;
        for (const [i, s] of f.steps.entries()) {
          const t = Date.now();
          const label = `${Object.keys(s)[0]} ${JSON.stringify(Object.values(s)[0])}`;
          try {
            await runStep(page, s, base, timeout);
            steps.push({ n: i + 1, label, ok: true, ms: Date.now() - t });
          } catch (e) {
            const err = firstLine(e).replace(/\s+/g, " ");
            steps.push({ n: i + 1, label, ok: false, ms: Date.now() - t, err });
            failedStep = { n: i + 1, label, err };
            break;
          }
        }
        const checks = [];
        const exps = (f.expect ?? []).filter((e) => !e.on || e.on === (o.fixture ? "fixture" : "release"));
        for (const e of exps) {
          if (failedStep) {
            checks.push({ ok: false, what: e.what, why: e.why, expected: describeExpect(e), found: `not checked: step ${failedStep.n} (${failedStep.label}) failed: ${failedStep.err}` });
            continue;
          }
          const r = await check(page, e, timeout);
          checks.push({ ok: r.ok, what: e.what, why: e.why, expected: describeExpect(e), found: r.found });
        }
        if (!failedStep) for (const g of await globalChecks(page, keys, errors)) checks.push({ ...g, expected: "none" });
        const finalUrl = page.url();
        // Screenshot-time checks (phone width, second language) run once; their result counts for
        // every run, so a steady failure never shows up as "flaky".
        let shots = [];
        if (o.shots && run === 1 && !failedStep) {
          const shotChecks = [];
          shots = await screenshots(browser, f.id, finalUrl, o, keys, shotChecks);
          shotChecksById.set(f.id, shotChecks);
        }
        checks.push(...(shotChecksById.get(f.id) ?? []));
        await ctx.close();
        const ok = !failedStep && checks.every((c) => c.ok);
        results.push({ run, feature: f, ok, steps, checks, ms: Date.now() - t0, finalUrl, shots });
        console.log(`${ok ? "✓" : "✗"} [run ${run}] ${f.id} (${Date.now() - t0} ms)`);
      }
    }
  } finally {
    await browser.close();
    if (server) {
      try {
        process.kill(-server.child.pid);
      } catch {
        /* already gone */
      }
      if (o.fixture) rmSync(server.catDir, { recursive: true, force: true });
    }
  }
  const report = writeReport(results, features, o, { commit, dataLabel, reason, changed });
  console.log(`\n${report.headline}\nReport: ${path.relative(process.cwd(), path.join(o.out, "verify-report.md"))}`);
  process.exit(report.ok ? 0 : 1);
}

/** 360 + 1280 px × light + dark of the final URL, plus 360 px light in a second language. */
async function screenshots(browser, id, url, o, keys, checks) {
  const out = [];
  const shot = async (w, scheme, u, name) => {
    const ctx = await browser.newContext({ viewport: { width: w, height: w < 500 ? 800 : 900 }, colorScheme: scheme, deviceScaleFactor: 1 });
    const p = await ctx.newPage();
    const errors = [];
    p.on("pageerror", (e) => errors.push(firstLine(e)));
    await p.goto(u, { waitUntil: "load" });
    await p.waitForTimeout(600);
    const file = `${id}--${name}.png`;
    await p.screenshot({ path: path.join(o.out, file) });
    if (name.startsWith(o.lang)) for (const g of await globalChecks(p, keys, errors)) checks.push({ ...g, what: `${g.what} (${o.lang.toUpperCase()})`, expected: "none" });
    // Horizontal scroll at phone width breaks the layout for most buyers.
    if (w < 500) {
      const over = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      if (over > 0) checks.push({ ok: false, what: `the page at ${w} px (${name}: ${u.replace(/^https?:\/\/[^/]+/, "")})`, why: "it scrolls sideways on a phone", expected: "no sideways scroll", found: `${over} px too wide` });
    }
    await p.close();
    await ctx.close();
    out.push(file);
  };
  await shot(360, "light", url, "360-light");
  await shot(360, "dark", url, "360-dark");
  await shot(1280, "light", url, "1280-light");
  await shot(1280, "dark", url, "1280-dark");
  const alt = altLangUrl(url, o.lang);
  if (alt !== url) await shot(360, "light", alt, `${o.lang}-360-light`);
  return out;
}

function writeReport(results, features, o, meta) {
  const byId = new Map();
  for (const r of results) {
    const list = byId.get(r.feature.id) ?? [];
    list.push(r);
    byId.set(r.feature.id, list);
  }
  const rows = [];
  let pass = 0;
  let fail = 0;
  let flaky = 0;
  for (const f of features) {
    const rs = byId.get(f.id) ?? [];
    const oks = rs.filter((r) => r.ok).length;
    const state = oks === rs.length ? "pass" : oks === 0 ? "FAIL" : "FLAKY";
    if (state === "pass") pass++;
    else if (state === "FAIL") fail++;
    else flaky++;
    rows.push({ f, rs, state });
  }
  const ok = fail === 0 && flaky === 0;
  const runs = o.repeat > 1 ? ` × ${o.repeat} runs` : "";
  const headline = `${ok ? "✅" : "❌"} ${pass} of ${features.length} features pass${runs}${fail ? `, ${fail} fail` : ""}${flaky ? `, ${flaky} flaky` : ""} (${meta.dataLabel}, commit ${meta.commit})`;
  const icon = { pass: "✅", FAIL: "❌", FLAKY: "⚠️" };
  const failLines = (r) =>
    r.checks
      .filter((c) => !c.ok)
      .map((c) => `- **${c.what}**: ${c.why}. Expected ${c.expected}; found ${c.found}.`)
      .join("\n");

  const summary = [
    `### Evidence pack: verify-web`,
    headline,
    "",
    "| Feature | Result | Checks |",
    "|---|---|---|",
    ...rows.map(({ f, rs, state }) => `| ${f.title} | ${icon[state]} ${state} | ${rs[0] ? rs[0].checks.filter((c) => c.ok).length + "/" + rs[0].checks.length : "-"} |`),
    "",
    ...rows.filter((r) => r.state !== "pass").flatMap(({ f, rs }) => [`**${f.title}**`, failLines(rs.find((r) => !r.ok)), ""]),
    `Screenshots: ${o.shots ? "360 + 1280 px, light + dark, plus " + o.lang.toUpperCase() + " at 360 px, per feature (in verify-report/)" : "off"}. Selection: ${o.changed ? `--changed vs ${o.base} (${meta.reason})` : "all features"}.`,
  ].join("\n");

  const detail = [
    `# Verify report`,
    "",
    headline,
    "",
    `- Commit ${meta.commit}; data: ${meta.dataLabel}; selection: ${o.changed ? `--changed vs ${o.base} (${meta.reason}; ${meta.changed.length} changed files)` : "all features"}`,
    `- Map: apps/web/e2e/feature-map.yaml · ${new Date().toISOString().slice(0, 16)}Z`,
    "",
    ...rows.flatMap(({ f, rs, state }) => {
      const r = rs.find((x) => !x.ok) ?? rs[0];
      if (!r) return [];
      return [
        `## ${icon[state]} ${f.title} (\`${f.id}\`)`,
        state === "FLAKY" ? `\nPassed ${rs.filter((x) => x.ok).length} of ${rs.length} runs: a flaky step. Find the cause (never retry until green).\n` : "",
        `Ends on \`${r.finalUrl.replace(/^https?:\/\/[^/]+/, "")}\` · ${r.ms} ms`,
        "",
        "Steps:",
        ...r.steps.map((s) => `${s.n}. ${s.ok ? "✓" : "✗"} ${s.label} (${s.ms} ms)${s.err ? ` — ${s.err}` : ""}`),
        "",
        "Checks:",
        ...r.checks.map((c) => `- ${c.ok ? "✓" : "✗"} ${c.what}${c.ok ? "" : `: ${c.why}. Expected ${c.expected}; found ${c.found}.`}`),
        "",
        (rs[0]?.shots ?? []).length ? "Screenshots: " + rs[0].shots.map((s) => `[${s.replace(`${f.id}--`, "").replace(".png", "")}](${s})`).join(" · ") : "",
        "",
      ];
    }),
  ].join("\n");
  writeFileSync(path.join(o.out, "verify-report.md"), detail);
  writeFileSync(path.join(o.out, "summary.md"), summary + "\n");
  return { ok, headline };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((e) => {
    console.error("verify:", e);
    process.exit(2);
  });
}
