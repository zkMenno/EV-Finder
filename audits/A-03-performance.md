# A-01 Performance budget (T-016)

**Type:** performance · **Date:** 2026-11-15 · **Auditor:** reviewer agent (fresh), branch `proto/overnight-1` · **Data:** release 1 (210 variants)

## Method

- `pnpm --filter @ev/web build`, then `next start -p 3200` from `apps/web` with the default `CATALOGUE_DIR` (release 1). Note: `next start` warns that `output: "standalone"` wants `node .next/standalone/server.js`; bundles are the same files.
- **JS:** every `<script src>` on `/nl`, each fetched and gzipped (`gzip -9`), `noModule` polyfills counted separately. Cross-checked with Playwright (Chromium): recorded every script response the page loads up to network idle + 1 s, gzipped in Node. Both give the same 8 modern scripts, no lazy chunks after hydration.
- **Catalogue:** `/data/catalogue-1.json` as served, and `data/releases/1/catalogue.json` on disk, raw and `gzip -9`.
- **HTML / render time:** `curl -w %{time_starttransfer} %{time_total}` on localhost, right after a server restart (cold) and repeated (warm).

## Results

| Metric | Actual | Budget | Verdict |
|---|---|---|---|
| Explore `/nl` first-load JS, modern browsers (8 scripts) | **159.2 KB gzip** (155.5 KiB); 531.5 KB raw | < 200 KB gzip | **Pass** (41 KB headroom) |
| … plus the `noModule` polyfills (skipped by modern browsers) | 198.6 KB gzip (39.4 KB polyfills) | — | info |
| Client catalogue `/data/catalogue-1.json` | **34.7 KB gzip** (35.8 KB on the wire with `next start` compression); 915 KB raw; `Cache-Control: public, max-age=31536000, immutable` | < 300 KB gzip | **Pass** |
| Full release `data/releases/1/catalogue.json` (server only, never sent to the browser) | **97.0 KB gzip**; 1.97 MB raw | < 300 KB gzip | **Pass** |
| `/nl` HTML | 424 KB raw / **29.6–29.8 KB gzip** | — | info |
| `/nl` server render, cold (first request after start) | 157 ms TTFB | — | info |
| `/nl` server render, warm (n=15) | 17–56 ms total, median ≈ 23 ms | — | good |
| Other pages, warm, gzip size | `/nl/top` 12 ms / 6.7 KB; `/nl/top/fastest-dc` 26 ms / 16.2 KB; `/nl/compare?ids=…` 20 ms / 14.5 KB; `/nl/learn/real-range` 13 ms / 6.8 KB; `/health` 5 ms | — | info |

Largest scripts (gzip): 71.6 KB and 46.2 KB (React/Next runtime), 13.5 KB, 10.8 KB, 7.7 KB, 3.9 KB (Turbopack runtime), 3.5 KB, 2.0 KB. Matches the builder's figure (~156 KB) within rounding; `apps/web/AGENTS.md` rule 4 still holds.

## Findings

| Severity | Finding | Suggested fix |
|---|---|---|
| Low | `/nl` HTML is 424 KB raw (29.7 KB gzip): 25 rows × popover markup plus the RSC payload and taxonomy. Fine over gzip, but parsing cost on low-end phones grows with rows. | Keep 25 server rows; consider rendering popover bodies only on open. |
| Low | The client catalogue repeats provenance objects per field (915 KB raw). Gzip hides it (34.7 KB), but JSON.parse time on phones scales with raw size. | De-duplicate provenance (index into a table) when the catalogue passes ~2 MB raw. |
| Info | No automated budget check: the JS number is measured by hand. A regression would go unnoticed. | Add a CI step (or Playwright test) that sums gzipped script responses on `/nl` and fails above 200 KB. Proposed task: **T-0xx perf budget check in CI**. |
| Info | Measured with `next start`; production uses the standalone server behind Caddy (`encode zstd gzip`), so real wire sizes will be a little smaller. | Re-measure on staging once it exists. |

**Verdict: both budgets met.** No blocking findings.
