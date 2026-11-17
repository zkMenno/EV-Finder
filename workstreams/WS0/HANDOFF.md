# WS0 handoff (2026-11-17 20:45 UTC, A-35 fixes chat)

Repo renamed by Menno to **zkMenno/EV-Shortlist** (use it for add_repo and every `gh api repos/zkMenno/EV-Shortlist/...`; the old name fails through the proxy). Project instructions, AGENTS.md (#92) and process docs/START prompts (#93) updated.

Mission: fix QA A-35 launch blockers. Done = release 2 published (`latest` = 2, diff vs 1), hero walk passes on it, Model Y passes the plausibility gate, /de/de /fr/fr /es/es /it/it show no English UI, CI green, A-35 findings marked fixed in task `## Review` lines. Then hand Menno a prompt for QA launch review 2.

## Merged today
#58 #62 #63 #64 #65 #66 #67 #68 #69 #70 #71 #72 #73 #74 #75 #76 #77 #78 #79 #80 #81 #82 #83 #84 #86 #87 #92 #93. Decisions 069 (generation band stands in), 080 (Autotijd held, Menno).
Default taken: a reviewed PR whose files don't overlap with what landed on main since its green CI may merge without another CI run; overlap → merge main in + CI.

## Release 2 state
Data refresh run 44152473152 on main passed QA and opened **#91 "Data release 2"** (226 → 271 variants, 0 blocking, 248 approved via #87). Fresh review: changes requested:
- CI red: web + pipeline jobs don't fetch release files (gate PR to ci.yml); pipeline tests: "Nyland" named in qa.json (backtest/epa.py note), plausibility-withheld rows (Atto 3, Kona SX2 ×2, Enyaq 85) still publish winter range/basis, RDW model registrations on 4 EV6 gen1 + 2 XPeng G6 rows.
- Ioniq 5 gen1 (awd/base/n) disappear; facelift ids carry gen1 figures → investigate, keep gen1.
- Model Y gen1 winter range 83 % of real range vs Ioniq 6 61 % → check.
- publish.yaml repo → EV-Shortlist.
- Hero NL €15k: 8 of 9 cards unpriced; Leaf e+/Zoe/e-208 priced under €15k missing → web fix (Decision 064: unpriced never top 5).
A-35 status on release 2 + main: B1 fixed (used prices 171/271, winter range 241/271, NL €35k 10/10 cards priced, 8/10 winter), B2 partial (€15k), B3 to re-check, B4 fixed (Model Y 533/586 km), B5 fixed (e2e 37/1).

Running now: WS1 subagent (fixes 1–7 above, one PR each); WS2 subagent (fix/hero-unpriced-never-top5 + B3 re-check).
Next: fresh reviews → merge → `gh workflow run data-refresh.yml --ref main -R zkMenno/EV-Shortlist` (replaces the unmerged release PR; may need extra approvals in config/approved_changes.yaml) → fresh review of the new release PR incl. hero walk → merge → data-publish → latest = 2 → A-35 `## Review` lines → QA review 2 prompt.

## Follow-ups noted
- FR loan.warning wording per country (Q-072, Menno). IT CCD2: cite the Official Journal.
- EV6 GT own TGK versions don't attach (consumption 24.2, +43 %): task + estimate label.
- Approvals check id/field/type, not values: diff each release PR's release_diff.csv against its approvals' source CSV.
- cite_paths should be required on every non-manual source (replace SHARED_HOSTS deny-list).
- CI ranking e2e skips without a scores file → release-like fixture step.
- Car pages: some data labels English on non-English pages; `{country}` own-language names.
- maker-docs: 11 seed citations are third-party copies (WS3 source_id). Test that used-price sources never include autotijd.
- #59 staging runbook waits WS4; #90 (infra reference-only) is another chat's.
