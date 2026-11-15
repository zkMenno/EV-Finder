# Launch plan: [site name]

Status: proposed 2026-11-15 · Owner: WS5 growth, run by Menno solo · Budget: no ads, no paid placement · Legend: 🟢 verified · 🟡 reasoned · 🔴 unsure

**The answer.** Launch with something people can use and something they can cite. The product is the Explore table (no sign-up). The citable part is a small open dataset under CC BY 4.0: real winter range for the 40 most-bought used EVs, plus charger counts per launch country. Build a short double-opt-in waitlist before launch, release the dataset two weeks ahead to earn links, then launch country by country in the communities where used-EV buyers already ask questions. Lead everywhere with one hook, "The range you truly need". Answer people's questions with numbers and sources, and mention the site only when it helps. Keep the plan small enough for one person: three channels at a time, posts written in batches.

**Decision needed.** The spec tags open summaries "Next" (§14). A launch dataset of a few hundred rows pulls a slice forward. Ask WS0 to approve it in DECISIONS.md. Without it, the fallback hook is the Top 10 rankings with method notes.

## 1. Pre-launch (launch day L; about 8 weeks before)

| Item | What | Why |
|---|---|---|
| Waitlist | One page, one email field, double opt-in, EU-hosted mailer. Promise: one email at launch and a monthly digest at most | Only owned channel at the start; no cookies needed |
| Open data release (L-14) | `/data/real-range` and `/data/charging`: CSV/JSON, CC BY 4.0, method page, release number and date | Link bait for journalists, forums and AI assistants |
| Public repo | Already public; add a short README section on data and method | Gives Hacker News its angle |
| Seed content | 10 Top 10 rankings and 4 /learn pages live and indexed | Search traffic starts before launch |
| Private beta | 20–30 people from owner forums try 3 tasks (spec §4 "test with normies") | Fixes confusing terms; creates first advocates |
| Permissions | Email Bjørn Nyland, NAF/Motor, Spritmonitor first (Phase 0 checklist); credit them in the dataset | Avoids a trust problem on day one |
| Measurement | Umami events and UTM scheme live | See section 6 |

## 2. The content hook: "The range you truly need"

Built from the Trip-fit spec. A person says where they drive; we show which used EVs make those trips in winter without charging.

- **Headline claim, sourced:** Recurrent measured roughly 80% of range kept at 0 °C, 83% with a heat pump versus 75% without 🟢 (Trip-fit §2). NAF's winter 2026 test averaged 38% below WLTP at down to −32 °C 🟢. Use these with their conditions, never a flat "minus 30%".
- **Formats:** (1) a one-page explainer per country in its language; (2) the quick Trip-fit version as a shareable URL; (3) three screenshots per post showing one car, one number, one source.
- **Repurpose:** each article becomes a forum answer, a short video script and a newsletter item.

## 3. Channels per country

Do not post in a community before you have read its current rules 🔴: I could not open Reddit's rules pages from this environment, and I have not verified forum rules. Start by answering questions for two weeks. Self-promotion limits vary by community.

