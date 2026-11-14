# AGENTS.md — packages/schema

- Coordinator-only lane. Builders read it; they never edit it.
- Edit `schemas/ev.schema.json`, then run `pnpm --filter @ev/schema gen` and commit the generated files.
- Never hand-edit `generated/` or `pipeline/ev_pipeline/schema_models.py`.
- Every change needs a fixture: `fixtures/<entity-kebab>.valid.json` or `.invalid.json`.
- Stable ids (`Id`) never change once published; slugs may.
