# Open items from the old project decisions log (archived)

_Verbatim "Open" tail of the claude.ai project doc `claude/decisions.md` (last edited 15 Nov 2026), archived 2026-11-17 when the log moved to docs/spec/product-decisions.md. Live state: QUESTIONS.md, BOARD.md, workstream STATUS files._

Open: final name + domain (shortlist in repo docs/brand/name-shortlist.md; working title EV Shortlist; .eu unchecked); legal check on price sampling and finance display (brief + lawyer questions in repo research/R-03; written opinion likely €1.5–4k, estimate; layer 3 off until then); permissions (Bjørn Nyland, NAF/Motor, Spritmonitor, Fastned, Euro NCAP, EV Database, ABRP) — after the name; open-data coverage for full catalogue; affiliate programmes per launch country (none open at the big marketplaces; partner contracts needed; Carwow used-car leads DE/UK fit; repo docs/growth/affiliates.md); affiliate links live from day 1?; confirm emerging-market order; battery-savvy review of the chemistry explainer text before launch; keep Cahier off or account for it; repo security settings by hand; QUESTIONS Q-002 pnpm + uv, Q-003 require PRs on main, Q-008 maker documents, Q-037 RDW attribution, Q-093 free data accounts (Copernicus CDS, ABRP), Q-094 EAFO + RDW licence emails.

Charging buildout follow-ups (no Menno input needed): official maps for NL/BE/NZ; ABRP model-code list (needs ABRP account, Q-093).

Bidirectional follow-ups (no Menno input needed): car-side ISO 15118-20 support per maker (only VW official so far); monthly re-check of bidi status per country.

Trip fit follow-ups (no Menno input needed): Valhalla sizing test for NL+BE+LU+DE+FR+UK + Hetzner price; fit warm-up kWh per cold start and towing/roof-box factors from data; heat_pump option status for top-40 used (R-21 partial, ~20 models open); back-test harness on El Prix routes + Bjørn tests; GDPR note for trip data (repo research/R-04 — 200 m rounding doesn't anonymise a rural home; Umami consent exemption 🔴 in DE); Bjørn Nyland permission now also covers consumption tests.

Variant finder follow-ups (no Menno input needed): remaining clues (R-22: 16 of 20 models done); EU VIN rules (R-23 partial); colour-blind-safe diff highlight (UX).

Pipeline: published releases out of git before the catalogue passes the top 40 (T-064, WS1 + WS4).

AppInfra follow-ups: busy-evening numbers (check due 19:00 UTC 15 Nov); lower shared Postgres limit 6 → 5 GB to restore the worst-case guarantee (proposed); off-site backups to Scaleway not running yet (AppInfra issue #93) — must work before EV Finder holds real data; Postgres minor version + pg_trgm need an SSH/psql check; consider Umami 512 → 768 MB when the EV site is added; write an "add an app" checklist into the AppInfra README (first EV infra task); email + Actions usage to check by hand in Scaleway/GitHub.
