# R-04 Privacy and GDPR: data processing notes

Researched 2026-11-15 by a WS0 researcher agent. Status of law as of that date. **Not legal advice: I am not a lawyer.** Confidence: 🟢 verified in a primary or 2+ good sources · 🟡 reasoned / one good source · 🔴 unsure.

Spec: `docs/spec/master-spec-v2.md` §9 (accounts), §11 (staff), §13 (hosting); `docs/spec/trip-fit.md` §7; Decisions 006, 013. Layer 3 price sampling: see R-03.

## Answer

EV Finder handles little personal data, and the design already keeps most of it out. The main work is paperwork and a few settings. 🟡

1. Accept two DPAs: Hetzner (a checkbox in the account) and Scaleway (the PDF in their contracts).
2. Publish a short privacy notice.
3. Set retention limits in code.
4. Keep tokens and coordinates out of URLs and logs.
5. Configure Umami minimally.

**Cookie-less Umami does not escape the ePrivacy rule by default.** The EDPB says JavaScript that tells the browser to send information falls under art. 5(3). It still fits the consent exemptions in **France (CNIL)** and very likely the **Netherlands**. **Germany has no analytics exemption**, so consent-free Umami is a 🔴 residual risk there. Recommendation: launch without a banner, with Umami in minimal mode, an opt-out link and Do Not Track / GPC honoured, and put the German question to the lawyer (R-03 §6). Trip fit's rules (addresses stay in the browser, ~200 m rounding, no route logs) are good. Two gaps need closing: rounding doesn't anonymise a rural home, and share or state URLs must never carry coordinates.

## 1. Controller and setup

- **Controller:** Menno as a sole trader (Dutch KvK registration, living and working in France). 🟢
- **Lead supervisory authority:** probably the authority of the "main establishment", i.e. where decisions are taken. For a sole trader living in France that likely means the **CNIL**, not the Dutch AP. 🔴 Ask the lawyer; it decides whose guidance wins.
- **DPO:** not required (no large-scale systematic monitoring, no special categories). 🟡
- **Record of processing (art. 30):** the under-250-staff exemption doesn't cover regular processing, so keep the table in §2 as the record. 🟡
- **UK users:** UK GDPR may apply (services offered to UK users), possibly with an art. 27 UK representative. 🟡 Check before the UK launch.

## 2. What personal data exists

| Data | Where | Lawful basis (art. 6) | Retention (proposal) | Conf. |
|---|---|---|---|---|
| Account: email, passkey public key, settings (country, language, budget, home charging) | Postgres, user schema | Contract (b) | Until deletion; delete after 24 months inactive, with 30 days' email warning | 🟡 |
| Magic-link token | Postgres (hash only) | Contract (b) | 15 min, single use | 🟢 |
| Session cookie | Browser + Postgres | Contract (b); strictly necessary, no consent | 30 days rolling | 🟢 |
| Favourites, shortlists, notes, saved comparisons | Postgres | Contract (b) | With the account | 🟢 |
| Trip fit: trip names + route summaries (km per band, climb, starts) | Postgres | Contract (b) | With the account | 🟡 |
| Share links (read-only) | Postgres token | Contract (b) | Until revoked or account deleted | 🟢 |
| "Report a data issue": text, optional name/credit, optional email | Postgres, review queue | Legitimate interest (f) | Text kept as provenance; email deleted 12 months after resolution | 🟡 |
| Transactional email (magic link, alerts, digest) | Scaleway TEM | Contract (b); a newsletter would need consent (a) | Provider logs: 🔴 check Scaleway's retention | 🟡 |
| Server/proxy logs (IP, UA, path) | Caddy on CAX31 | Legitimate interest (f): security, abuse | 14 days, IP masked if possible | 🟡 |
| Error reports | GlitchTip (self-hosted) | Legitimate interest (f) | 30 days; scrub emails/IPs | 🟡 |
| Analytics events | Umami (shared AppInfra instance) | Legitimate interest (f) + ePrivacy exemption (§4) | 13 months (CNIL ceiling 25) | 🟡 |
| Staff accounts and the audit trail of edits | Postgres | Contract / legitimate interest | Audit trail kept with facts (provenance) | 🟡 |
| Backups | Hetzner + nightly dumps | Same as source | 14 days; deletions reach backups within 14 days (say so in the notice) | 🟢 spec |

**Not collected:** addresses or coordinates from Trip fit (browser only), raw route requests, listing seller data (R-03), payment data, social logins. 🟢 per spec

## 3. Processors and DPAs

