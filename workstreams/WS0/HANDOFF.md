# WS0 handoff (2026-11-17 21:15 UTC, A-35 fixes chat — mission done)

Repo renamed by Menno to **zkMenno/EV-Shortlist** (use it for add_repo and every `gh api repos/zkMenno/EV-Shortlist/...`; the old name fails through the proxy). Project instructions, AGENTS.md (#92) and process docs/START prompts (#93) updated.

Mission: fix QA A-35 launch blockers. Done = release 2 published (`latest` = 2, diff vs 1), hero walk passes on it, Model Y passes the plausibility gate, /de/de /fr/fr /es/es /it/it show no English UI, CI green, A-35 findings marked fixed in task `## Review` lines. Then hand Menno a prompt for QA launch review 2.

## Merged today
#58 #62 #63 #64 #65 #66 #67 #68 #69 #70 #71 #72 #73 #74 #75 #76 #77 #78 #79 #80 #81 #82 #83 #84 #86 #87 #92 #93. Decisions 069 (generation band stands in), 080 (Autotijd held, Menno).
Default taken: a reviewed PR whose files don't overlap with what landed on main since its green CI may merge without another CI run; overlap → merge main in + CI.

## Release 2 state
**Published 2026-11-17 21:00 UTC**: PR #91 merged (round-2 fresh review pass on 42bb9d8), data-publish green, `data/releases/latest` = 2, GitHub Release data-v2 (151 assets). Release diff vs 1: 0 blocking, 249 approved. Hero walk on release 2: NL €35k 10/10 cards priced, 8/10 winter range; €15k one priced pick + unpriced list (cheaper cars fail road-tripper presets); DE/FR/ES/IT no English (e2e). A-35 B1–B5 + S7 marked fixed in T-110–T-119 `## Review` lines.
Fix PRs merged after the first release-2 review: #95 #96 #97 #99 #100 #101 #102 #103.

## Next
QA launch review 2 in a fresh chat (prompt in WS0 INBOX / given to Menno); QA INBOX has the scope. WS0 then triages A-36.

## Follow-ups noted
- FR loan.warning wording per country (Q-072, Menno). IT CCD2: cite the Official Journal.
- EV6 GT own TGK versions don't attach (consumption 24.2, +43 %): task + estimate label.
- Approvals check id/field/type, not values: diff each release PR's release_diff.csv against its approvals' source CSV.
- cite_paths should be required on every non-manual source (replace SHARED_HOSTS deny-list).
- CI ranking e2e skips without a scores file → release-like fixture step.
- Car pages: some data labels English on non-English pages; `{country}` own-language names.
- maker-docs: 11 seed citations are third-party copies (WS3 source_id). Test that used-price sources never include autotijd.
- #59 staging runbook waits WS4; #90 (infra reference-only) is another chat's.
- Ioniq 5 facelift base/awd rows carry pre-facelift figures (72.6 kWh, 507 km): WS3 adds facelift seed variants (RDW type-approval codes in #101).
- Model Y winter vs real range on different bases (EPA-based matrix vs WLTP × 0.78): design follow-up (WS1).
- eafo source: upstream 429 on 2026-11-17 refresh (previous data kept).
- €15k road-tripper list is thin on real data (one priced pick): product question for Menno/QA, not a bug.