| Country | Where | Approach |
|---|---|---|
| NL | Tweakers (Elektrische Auto's forum and the news desk), r/Nederland and any Dutch EV subreddit (check which exist) 🔴, Dutch EV Facebook groups | Pitch Tweakers a data story; answer used-buyer questions with generation-level prices |
| DE | GoingElectric forum (per-model sub-forums exist), Facebook groups, r/de | Post the German winter-range table in the matching model sub-forum, with sources |
| FR | Automobile Propre (press and comments), Forum-Auto 🟡, r/france, Facebook groups | Press note with the French charger series (202,804 points, end Sep 2026 per spec) |
| BE | Same NL and FR channels, company-car angle (lease-end EVs) | Use the Belgian lease-return story from the spec |
| UK | Speak EV forum, r/electricvehicles, r/UKPersonalFinance only if on topic 🟡, Facebook groups | Lead with used prices and the DfT figure of 121,171 public chargers (1 Jul 2026) |
| Global/English | r/electricvehicles, r/teslamotors, Hacker News, Product Hunt | See below |

- **Hacker News "Show HN".** Rules ([HN Show guidelines](https://news.ycombinator.com/showhn.html)) 🟢: it must be something people can try without signing up; landing pages and sign-up pages don't qualify; title starts "Show HN"; don't ask friends to upvote. We qualify only because Explore needs no account. Angle: open data, open repo, derived-not-copied method. Post on a weekday morning (US Eastern) and stay in the thread for hours.
- **Product Hunt.** Low fit for consumer car buyers 🟡. Do it once, after launch, for backlinks and a few early adopters; not a main channel.
- **Reddit.** Contribute first. Post the dataset as a text post with the method, not a link-only post. One subreddit per week.
- **Facebook groups.** Ask admins before posting. Useful for NL, DE and FR owner clubs.

## 4. Partnerships and press

- **YouTubers (borrowed audience).** Offer a free walkthrough and the data for their model, no payment, no say over rankings. Approach 5 creators per language, starting with the ones whose tests we already credit. Their tests are our best input, so ask for permission and credit first. Give each a trackable link. Affiliate links on our side need a visible disclosure.
- **Owner clubs and forums.** Offer per-model fact checks: "we got your car's winter range from 3 sources, tell us where it is wrong." Corrections are content.
- **Press angles** (pitch a journalist with the figure, the method and a CSV):
  1. "What a used EV really does in winter: 40 models compared" (Tweakers, Automobile Propre, UK EV press).
  2. "Charger counts per country, year on year" from the open charging series (DE 212,064; UK 121,171; FR 202,804, per the spec's sources).
  3. "Same used car, five prices": cross-border price gaps per generation.
  4. A solo, EU-hosted, independent finder: no ads, no paid rankings.
- **Marketplaces and data partners.** Separate track (spec §8): keep editorial independence in writing before any affiliate deal.

## 5. 90-day calendar

Week 0 is launch week; countries open in sequence so one person can answer every thread.

| Weeks | Focus | Actions |
|---|---|---|
| L-8 to L-6 | Foundations | Waitlist live; permissions emails; beta recruiting; rankings and /learn indexed |
| L-5 to L-3 | Proof | Beta feedback fixes; dataset and method page written; 5 forum accounts warmed by helping |
| L-2 | Data release | Publish dataset; email 10 journalists and 5 creators per language; post in data-friendly spots |
| L-1 | Prep | Launch assets, FAQ, answer snippets; check errors in top 40 models |
| L0 | NL + UK | Waitlist email; Show HN (Tuesday–Thursday); Tweakers pitch; r/electricvehicles post |
| L+1 | DE | GoingElectric posts; German press note |
| L+2 | FR + BE | Automobile Propre note; Belgian angle |
| L+3 to L+4 | Listen | Fix top 10 reported errors; publish "what we got wrong" note; first creator videos |
| L+5 to L+8 | Compound | Monthly dataset release 2; one winter-range explainer per country; Product Hunt |
| L+9 to L+12 | Review | 90-day retro; prune channels under 5% of signups; decide on paid or sponsor support |

## 6. Measurement without cookies

Umami (self-hosted, no cookie banner, per spec) plus Search Console. Counts are approximate because visitors are not tracked across days; read trends, not single values.

| # | Metric | Target 🟡 | Source |
|---|---|---|---|
| 1 | Weekly active hunters (compare, favourite or save) | +10% per month (spec) | Umami events |
| 2 | Compare rate (sessions that compare 2+ cars) | ≥ 25% (spec) | Umami events |
| 3 | Outbound "See listings" clicks per 100 sessions | ≥ 15 (spec) | Umami events |
| 4 | Waitlist and email signups by channel | Set baseline in week 1 | UTM plus mailer |
| 5 | Organic clicks and share of submitted URLs indexed | Indexed ≥ 80% of sitemap in 8 weeks | Search Console |

Every outside link carries `utm_source` and `utm_campaign`. Once a month, check AI citations for 20 queries (see the SEO plan).

## 7. Risks

| Risk | Likelihood | Response |
|---|---|---|
| Community sees promotion and bans or downvotes | Medium | Help first; follow each community's rules; use data posts, not links |
| A wrong number goes viral | Medium | Confidence badges, visible corrections log, fast fixes, "report an error" on every figure |
| Creators or data owners refuse permission | Medium | Use fallback range model and credit; never use data without a yes |
| Marketplace objects to price sampling | Low–medium | Kill switch per site (spec §8); legal check before layer 3 |
| Thin or untranslated pages hurt indexing | Medium | Data gate and review rule (SEO plan) |
| Solo bandwidth | High | Max 3 active channels; batch posts; stagger countries; drop the weakest channel at week 6 |
| Hacker News post gets no traction | Medium | It is one attempt, not the plan; keep the data release as the evergreen asset |

## Sources

- Spec mirrors in `docs/spec/`: master-spec-v2.md (§4, §14, §15), trip-fit.md, charging-buildout.md, research-and-notes.md
- [Hacker News: Show HN guidelines](https://news.ycombinator.com/showhn.html) (opened 2026-11-15)
- [GoingElectric forum](https://www.goingelectric.de/forum/?lang=en) (appeared in search 2026-11-15; rules not read)
- Reddit rules pages: blocked in this environment, not read. Forum rules for Tweakers, Automobile Propre and Speak EV: not read.
- Marketing skills used: launch, community-marketing, content-strategy