| Processor | Role | DPA | Location | Conf. |
|---|---|---|---|---|
| Hetzner Online | Shared CAX31, Valhalla box, backups | Concluded in the account at accounts.hetzner.com (checkbox, no signature); list data types and data subjects | EU, Germany (choose EU locations only) | 🟢 |
| Scaleway | Transactional email; object storage (raw catalogue snapshots, no user data) | DPA and technical/organisational measures PDF on the contracts page | EU (France) | 🟢 DPA exists; 🟡 how it is concluded |
| Bunny CDN (if used) | Edge cache, sees IPs | Check its DPA before enabling | EU (Slovenia) | 🔴 not checked |
| GitHub | Code and CI only | No user data may enter issues, CI logs or fixtures | US | 🟡 |

Self-hosted Umami, GlitchTip and Uptime Kuma run under Hetzner's DPA; there is no separate processor. 🟡 AppInfra runs the shared server, but it's the same controller (Menno), so no DPA between apps. Keep separate databases and Umami website IDs anyway. 🟡

## 4. Cookie-less analytics and the ePrivacy rule

**The general rule.** EDPB Guidelines 2/2023 (final, Oct 2024): art. 5(3) covers more than cookies. JavaScript in which the "accessing entity instructs the browser of the user to send asynchronous requests" is gaining access (paras 32–34, 63). IP-only tracking can be caught too (paras 54–55). So "no cookies" ≠ "no consent question". 🟢

**How Umami works:** a session id is a hash with a time-rotating salt (monthly by default; daily and weekly options exist). 🟢 (`src/lib/crypto.ts`) It is likely built from website id, IP and user agent. 🟡

| Country | Rule | Umami without consent? | Conf. |
|---|---|---|---|
| FR | CNIL exemption (4 Jul 2025): only for the publisher's own audience measurement, anonymous statistics only, no linking with other processing, no sharing, no cross-site tracking. Recommended: inform users, 13-month lifetime, 25-month retention | **Yes, if configured as below** | 🟢 rule / 🟡 fit |
| NL | Telecommunicatiewet art. 11.7a(3)(b): analytics for your own service with little or no privacy impact; mask IPs, no sharing, no combining, no ads, DPA with any provider | **Likely yes** | 🟡 |
| DE | TDDDG §25: only two exceptions (transmitting a message; a service the user expressly asked for), read narrowly; the DSK guidance (v1.2, Nov 2024) names no analytics exception | **Uncertain to no** | 🔴 |
| EU future | Digital Omnibus: the Council mandate (21 Oct 2026) would allow anonymous first-party audience measurement without consent. Parliament has no position, trilogues haven't started, no application date | Not yet law | 🟢 status |

**Minimal Umami setup (required):**
- Monthly salt or shorter.
- Exclude `/auth/*`, `/me/*` and `/staff/*` paths.
- Strip query strings except the filter params we choose (never tokens).
- No custom events with user ids.
- Honour Do Not Track / GPC.
- Opt-out link in the privacy notice.
- One website id per app, with no cross-site identifier.
- Disclose it in the notice.

Recommendation: no banner at launch, with the German risk logged in DECISIONS and asked of the lawyer. If the answer is "consent needed", the fallback is to not load Umami for DE visitors, or count only from server logs. 🟡

## 5. Accounts, auth and logs

- **Passkeys:** we store a public key and a credential id. Biometrics never leave the device (WebAuthn). 🟡
- **Magic links:** the token sits in a URL, so make sure it never reaches Caddy access logs, Umami or GlitchTip. Exchange it by POST from the landing page, or filter `/auth/*` from logs. 🟡
- **Caddy logs:** mask IPs with a log filter (`ip_mask`), keep 14 days, no request bodies. 🟡
- **Export (art. 15/20):** one JSON download from `/me` with account, settings, lists, comparisons, trip summaries, reports and share links. 🟢 spec
- **Delete (art. 17):** one click; hard delete in Postgres immediately; backups age out within 14 days; anonymise the reporter id on data reports, keep the fact provenance. 🟡
- **Staff "Users" tool:** look-up and delete only, every access logged. Staff can't read private notes unless handling a request. 🟡

## 6. Trip fit privacy rules

What the spec already does well (Decision 013):

- Addresses never reach the server; GeoNames town search runs in the browser.
- Coordinates are rounded to ~200 m before routing.
- No request logging on the route endpoint.
- Accounts store trip names and summaries only.
- Share links carry summaries only.

Gaps to close:

| Gap | Fix | Owner | Conf. |
|---|---|---|---|
| ~200 m rounding still points to one house in rural areas, so it's still personal data in transit | Treat it as personal data: process transiently, never log, never cache by coordinate. Optionally snap to the nearest road node | WS2 + WS4 | 🟡 |
| "No logging" must hold at every hop: Caddy/proxy, Valhalla's own logs, GlitchTip breadcrumbs | Turn off access logs for the route path at the proxy and in the Valhalla config; scrub request bodies in error reports; test it | WS4 | 🟡 |
| URL state ("state never gets lost") could put coordinates in the URL, where Umami and Referer headers pick them up | Keep trip places in local storage only; the URL carries trip ids or summaries; `Referrer-Policy: strict-origin-when-cross-origin` | WS2 | 🟡 |
| Trip names can reveal places ("Home → Mum's in Lyon") | Hint in the UI: "Names are saved to your account; avoid addresses" | WS2 | 🟡 |
| Separate Valhalla box | Same Hetzner DPA; firewall so only ev-web can call it | WS4 | 🟢 |

