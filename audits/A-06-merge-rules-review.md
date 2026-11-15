# A-06 Merge rules review: Decisions 025–030 and how they interact

**Type:** data quality + rule interaction review · **Date:** 2026-11-15 · **Auditor:** fresh reviewer agent, branch `proto/overnight-1` (read-only; no commits) · **Data:** release 1 (`data/releases/latest` = `1`, 244 rows)

**Scope:** work since A-05 (`60c296f`..`e44dda8`): Decisions 025–030 and their code in `match/matcher.py`, `match/seed.py`, `merge/merge.py`, `merge/policy.py`, `qa/value_guard.py`, `derive/links.py`, `release/build.py`, `net.py`, `data/field_sources.yaml`, plus the seed `cited:` values in `data/seed/variants.yaml`.

**Tests added:** `pipeline/tests/test_a06_review.py`: 5 `xfail(strict=True)` tests that reproduce F1 (2 tests), F2, F3 and F6. Each fails for the reason stated (checked with `--runxfail`). They turn into XPASS errors once fixed, so remove the marker in the same commit as the fix.

## Check runs

| Check | Result |
|---|---|
| `uv run pytest -q` | 1147 passed, 5 xfailed (the new A-06 tests) |
| `uv run ruff check .` / `ruff format --check .` | pass |
| `python -m ev_pipeline.qa check-release ../data/releases/latest` | pass (provenance 5711 values, licence gate 13 sources / 40116 facts) |
| `ev release` twice, on a copy of `data/` in /tmp (releases 2 and 3) | identical apart from the release number, `previous_release`/"vs release N" text and the gzip byte count. Parquet differs only by the embedded release column. `data/review/*` byte-identical. Committed release 1 = the rebuild, so release 1 matches the current code. |
| WebFetch of the cited URLs | **not done**: the first fetch got no answer to its permission prompt, so I made no other network calls. The cited values were checked against common knowledge instead (see "Verified clean"). Re-run this check with web access. |

## How the rules are applied (order)

1. Matcher: battery gate (027) rules out candidates, then nameless records need evidence (025) → placement.
2. `guard_usable_vs_pack` (T-057) drops usable kWh above a linked pack's gross.
3. `merge_facts` per field: one vote per SPREAD_SOURCES source → mode (priority / median / default majority / newest) → `agreement` (025; priority mode only) → `cited` (028; all modes but `newest`).
4. `guard_mixups` (029) → `guard_needs_backing` (025) → `guard_impossible` (A-05 F7). Each removes facts and merges the field again, but **no guard runs again after a later guard changes a value**.
5. Corroboration, then rule pack/platform links (030) on the guarded `battery_kwh_net`.

## Findings

### Critical

None.

### High

**F1 · `needs_backing` deletes the whole field, not just the unbacked value.** `guard_needs_backing` (`qa/value_guard.py:120`) checks only the merged *winner*. If the winner's sources are all `kilowatt-openev`, it deletes the field and sends **every** fact for that field to review, including values that are backed or come from other sources. It never merges the field again without the weak facts (the other two guards do).
- *Scenario seen in release 1:* Audi Q4 40: KilowattApp 143 (earliest year, wins) and 125, seed 125. The 125 group meets the rule's own bar (seed agreement counts as backing, per the QUESTIONS.md default), but the row ships with **no DC peak**.
- *Non-monotone:* 16 variants lose a seed DC peak that would have shipped (single, low) if KilowattApp had no record. Examples: Nissan Leaf ZE0 24/30, Leaf ZE1 40, Kia EV6 77 AWD and GT, Mercedes EQC 400, VW ID.3 Pro, e-Golf, Model S P100D, Zoe Ph2 R110/R135. Adding a source *removes* data.
- *Latent:* a lone KilowattApp value outranks `maker-docs` and `seed-manual` for `dc_peak_kw`, so once maker-docs facts are released, a real maker figure would be withheld with it.
- *Fix:* drop only the facts whose group is backed solely by `needs_backing` sources, then merge again (as `guard_mixups` does). Tests: `test_needs_backing_keeps_a_backed_value_when_the_winner_is_unbacked`, `test_needs_backing_does_not_drop_another_sources_value`.

