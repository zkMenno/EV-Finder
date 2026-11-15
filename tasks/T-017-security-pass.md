# T-017 Security pass
Role: coordinator   Lane: audits/   Wave: 4
Status: review (reviewer agent, 2026-11-15)

## Goal
No secrets, dependency audit, safe Caddy headers, no third-party browser calls.

## Acceptance criteria
- [x] Findings in audits/A-02
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes
**Reviewer, 2026-11-15.** See `audits/A-02-security.md`. No critical/high findings in production code or runtime deps.
- Secrets scan of the whole tree: clean (only `.env.example` placeholders and a third-party sample in git-ignored `data/raw/`).
- `pnpm audit --prod`: 0. `pnpm audit`: 16 dev-only (vitest 2.1.9 chain, minimatch). `pip-audit` on the pipeline: 0.
- Headers: app CSP `default-src 'self'` (+ `'unsafe-inline'` scripts for Next); Caddy adds HSTS, Permissions-Policy, XFO, `object-src 'none'`.
- New e2e "every page talks only to our own origin" across 9 pages: 0 foreign requests.
- Staff page 404 unless `STAFF_PAGES=1`; `/health` returns only status/release/time; listing links `nofollow noopener`; no marketplace fetching anywhere.
- Top fixes: run e2e in CI (Medium), upgrade vitest ≥ 4.1.12 (Medium, dev-only criticals), nonce-based CSP later (Medium, defence in depth), Dependabot for npm/uv (Low).

## Review
