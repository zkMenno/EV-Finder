# A-01 Threat model and security baseline

Audit type: security (baseline, before any code reaches staging). Written 2026-11-15 by a WS0 researcher agent. Not a penetration test. Confidence: 🟢 verified · 🟡 reasoned · 🔴 unsure.

Inputs: AGENTS.md, Decisions 004, 005, 006, 013, spec §9, §11, §13, `docs/spec/trip-fit.md` §7, R-04.

## Answer

The biggest risks aren't exotic. In order:

1. **A poisoned dependency or CI workflow** that steals the deploy SSH key. That key reaches a server shared with two other apps.
2. **Staff-area takeover**, since the staff area can rewrite published data.
3. **SSRF from pipeline fetchers** into the private network, the shared Postgres or Hetzner metadata.
4. **Stored XSS or prompt injection** through user reports and scraped source text.
5. **Abuse of the route endpoint.**

Being open source helps reviewers, but attackers can read the code too, so nothing may depend on secrecy of code (Decision 004 already keeps targets and keys in config). 🟡 A baseline of 24 controls follows. 15 are needed before staging, mostly CI and server settings.

## Assets

| Asset | Why it matters |
|---|---|
| Catalogue releases + provenance | The product is trust; silent tampering is the worst outcome |
| User data (emails, lists, trip summaries) | GDPR; small, but real |
| Deploy SSH key, GHCR token, DB passwords, Scaleway keys, partner/affiliate creds | Keys to the shared server and to revenue |
| The shared CAX31 and its Postgres (GardenLayer, Dungeon Tracker too) | One compromise hits three apps |
| Valhalla box | Availability; it sees rounded coordinates in transit |
| GitHub repo and Actions | Build chain to production |

## Trust boundaries

1. Internet → Caddy → ev-web (public pages, `/me`, `/staff`, route API)
2. ev-web → Valhalla box (private network)
3. ev-jobs → the internet (source fetchers) and → Scaleway object storage
4. Containers → shared Postgres (one database and login per app)
5. GitHub (fork PRs, agent branches, Actions) → GHCR → SSH deploy → server
6. Our app ↔ neighbour apps on the same host (Docker, Caddy, Umami, Postgres)

## Threats (STRIDE)

| Area | Threat | STRIDE | Likelihood / impact |
|---|---|---|---|
| Staff area | Phished or stolen staff session; no second factor; CSRF on accept/override actions | S, E | Medium / high |
| Staff area | Edits bypass provenance, or edits by an account later deleted can't be traced | R, T | Medium / high |
| Review queue | Stored XSS in "Report a data issue" text, rendered in staff UI | T, E | Medium / high |
| Review queue | Prompt injection in source pages or reports steers the LLM that "suggests" values | T | Medium / medium (rules decide, per data rule 5) |
| Review queue | Report spam floods the queue | D | High / low |
| Auth | Magic-link token leaks via logs, Referer or analytics; link reused; email enumeration | S, I | Medium / medium |
| Auth | Account takeover via mail account; session fixation | S | Low / medium |
| Route endpoint | Flood of route calls drives Valhalla CPU; used as a free routing API | D | High / medium |
| Route endpoint | Coordinates logged somewhere (proxy, error tracker) | I | Medium / medium |
| Pipeline fetchers | SSRF: a source URL (config, staff YAML, redirect, DNS rebinding) points at Postgres, internal services or 169.254.169.254 | I, E | Medium / high |
| Pipeline fetchers | Malicious files (zip bombs, huge PDFs, XML entities) exhaust the 1 GB job limit | D | Medium / low |
| Pipeline fetchers | Poisoned source data published as fact | T | Medium / high |
| Supply chain | Compromised npm/PyPI package (cf. Shai-Hulud, Sept 2025: postinstall scripts harvested CI secrets and self-propagated); agents adding typosquatted packages | T, E, I | Medium / critical |
| GitHub Actions | `pull_request_target` or script injection runs fork code with secrets; unpinned third-party actions; over-broad `GITHUB_TOKEN` | E, I | Medium / critical |
| GitHub Actions | Secrets printed in logs of a public repo | I | Low / high |
| Shared server | A neighbour's compromise reads our DB or env files; Docker socket access = root | E, I | Low / critical |
| Shared server | A neighbour or our job eats RAM/CPU (Postgres has no CPU limit) | D | Medium / medium |
| Public repo | Secret committed; sampling targets leaked (Decision 004) | I | Medium / high |

## Baseline controls