**F2 · `guard_impossible` can undo a `cited` win, so the overruled lone value comes back.** The impossible-pair guard drops the half with the lower `independent_agreeing`. A cited seed fact counts 0 (seed-manual is never independent), so a value that won by rule `cited` always loses to any single uncited source on the other half.
- *Scenario:* OpenEV gives usable 82 and gross 85. Ford's cited usable is 88, so rule `cited` publishes 88. Then 88 > 85, so the guard drops the cited 88, merges again, and OpenEV's 82 (the value Decision 028 overruled) ships with no review flag on 82. The same happens with `wltp_efficiency` (cited usable vs a lone wrong-trim WLTP).
- *In release 1:* not triggered (Mach-E cited gross values sit next to the cited net values). Any new `cited:` net without a cited gross is exposed.
- *Fix:* in `guard_impossible`, count a cited half as at least 1 (or prefer it), or drop the uncited half when only one side is cited. Test: `test_impossible_guard_does_not_undo_a_cited_win`.

**F3 · Seed `cited:` values ship under the seed's CC BY licence, and the citation URL is dropped.** `parse_cited` (`match/seed.py:337`) copies the seed source and changes only `url` and `name`. The id stays `seed-manual`, licence `CC-BY-4.0`, owner "EV Finder". Two problems:
- (a) *Traceability:* `_flat_facts` (`release/build.py:710`) does not write `source.url`, and `sources.json` / `ATTRIBUTION.md` list only the generic seed. The URL, the only real evidence for a cited value, appears **nowhere in release 1** (grep for fordpers/press.renault/newsroom.bmwgroup: 0 hits; facts.parquet has 15 cited facts with name only). The attribution text says seed-manual values are "hand-entered and unchecked", which is wrong for these 15.
- (b) *Licence gate:* the same kind of fact from a maker document is `blocked` when it comes through `maker-docs` or `manual` until Q-008 is answered ("Can cited single facts from maker documents count as releasable? ... EU database right may apply"). `bidi_equipment` is held back for exactly this reason. Seed `cited:` routes maker-document facts (Ford, Renault and BMW press PDFs, three of them third-party copies: rinnovabili.it, xr793.com, projekt-renault.de) around that gate into the CC BY release.
- *Scenario:* a reuser of `facts.parquet` sees "Mach-E GT usable 88 kWh, seed-manual, CC-BY-4.0, EV Finder" with no URL. If Menno answers Q-008 "no", these values have already shipped.
- *Fix:* (a) write `source_url` in facts.parquet (and the row provenance). (b) Either give cited seed values their own source id that follows `maker-docs`' gate, or record in DECISIONS.md that Decision 026 deliberately answers Q-008 for single cited facts, and ask Menno. Test for (a): `test_published_facts_keep_the_citation_url`. (b) is a policy question, so no test.

### Medium

**F4 · `needs_backing` counts unchecked seed values as backing.** `set(mg.source_ids) <= set(weak)` treats any seed-manual agreement as backing. That goes against Q-015 / merge.py ("seed-manual never counts as an independent confirmation"). It was disclosed as a default in QUESTIONS.md, but it was never logged in DECISIONS.md 025.
- *Release 1:* 42 of 211 DC peaks rest on KilowattApp + uncited seed only (e.g. Mach-E ER AWD 148, Cupra Born 58 124, EQA 250 99), published at `medium`.
- *Scenario:* a seed value typed from memory, possibly from the same upstream as KilowattApp, "confirms" a KilowattApp error like the Zoe R110 150 kW, and it ships.
- *Fix:* count only cited seed facts as backing, or log the exception in DECISIONS.md.

