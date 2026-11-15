# R-03 Legal brief: automated used-price sampling (layer 3)

Researched 2026-11-15 by a WS0 researcher agent. Status of law as of that date. **Not legal advice: I am not a lawyer.** This brief exists to make a one-off lawyer opinion short and cheap. Confidence: 🟢 verified in a primary or 2+ good sources · 🟡 reasoned / one good source · 🔴 unsure.

Spec: `docs/spec/master-spec-v2.md` §8 (layers 0–3), `docs/spec/marketplaces.md`. Decision 004.

## Answer

Layer 3 is **defensible in principle but not safe to switch on without a lawyer**, and the risk differs a lot per site and country. 🟡 Three things decide it:

1. **Database right.** Big marketplaces clearly hold the EU sui generis right (French courts have upheld it for leboncoin twice, with €50k damages each time). Daily systematic extraction of small parts can add up to a substantial part (Art. 7(5)). Our best argument is the CJEU's *CV-Online* test: extraction is only prohibited if it puts the maker's investment at risk, and price aggregates don't replace their listings. Marketplaces will answer that our bands compete with their own price ratings. 🟡
2. **The text-and-data-mining (TDM) exception (DSM art. 4)** fits what we do (automated analysis to produce trends) and covers *extraction* from databases, **but only where the site has not opted out in a machine-readable way**. Most big marketplaces will have opted out (robots.txt, ToS, TDM headers). Courts disagree about what counts as machine-readable. Once a site has opted out, the exception is gone. 🟡
3. **Terms of service** almost always ban bots. Whether that binds a non-logged-in visitor differs by country. Getting around any technical barrier (CAPTCHA, IP blocks, login) changes the picture in every country and is a hard red line. 🟢

GDPR is manageable if we never store raw result pages and drop seller fields in memory. 🟡 The UK is the weakest case: its database right still applies and its TDM exception is non-commercial only. 🟢

**Recommended default:** layer 3 **off** everywhere. Ship layers 0–2 (and 1 where feeds exist). Book a written opinion (estimate €1.5k–4k, see below) before Phase 3, scoped to the first two countries where partnerships fail.

## 1. EU database right (Directive 96/9/EC, sui generis)