| # | Control | Owner | Phase |
|---|---|---|---|
| 1 | Actions: pin third-party actions to full commit SHA; default `permissions: contents: read`; no `pull_request_target` for code that checks out PRs; pass untrusted inputs via env vars, not `${{ }}` in scripts | WS4 | Before staging |
| 2 | Deploy secrets only in a protected `production` environment, used only by `push` to `main`; PR workflows get no secrets; no self-hosted runners | WS4 | Before staging |
| 3 | Deploy key: dedicated deploy user, `authorized_keys` forced command (pull + restart only), no shell | WS4 | Before staging |
| 4 | Secret scanning + push protection on (Decision 004); gitleaks in CI | WS4 | Before staging |
| 5 | Lockfiles committed; `pnpm install --frozen-lockfile`; build scripts allowed only for listed packages (pnpm `onlyBuiltDependencies`); `uv sync --locked` | WS2 / WS1 | Before staging |
| 6 | New dependency = PR note with reason (AGENTS.md) + reviewer checks name, age, downloads; Dependabot with a short cool-down before auto-PRs on new releases 🟡 | WS0 review | Before staging |
| 7 | Containers: non-root user, read-only root FS where possible, no Docker socket mounted, memory/CPU limits (Decision 006) | WS4 | Before staging |
| 8 | Postgres: own DB + login per app, no superuser for apps, `pg_hba` limited to the app's private network; separate role for ev-jobs (writes catalogue) vs ev-web (reads catalogue, writes user schema) | WS4 | Before staging |
| 9 | Env files per app, mode 600, owned by that app's deploy user; no shared keys between apps | WS4 | Before staging |
| 10 | Staff: passkey required (no magic-link-only), short sessions, re-auth for bulk actions, role check on every server action, CSRF protection | WS2 | Before staging |
| 11 | Every staff edit goes through the provenance layer with the actor id; append-only audit log | WS2 | Before staging |
| 12 | Render all user and source text as text (React escaping, no `dangerouslySetInnerHTML`); strict CSP with nonces; `frame-ancestors 'none'` | WS2 | Before staging |
| 13 | Magic links: hashed, single-use, 15 min; exchanged by POST; same response whether or not the email exists; rate-limited per IP and per email | WS2 | Before staging |
| 14 | Fetchers: allowlist of hosts from the source registry; resolve and block private, loopback, link-local and metadata ranges (IPv4 + IPv6); re-check after DNS; no automatic redirects (or re-validate each hop); size and time caps; ev-jobs egress firewall | WS1 / WS4 | Before staging |
| 15 | Parsers: safe XML (no entities), zip and PDF size limits, files processed in a temp dir with a size quota | WS1 | Before staging |
| 16 | LLM outputs are suggestions only: schema-validated, rule-checked, never auto-published below the threshold; source text is fenced as data in prompts | WS1 | Before launch |
| 17 | Release diff gate: large or unusual changes need staff approval before publish; one-step rollback tested | WS1 | Before launch |
| 18 | Route API: requires a same-origin token, rate limit per IP (e.g. 30/min), coordinate and length bounds, timeout; Valhalla reachable only from ev-web | WS2 / WS4 | Before launch |
| 19 | Rate limits and a honeypot or proof-of-work on "Report a data issue"; queue cap per IP per day | WS2 | Before launch |
| 20 | Logging hygiene: no tokens, coordinates or bodies in logs; GlitchTip scrubbing (R-04) | WS2 / WS4 | Before launch |
| 21 | Security headers at Caddy: HSTS, `Referrer-Policy: strict-origin-when-cross-origin`, `X-Content-Type-Options`, Permissions-Policy | WS4 | Before launch |
| 22 | Off-site backups working (AppInfra #482) and one restore test | WS4 | Before launch |
| 23 | SECURITY.md disclosure contact + GitHub private vulnerability reporting on | WS0 | Before launch |
| 24 | Weekly dependency audit (`pnpm audit`, `pip-audit` / `uv`), per audits/README.md | WS0 | Before launch |

**Open questions:** do the neighbour apps share a Docker host user or Caddy admin API with us? Is the Caddy admin endpoint bound to localhost only? 🔴 Check with AppInfra.

## Sources (opened 2026-11-15)

- GitHub Docs, Secure use / security hardening for GitHub Actions: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- OWASP SSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- CERT/CC VU#534320, npm supply chain compromise (Shai-Hulud), Sept–Oct 2025: https://kb.cert.org/vuls/id/534320
- R-04 (privacy, logging) in this repo.
