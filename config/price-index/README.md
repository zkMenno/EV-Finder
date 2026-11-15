# Country price indices (price layer 0): placeholder

Structure only. No values, no source and no method yet, and nothing in the UI reads it.

Layer 0 is meant to hold one index value per country and year, so price figures from different
countries and years can later be put on a common footing. Until a source and a method are decided
(and logged in `DECISIONS.md`), every value stays `null`.

- Typed structure: `apps/web/src/lib/price-index.ts` (`PRICE_INDEX`: country → year → value, all `null`).
- Countries: the five site countries (`NL`, `DE`, `FR`, `BE`, `UK`).
- When values arrive they follow the data rules in `AGENTS.md`: each value gets a source, a retrieval
  date, a confidence and the source's licence, and it comes through the pipeline release, not
  hand-edited into the web app.

Open points for the coordinator: which index (and from whom), base year, how often it updates,
and whether it lives in the catalogue release or a separate file here.