| Point | What it means for us | Conf. |
|---|---|---|
| Who is protected | The maker of a database built with a "substantial investment" in obtaining, verifying or presenting its contents. A big classifieds site easily qualifies; the Paris Court of Appeal (leboncoin v Entreparticuliers, 2 Feb 2021) also protected the real-estate *sub-database* on its own and refused to measure investment against revenue. | 🟢 |
| Extraction / re-use | Read broadly: any appropriation of the results of the investment without consent. A search engine that copies and indexes another site's ads does extract and re-use (*CV-Online Latvia v Melons*, C-762/19, 3 Jun 2021). | 🟢 |
| Harm test | The maker can only stop it if the act risks its investment, i.e. its ability to recoup the investment through normal operation. Courts must weigh this against users' and competitors' interest in access and new products (*CV-Online*). | 🟢 |
| Purpose doesn't excuse | The Paris CA said the extractor's purpose is irrelevant to infringement. | 🟢 |
| Repeated small parts | Art. 7(5): repeated, systematic extraction of insubstantial parts that conflicts with normal exploitation is also banned. **Our daily job across every generation × country is exactly this pattern.** | 🟡 |
| Our position | We keep counts and p25/p50/p75 only, publish no listing, and link out (sending them traffic). That is a strong *CV-Online* argument. The weak spot: marketplaces sell price analytics (e.g. AutoScout24's price index, dealer price ratings), so our bands could be framed as a substitute. | 🟡 |

**Enforcement record.** leboncoin actively litigates: Entreparticuliers (€50k financial + €20k reputational damages, Paris CA 2021) and Jinka (Nanterre court, 31 May 2024: stop, delete extracted content, €50k). Both copied listings, which we don't. 🟢

## 2. Terms of service and contract law

- **Where no database right exists**, the site can ban scraping by contract (*Ryanair v PR Aviation*, C-30/14, Jan 2015). Where the right exists, the directive's lawful-user rights to insubstantial parts can't be contracted away. Either way the ToS matter. 🟢
- **Binding a visitor?** In the leboncoin case the ads were visible without accepting the ToS, so leboncoin could not sue on contract and used the database right instead. 🟢 Browse-wrap enforceability varies per country. 🟡
- **Germany:** the BGH (*Flugvermittlung im Internet*, I ZR 224/12, 30 Apr 2014) held that ignoring a ToS scraping ban is not by itself unfair competition, and that price transparency counts in the scraper's favour; but **overcoming a technical barrier** can make it unfair. 🟢
- **Computer-misuse law** (FR Code pénal art. 323-1, DE StGB §202a, UK Computer Misuse Act) becomes relevant once you get around access controls. Not if we stay on public pages and stop at any barrier. 🟡
- **Red lines (non-negotiable):** no login, no CAPTCHA solving, no proxy or IP rotation, no fake user agent, stop on 403/429 or a robots.txt disallow, honour a cease-and-desist the same day. 🟢 (our rules; spec §8)

## 3. Text-and-data-mining exception (DSM Directive 2019/790, art. 4)

- **Scope:** an exception to the database right (art. 7(1) of 96/9) and to copyright, "for reproductions and extractions of lawfully accessible works and other subject matter for the purposes of text and data mining" (art. 4(1)). Copies may be kept "as long as is necessary" (art. 4(2)). TDM means automated analysis to produce information such as patterns and trends (art. 2(2)); price bands fit. 🟢
- **It covers extraction, not re-utilisation.** It does not let us republish contents, which we don't. Our published aggregates are our own figures. 🟡
- **Opt-out:** the exception only applies where the rightholder hasn't reserved use "in an appropriate manner, such as machine-readable means in the case of content made publicly available online" (art. 4(3)). 🟢
- **What counts as machine-readable is unsettled:**
  - Amsterdam District Court (DPG Media v HowardsHome, ECLI:NL:RBAMS:2024:6563): a robots.txt naming only AI bots was not a valid general opt-out, so the aggregator could rely on TDM. 🟢
  - Danish Eastern High Court (BoligPortal v ReData, 12 May 2026): an opt-out in the HTML privacy policy was not machine-readable, so the injunction was lifted. 🟢 (single tracker source). BoligPortal is a rental-listings portal, so the case is close to ours. 🟡
  - German courts (Kneschke v LAION, Hamburg; appeal 10 Dec 2025) have been readier to accept natural-language ToS reservations. 🟡
- **Commercial use:** art. 4 is open to commercial users (art. 3, research only, isn't). We earn affiliate revenue, so only art. 4 is open to us. 🟢
- **Practical rule:** treat any of these as an opt-out and don't sample the site: a robots.txt disallow for our user agent or `*` on the search path, a TDMRep header or `tdm-reservation`, or a ToS clause banning TDM or automated collection. That probably rules out most big sites, which is the honest result. 🟡

## 4. GDPR (private sellers)

- Result pages can show a private seller's first name, town, sometimes a phone number or profile link. Fetching the page means processing that personal data, even for a moment. 🟢
- **CNIL (19 Jun 2025):** scraping isn't banned by itself, but under legitimate interest you must set collection criteria in advance, filter out unneeded data, delete irrelevant data at once, and exclude sites that object via robots.txt or CAPTCHAs. 🟢
- **Dutch AP (May 2024):** scraping is "almost always" unlawful. Its strict view that a purely commercial interest can't be a legitimate interest was rejected by the CJEU in *KNLTB* (C-621/22, 4 Oct 2024). The AP is still the strictest regulator to plan for. 🟢
- **What this means for the build:** for layer 3 only, **break data rule 4 on purpose**. Don't store raw HTML. Parse in memory, keep only price, mileage, first-registration year and seller type (private/dealer), then discard. Log the URL template and count, not the page. 🟡

## 5. Country notes

| Country | Database right | TDM exception | Notes | Risk |
|---|---|---|---|---|
| FR | CPI L.341-1 ff. | CPI L.122-5-3 / L.342-3 | leboncoin litigates and wins; La Centrale; also *parasitisme* (unfair free-riding) claims | 🔴 high |
| DE | UrhG §87a ff. | UrhG §44b | BGH 2014 is scraper-friendly on unfair competition; mobile.de offers a partner Search-API, so a judge may ask why we didn't use it | 🟡 medium |
| NL | Databankenwet | Auteurswet / Databankenwet (DSM transposed) | Amsterdam 2024 strict on what counts as an opt-out; AP strict on GDPR; AutoScout24 now owns AutoTrack and Gaspedaal | 🟡 medium |
| UK | CRDR 1997, still in force | CDPA s29A, **non-commercial only**; reform still under review in 2026 | No TDM shelter for us | 🔴 high |

## 6. Questions for an EU internet/IP lawyer

1. Does daily sampling of one results page per pre-filled search, kept only as counts and quartiles, amount to repeated, systematic extraction of insubstantial parts under art. 7(5), across our whole query set?
2. Under *CV-Online*, how would a court weigh a site's own paid price-analytics products against our free aggregates, and does linking out (sending traffic) help?
3. Is a published price band a "re-utilisation" of the database, or only our own derived information?
4. What exactly is a valid art. 4(3) opt-out in FR, DE and NL today: robots.txt `*`, ToS text, TDMRep? Given Amsterdam 2024, Hamburg 2025 and Eastern High Court 2026, which test would each country's courts apply?
5. Does a ToS scraping ban bind a visitor who never logs in or clicks "accept", in FR, DE and NL?
6. Does "stop at any barrier" (403, 429, CAPTCHA) keep us clear of computer-misuse offences, or can a plain robots.txt or ToS ban count as revoking authorisation?
7. Is in-memory parsing with immediate discard of seller fields enough under GDPR (art. 6(1)(f), arts. 13/14 transparency, art. 14(5)(b) exemption)? Do we need a DPIA or legitimate interest assessment?
8. Does a Dutch sole trader living in France, with servers in Germany, face jurisdiction and applicable-law questions (e.g. French courts for French sites)? Which law governs a claim by a German marketplace?
9. What is our realistic exposure if a marketplace objects and we stop the same day: injunction only, or damages for past sampling? Would a published kill-switch policy reduce it?
10. Is layer 2 (staff noting about 20 prices per generation each month) clearly fine, and can staff use a browser extension to speed it up without becoming "automated"?
11. Can we show marketplaces' published price indices (layer 0) as figures with attribution, and are there licence limits?
12. UK: with no commercial TDM exception, is any form of layer 3 for AutoTrader UK workable, or is it partnership-or-nothing?

## 7. Cost of a written opinion

| Basis | Figure | Conf. |
|---|---|---|
| Dutch independent lawyers, average 2026 | €241/h ex VAT (Knab ZZP rate guide 2026) | 🟢 one source |
| German commercial-law firms | €280–600/h net; boutiques up to €1,000 (Rose & Partner) | 🟡 |
| French lawyers, general consultation | €50–300/h (Coover; not IP-specific) | 🟡 |
| **Estimate: one EU-level memo on questions 1–7 plus one country (FR or DE), 6–12 h** | **€1,500–4,000 ex VAT** | 🔴 estimate |
| Estimate: four countries with local checks (FR, DE, NL, UK) | €4,000–10,000 | 🔴 estimate |

The spec's €500–1,500 is probably too low for a written opinion. It does fit a fixed-fee 1–2 h call on a pre-written question list. Cheapest path: send this brief plus the questions and ask for a fixed fee for a short memo. 🟡

## 8. Recommended default until the opinion

- **Layer 3 off** in code and config: every site's kill switch defaults to `off`, and switching it on needs a DECISIONS entry naming the lawyer's opinion. 🟢
- **Ship layers 0–2:** layer 0 country trend lines from published indices; layer 1 feeds where partners agree; layer 2 manual samples for the top generations; plus Stage A smart links everywhere.
- **Push partnerships** (Autonex, Adevinta, Vend, OLX Group) in Phase 1, as the marketplaces spec says. A "no" or no answer is the trigger to book the lawyer, not to switch layer 3 on.
- **If layer 3 is ever switched on:** build the TDM opt-out check (robots.txt, TDMRep, ToS flag in config) into the fetcher, parse without storing, follow the red lines in §2, and keep sampling targets out of the public repo (Decision 004).

## Sources (opened 2026-11-15)

- Clifford Chance, *CV-Online Latvia v Melons* (C-762/19) summary: https://cliffordchance.com/expertise/services/intellectual-property/global-ip-updates/2021/q4/cv-online-latvia-v-melons.html
- Pinsent Masons, *Ryanair v PR Aviation* (C-30/14): https://www.pinsentmasons.com/out-law/news/website-operators-can-prohibit-screen-scraping-of-unprotected-data-via-terms-and-conditions-says-eu-court-in-ryanair-case
- CMS Francis Lefebvre, leboncoin v Entreparticuliers (Paris CA, 2 Feb 2021): https://cms.law/en/fra/news-information/arret-leboncoin-web-scraping-droit-sui-generis-sur-les-bases-de-donnees
- MySweetImmo, leboncoin v Jinka (TJ Nanterre, 31 May 2024): https://www.mysweetimmo.com/2024/06/06/immobilier-jinka-condamnee-pour-extraction-et-reutilisation-illicites-dannonces-immobilieres-du-site-leboncoin/
- EUR-Lex, Directive (EU) 2019/790, arts. 2 and 4: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L0790
- IPKat, DPG Media v HowardsHome (Amsterdam, ECLI:NL:RBAMS:2024:6563): https://ipkitten.blogspot.com/2025/02/dutch-court-holds-that-tdm-opt-out-must.html
- Hogan Lovells AI case tracker, BoligPortal v ReData (Eastern High Court, 12 May 2026): https://digital-client-solutions.hlc.com/resources/ai-litigation-case-law-tracker/case/boligportal-a-s-v-redata-a-s/decision/74
- Kneschke v LAION appeal, 10 Dec 2025 (search result, not opened in full): https://www.technologyslegaledge.com/2025/12/robert-kneschke-v-laion-judgment-of-10-december-2025-ref-5-u-104-24/
- Kanzlei Plutte, BGH I ZR 224/12: https://www.ra-plutte.de/bgh-zum-automatisierten-auslesen-fremder-websites-via-screen-scraping/
- CNIL, legitimate interest and web scraping (19 Jun 2025): https://www.cnil.fr/fr/focus-interet-legitime-collecte-par-moissonnage
- IAPP, Dutch AP scraping guidance: https://iapp.org/news/a/netherlands-dpa-issues-guidance-against-web-scraping
- Hogan Lovells, CJEU *KNLTB* C-621/22: https://www.hlc.com/en/publications/cjeu-clears-the-air-dutch-dpas-interpretation-of-legitimate-interests-is-too-strict
- DLA Piper, UK TDM and s29A (Jan 2026): https://www.dlapiper.com/en/insights/blogs/mse-today/2026/tdm-and-training-ai-models
- Knab, Dutch lawyer rates 2026: https://bieb.knab.nl/wat-verdient-een-advocaat-zzp-bekijk-uurtarief-en-winst
- Rose & Partner, German lawyer hourly rates: https://www.rosepartner.de/stundensatz-anwalt-kanzlei-zeithonorar.html
- Coover, French lawyer fees: https://www.coover.fr/?p=79588

## Added 15 Nov 2026: finance and lease display (Decision 017)
Extra questions for the lawyer:
1. Does a neutral loan calculator (no lender named, no commission, typical APR from public sources) count as credit advertising under CCD2 as transposed in NL, DE, FR and BE? If yes, which representative-example items must it show?
2. In the UK, does a plain unpaid link to a used-lease or car-finance site count as credit broking (FCA), and is there a safe way to show lease prices from a partner feed?
3. For NL private lease (Keurmerk Private Lease, BKR), may we show a partner's "from €X/month" figure, and what must accompany it?
