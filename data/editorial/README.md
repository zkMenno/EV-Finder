# data/editorial

Opinions, not facts. Owner: WS3. Decision 038.

| File | What | Edit by hand? |
|---|---|---|
| `menno-picks.yaml` | Menno's own EV analysis from his "New Car" sheet: verdicts, tiers, notes, era lists, July 2025 used-budget bands | No: re-run the importer |
| `import_menno_sheet.py` | Sheet (xlsx export) → `menno-picks.yaml`. Strips his postcode from marketplace links | Yes |
| `shortlist_rules.yaml` | Selection rules derived from the picks: gates, factor weights, bonuses, bands per profile | Yes (rules are rows) |
| `backtest_rules.py` | Scores the picks with the rules and checks agreement with his verdicts (CI, data-qa job) | Yes |

## Rules for this folder

- **Verdicts and notes are publishable** (Menno's own words, CC BY 4.0), shown as "Owner's pick" / owner notes, always labelled as one person's opinion.
- **`sheet_values` are internal only.** They were copied by hand from ev-database.org and Bjørn Nyland's 1000 km sheet. They calibrate the rules; they never reach a release, the app or the open data (AGENTS.md data rules 1-2). Production scoring reads our own published fields.
- **No location data.** The importer drops `dptCp` / `distance` from search links.
- A rule change must keep `backtest_rules.py` at or above 60% exact band match (CI fails below).

## Legend (how the sheet was read)

| Sheet signal | Stored as |
|---|---|
| Green row | `verdict: shortlist` |
| Yellow row | `verdict: consider` |
| Orange row | `verdict: fallback` (works, clearly behind the greens) |
| Grey text | `verdict: ruled_out` |
| No colour | `verdict: unrated` |
| Bold make/model | `favourite: true` |
| 😍 👍 👀 💸 | `flags: love / like / watching / expensive` |
| Tier 1.1–1.5 | `tier` (rank inside a group, lower is better) |

Re-import: download the sheet as .xlsx, then `python3 -I data/editorial/import_menno_sheet.py "New Car.xlsx"`.
