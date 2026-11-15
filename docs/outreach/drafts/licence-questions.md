---
status: draft
owner: WS5 (drafted by WS0, 2026-11-15)
sender: Menno
note: Factual licence questions, not outreach. Menno sends them himself. We already use the data meanwhile (Decision 037); if either answer is "no", we remove that source in the next release.
---

# Licence questions: EAFO, RDW, ABRP (drafts for Menno)

Three short emails. Fill in your surname and reply-to address, then send. Each has where to send it and what to do with the answer.

---

## 1. EAFO (European Alternative Fuels Observatory) — English

**Send via:** the contact form or contact address on https://alternative-fuels-observatory.ec.europa.eu/ (footer → Contact). 🔴 I didn't verify a direct email address, so use what the site shows.

**Subject:** Reuse of EAFO charging-point statistics under CC BY 4.0

> Hello,
>
> I'm building EV Shortlist (working title), a free, independent guide to used electric cars in the Netherlands, Germany, France, Belgium and the UK. One page per country shows how public charging has grown, so first-time buyers see today's network rather than the 2019 one.
>
> We'd like to use EAFO's published country totals of public recharging points (by power band, monthly) and show them as charts, credited as "Source: European Alternative Fuels Observatory (European Commission), [date]". We only use the aggregate figures, never individual charging locations. Our derived figures are published as open data under CC BY 4.0.
>
> The Commission's legal notice puts EU-owned content under CC BY 4.0, and your FAQ says the underlying data comes from Eco-Movement. Could you confirm that reusing the published EAFO aggregates this way is fine, or tell us what conditions apply?
>
> Thank you,
> Menno [surname]
> [reply-to email]

**If yes:** WS1 sets EAFO to `active` (confirmed) in `data/sources.yaml`. **If no or conditions:** WS1 drops EAFO from public releases; Belgium falls back to the IEA series.

---

## 2. RDW (Dutch vehicle authority) — Nederlands

**Send via:** the RDW open-data contact listed on https://www.rdw.nl/over-rdw/dienstverlening/open-data/bijsluiter or https://opendata.rdw.nl. 🔴 Check the address on the page; I didn't verify it.

**Onderwerp:** Bronvermelding bij hergebruik van RDW open data (CC0)

> Beste RDW open-data team,
>
> Ik bouw EV Shortlist (werktitel), een gratis, onafhankelijke gids voor tweedehands elektrische auto's. We gebruiken RDW open data (CC0) om per model te tellen hoeveel auto's er rijden, welke uitvoeringen er zijn en welke gebreken bij de APK vaak voorkomen. We tonen alleen totalen, nooit gegevens van één auto of kenteken.
>
> In de bijsluiter staat dat je bij hergebruik niet mag vermelden dat de gegevens van de RDW komen. Wij laten bij elk getal de bron zien, zodat bezoekers het kunnen controleren. Mogen we de dataset noemen en ernaar linken, bijvoorbeeld "Bron: open data RDW (opendata.rdw.nl), CC0", zonder logo of huisstijl? Of hebben jullie een voorkeursformulering?
>
> Alvast bedankt,
> Menno [achternaam]
> [antwoordadres]

**If they allow naming:** show "Bron: open data RDW, CC0" with a link (closes Q-037). **If not:** label it "Dutch open vehicle register (CC0)" with a link to the dataset, no RDW name or logo.

---

## 3. ABRP (Iternio) — English

**Send to:** contact@iternio.com 🟢 (from ABRP's own API docs, research R-24)

**Subject:** Car-model list for deep links from a used-EV guide

> Hello,
>
> I'm building EV Shortlist (working title), a free, independent guide to used electric cars in Europe. On each car page we'd like a "Plan this trip in ABRP" link that opens ABRP with the right car selected, using your `car_model` deep-link parameter. The link text will always name ABRP, as your docs ask.
>
> To pick the right typecode for each variant we need your car-model list. The `get_carmodels_list` endpoint asked for a key when we tried it. Could you give us access (or a telemetry/planning key) for the model list and the vehicle library, so we can keep typecodes and replacements up to date?
>
> Thanks,
> Menno [surname]
> [reply-to email]

**If yes:** WS1 adds an ABRP typecode sync (key in server env only, never in the repo); WS3 fills `abrp_typecode` for the top 40 (T-029).

---

## Accounts for you to create (Q-093, both free)

1. **Copernicus Climate Data Store (CDS):** sign up at https://cds.climate.copernicus.eu → accept the CC BY 4.0 licence for "ERA5-Land monthly means" and "ERA5-Land daily statistics" → copy your API key from your profile. Give it to WS4 for the server env file (never paste it in a chat that writes to the repo).
2. **ABRP:** sign up at https://abetterrouteplanner.com → account settings → create a free telemetry API key. Same: key goes to WS4 for the server env.