**F5 · Known-wrong KilowattApp `ac_kw` still ships at medium confidence.** The Zoe Ph1 **Q210 shows 11 kW** (Renault: 43 kW; the cited 43 is `low`, so it can't win). The **R90 shows 11 kW** over the seed's 22 (R-motor Zoes charge at up to 22 kW). Decision 028 parks this, but Decision 028's consequence line "No cited value loses anywhere in the release" is not true: the Q210 citation loses (conflicts.csv `cf-256b8af817`, seed-manual 43 vs 11). That is a bad value for anyone filtering on "fast AC".
- *Fix:* a confirmed Phase 1 spec sheet (the Q210 one is already cited, so raise it to medium if the page names the exact version), or `needs_backing: [kilowatt-openev]` on `ac_kw`.

**F6 · `manual` facts count as independent confirmation.** `NOT_INDEPENDENT` holds only seed-manual and model-estimate. A `manual` fact (cited by definition) counts as a second origin in `agreement`, in `confidence = high` and in `_cited_over` backing. That contradicts merge.py ("A cited fact still never counts as an independent confirmation").
- *Latent:* `manual` is blocked today.
- *Scenario:* once Q-008 opens it, OpenEV + one manual fact would outvote a priority source and show `high`. Test: `test_a_manual_citation_is_not_an_independent_confirmation`.

**F7 · Citation scope wider than the variant.** `bmw-i3-i01-i3s` covers "94 Ah / 120 Ah" (2017–2022) but cites the 120 Ah press release (42.2 kWh gross). The row shows 37.9 kWh usable (120 Ah), so 2017–18 i3s cars (94 Ah, 27.2 / 33.2 kWh) get the wrong battery. The cited gross also becomes a battery-gate anchor, so 94 Ah i3s records can't land anywhere (unmatched.csv: "several variants fit 120ah, 94ah").
- *Fix (seed lane):* split the i3s by battery, or limit the citation's `years`.

**F8 · OpenEV vs KilowattApp vs fueleconomy independence is unverified.** Both "Open EV Data" datasets count as separate origins for `agreement` and for "high" confidence. OpenEV's own files cite fueleconomy.gov 25 times, but SAME_ORIGIN maps only `rdw-tgk → rdw`.
- *Scenario:* if one dataset copied the other (or EPA), "2 independent sources agree" is one source counted twice. `agreement` can then outvote a priority source, and `cited` can lose to a copy (`_cited_over` returns None at 2 origins). 🔴 unsure: I could not check either project's upstream (web blocked).
- *Fix:* a research note on each dataset's upstream, then SAME_ORIGIN entries (per field if needed, e.g. openev→fueleconomy for `epa_range_km`).

### Low

- **L1 · Guards don't re-check each other.** `guard_mixups` compares `ac_kw` with battery values *before* `guard_impossible` may replace them. An `ac_kw` fact can be dropped as a "mix-up" with a battery value that is later found wrong. Equally, a new battery value from the impossible guard is never checked for mix-ups. Rare. A fixed-point loop over the three guards would close it.
- **L2 · Mix-up guard ignores pack-inherited battery values.** It compares only merged battery fields, so a row whose battery comes only from `variant_links.yaml` gets no mix-up check.
- **L3 · Platform rule is unanimity over possibly one link.** In `apply_rule_links`, a generation with a single linked variant hands that platform to every row of the generation. That's fine today (no generation spans two platforms), but worth a minimum of 2 links or a reviewer flag.
- **L4 · Git URL gate:** good (fail closed, `--`, https-only protocol flags). Git still reads the user's/system gitconfig (`url.<x>.insteadOf` could rewrite the URL after the check). Consider `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=/dev/null` in the subprocess env.
- **L5 · Taxonomy names blocked source `eafo`.** `catalogue.json` has power-band and definition entries with `source_id: eafo` (labels only, no values). That's harmless, but `section_gate_errors` / `excluded_source_errors` don't flag it, so a future value would need an explicit check.

## 15-row spot check (seeded random sample, release 1)

Plausible: Enyaq 80x, ID.3 Pro 2023 (except DC), Ioniq Electric 38, EQA 250 (2021), iX xDrive50, ID.4 Pro, Cupra Born 58, BYD Atto 3, EQB 300 4MATIC (except kWh).

Implausible (all single-source OpenEV values at `medium`):

| Row | Published | Why it looks wrong |
|---|---|---|
| `audi-q4-e-tron-gen1-50` (2023–25) | rwd, 150 kW, 0–100 8.5 s, 73 kWh; WLTP 464 from **RDW 2021–22 "Q4 50 E-TRON" year groups** | The Q4 50 is quattro (220 kW, about 6.2 s). OpenEV's own `2024/q4_e_tron_50.json` carries 40-trim figures. The WLTP comes from earlier quattro year-group records placed on a 2023+ RWD row (rdw wins by priority over OpenEV 520, since one origin can't outvote it). `-50-sportback` has the same problem. |
| `renault-megane-e-tech-gen1-40-kwh` | DC 130 kW | The EV40 does 85 kW. 130 kW is the EV60. |
| `renault-5-e-tech-gen1-40-kwh` | DC 100 kW | The 40 kWh R5 does 80 kW. 100 kW is the 52 kWh. |
| `volkswagen-id3-gen1-pro-2023` | DC 135 kW | The 58 kWh Pro does 120 kW. |
| `mercedes-eqb-gen1-300-4matic`, `-base`, `eqa-h243-base` (2023–25) | 60 kWh usable | The EQA/EQB 250+/300 use 66.5 kWh, and the facelift 70.5 kWh. |
| `hyundai-ioniq-6-gen1-long-range` | 72.6 kWh | 77.4 kWh pack, usable about 74. Minor. |
| also seen: `audi-q4-e-tron-gen1-40-sportback` | 48 kWh | The Q4 40 is 77 kWh. This is the OpenEV record Decision 027 pushed off the 40 e-tron row; it now has its own row. |
| also seen: `renault-zoe-ph1-q210/-r240` | usable 23.3 kWh | Decision 029 itself calls 23.3 the Z.E. 22 *gross* figure. Either the decision or the published usable value is wrong (seed says 22). 🟡 |

