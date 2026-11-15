# T-090 Open data download page
Role: WS2   Lane: apps/web   Wave: 10
Status: review (WS2, 2026-11-15, branch t-090-open-data-page)

## Goal
`/{country}/{lang}/data`: the CC BY 4.0 bundle of the current release (Decision 016), launch scope §3.

## Acceptance criteria
- [x] Lists the release's open/ files from manifest.json (Decision 035) with size, sha256 and a download link; nothing hard-coded
- [x] Licence, how to cite (release number + date), caveats, link to /about
- [x] Footer link on every page, in the sitemap, EN + NL, axe clean
- [x] Without a release (dev fixture) it says so instead of linking

## Inputs
Decisions 016, 035; data/releases/<n>/open/README.md.

## Out of scope
Serving the files from our own origin (they are release assets on GitHub; WS4 may move them to Scaleway storage later via publish.yaml).

## Handoff notes
- 2026-11-15 WS2: `src/lib/open-data.ts` parses the manifest (only https github.com links, safe file names, valid sha256; same allowlist idea as publish.yaml). When storage moves (publish.yaml new target), add its host to `HOSTS`. Page: `app/[country]/[lang]/data/page.tsx`. Tests: `src/lib/open-data.test.ts`, `e2e/open-data.spec.ts`, a11y list.

## Review
