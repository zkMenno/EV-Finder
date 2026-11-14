# data/seed

`models.yaml` is the hand-curated seed list of used-EV favourites (Make → Model → Generation, schema `seed-models/v1`), with year spans, mid-generation change markers and `name_aliases` for matching source records.
Validate it with `python3 -I data/seed/validate_seed.py data/seed/models.yaml` (needs PyYAML); `--self-test` checks the validator itself against small inline fixtures.
It was written from model knowledge only, without fetching sources, so no value here is traceable yet: treat it as a seed for matching, not as published data.
Every generation with `uncertain: true` must be hand-checked against a primary source (manufacturer or registration data) before it is relied on; its `notes` field says what is in doubt.