A DPIA is probably not mandatory, but do a one-page DPIA-lite for Trip fit (location data). 🟡

## 7. What goes in the privacy notice

1. Who we are: Menno, sole trader, KvK number, contact email and postal address.
2. What we collect and why, with the lawful basis per purpose (table §2, plain language).
3. What we don't collect: Trip fit addresses, ads trackers, cookies beyond the login cookie.
4. Analytics: Umami, cookie-less, self-hosted, what it records, retention, opt-out.
5. Processors and locations: Hetzner (DE), Scaleway (FR), and any CDN.
6. Retention per category, including the 14-day backup lag.
7. Rights: access, export, correction, deletion, objection; how to use them (the `/me` buttons plus email); the right to complain to the CNIL (or the AP for Dutch users).
8. Transfers outside the EU: none for user data.
9. Data reports: what happens to the text and to an optional name or email.
10. Changes and date of the notice, in the six site languages.

## 8. Checklist

| # | Item | Owner | Phase |
|---|---|---|---|
| 1 | Conclude the Hetzner DPA in the account (both boxes) | Menno / WS4 | Before staging |
| 2 | Download and file the Scaleway DPA; check email log retention | Menno / WS4 | Before staging |
| 3 | Caddy: `ip_mask` log filter, 14-day rotation, no logs for `/auth/*` and the route path | WS4 | Before staging |
| 4 | Valhalla: access logging off, firewall to ev-web only | WS4 | Before launch |
| 5 | Umami minimal config (§4), path exclusions, DNT/GPC | WS2 + WS4 | Before launch |
| 6 | Magic-link token exchange by POST, token hashed, 15 min TTL | WS2 | Before staging |
| 7 | Retention jobs: inactive accounts, report emails, GlitchTip 30 days | WS2 | Before launch |
| 8 | Export JSON and one-click delete, with tests | WS2 | Before launch |
| 9 | Trip fit: no coordinates in URLs, local storage only, Referrer-Policy | WS2 | Before Trip fit ships |
| 10 | GlitchTip PII scrubbing (emails, IPs, query strings) | WS2 | Before staging |
| 11 | Privacy notice in six languages + footer link + opt-out | WS3 (text) / WS2 | Before launch |
| 12 | Record of processing (this table) and Trip fit DPIA-lite filed in `docs/` | WS0 | Before launch |
| 13 | Ask the lawyer: lead authority, Germany §25, UK representative | Menno | Before launch |
| 14 | Log a DECISIONS entry: "no cookie banner, Umami minimal, DE risk accepted pending advice" | WS0 | Before launch |

## Sources (opened 2026-11-15)

- EDPB Guidelines 2/2023 on the technical scope of art. 5(3) ePrivacy, v2 (Oct 2024): https://edpb.europa.eu/system/files/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf
- Hunton, EDPB adoption note: https://www.hunton.com/privacy-and-cybersecurity-law-blog/edpb-adopts-guidelines-on-scope-of-eprivacy-directive
- CNIL, audience measurement solutions (4 Jul 2025): https://www.cnil.fr/fr/solutions-pour-la-mesure-daudience
- Ondernemersplein (NL government), cookies on your website: https://ondernemersplein.overheid.nl/wetten-en-regels/gebruik-van-cookies-op-uw-website/
- Law & More, Dutch analytics cookie exemption: https://lawandmore.eu/cookies-analytics-and-online-advertising-in-the-netherlands-staying-gdpr-compliant/
- 2B Advice, DSK guidance on digital services (Nov 2024): https://2b-advice.com/en/2024/11/28/data-protection-requirements-for-digital-services-according-to-the-new-orientation-guide-of-the-data-protection-conference/
- Relevant Audience, Digital Omnibus Council mandate (Oct 2026): https://www.relevantaudience.com/analytics/eu-council-digital-omnibus-cookie-consent/
- Umami source, `src/lib/crypto.ts`: https://github.com/umami-software/umami/blob/master/src/lib/crypto.ts
- Hetzner, data protection and DPA: https://docs.hetzner.com/general/company-and-policy/data-protection-at-hetzner
- Scaleway, contracts (DPA, TOMs): https://www.scaleway.com/en/contracts/
- CNIL scraping guidance and *KNLTB*: see R-03 sources.
