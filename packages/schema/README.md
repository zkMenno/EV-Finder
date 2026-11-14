# @ev/schema

`schemas/ev.schema.json` is the single source of truth for every catalogue entity
(Make → Model → Generation → Variant → MarketVariant → Fact → PublishedVariant).

- `pnpm --filter @ev/schema gen` regenerates `generated/ts/index.ts` and
  `generated/python/ev_schema.py` (copied to `pipeline/ev_pipeline/schema_models.py`).
- `pnpm --filter @ev/schema test` checks every file in `fixtures/` (`*.valid.json` must pass,
  `*.invalid.json` must fail).
- Only the coordinator edits this package (AGENTS.md).