These are source errors, not rule bugs. But all of them get past every guard because one OpenEV record per row "agrees with itself" (2023/2024/2025 files are one origin). Suggestion: a DC-peak-per-kWh outlier check within a generation (siblings with the same pack and platform but a different DC peak), and the generation-level year check for year-group records (RDW 2021–22 on a 2023+ row).

## Verified clean

- **Rule order inside `merge_facts`:** `agreement` only in priority mode, `cited` after it. Two agreeing origins beat a citation, disagreeing citations win nothing, `newest` is exempt, and `cited_wins` / `agreement_wins` opt-outs parse. No path leaves a field with zero candidates inside `merge_facts`. Field deletion happens only in the guards (F1, and the impossible guard when nothing is left, by design).
- **SPREAD_SOURCES + SAME_ORIGIN:** rdw-tgk votes once, and its followers back `fact_ids` but not confidence (A-05 F6 fix holds).
- **Mix-up guard:** cases in `fixtures/value_guard/ac_mixups.yaml` behave as documented. Re-merges without the bad facts. Cited or cross-origin agreement protects a value. Zoe R240 → 22 (seed), R110 → 22, Q90 → 43, e-Golf 36 → 7.2 verified in the release.
- **Battery gate:** Zoe R90 41 kWh, Q4 40 e-tron 77 kWh, Mach-E ER AWD 88 kWh as Decision 027 says. The gate only rules out (no next-nearest push) per `test_battery_gate.py`.
- **Cited values vs common knowledge** (web check not possible): Zoe Q210 43 kW AC, R240 22 kW, Q90 43 kW, Z.E. 40 41 kWh usable, R110 22 kW, i3 120 Ah 42.2 kWh gross, Mach-E SR 68 / 75.7 kWh, ER 88 / 98.7 kWh. All match the published maker figures I know, and every entry has a URL, date and quote or locator. No fake-looking citation was found, but the URLs themselves are **not** verified.
- **Licence gate:** check-release passes. Release sources are ademe, bnetza, dft-charging, dft-veh, eea, fueleconomy, kba-fz10, kilowatt-openev, model-estimate, openev, rdw, rdw-defects, rdw-tgk, seed-manual, wikidata. **No Nyland or EAFO data**: 0 hits in variants.csv/json, sources.json, charging_stats.json and facts.parquet. EAFO appears only as taxonomy labels (L5). Nyland raw stays in git-ignored `data/local/`.
- **Decision 030 links:** rule links carry their rule and gap in provenance (72 rows). The pack fit uses guarded usable kWh and never goes above gross. Spot check: Q8 50 → 95 kWh pack (89 usable) is right.
- **Idempotence:** see check runs. Deterministic, and release 1 is reproducible from the committed code + staging.

## Suggested tasks

1. Pipeline: F1 (re-merge in `guard_needs_backing`) + F2 (cited half in `guard_impossible`). Both are small, with tests ready.
2. Pipeline + coordinator: F3 (a) write `source_url` to facts.parquet and provenance; (b) DECISIONS entry or a separate gated source id for cited seed values, linked to Q-008.
3. Coordinator: log F4's exception, or tighten it. Decide F5 (`needs_backing` on `ac_kw`?).
4. Research: OpenEV / KilowattApp upstream and independence (F8).
5. Seed lane: split the i3s by battery (F7). Check the OpenEV-only rows in the spot-check table.
