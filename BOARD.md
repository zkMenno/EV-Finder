# Board

One screen: what's happening. Coordinator only. Task details live in `tasks/`.

_Last updated: 2026-11-17 09:30 UTC by WS0. Every task in "review" whose work is on `main` is now marked **merged**; its fresh review comes from QA (audits/A-35, PR #46)._

## Launch scope (Decision 051, docs/spec/launch-scope.md)

Builders take only tasks in **Launch**. Everything else needs Menno's yes. Built work for parked features stays behind feature flags (off).

**Launch fixes from QA A-35 (blockers, do first):** T-110 Model Y + seed figures (WS3) · T-111 plausibility + licence gates (WS1) · T-112 new list prices (WS3) · T-113 depreciation estimate (WS1) · T-114 hero reads release scores (WS2) · T-115 budget rule (WS2) · T-116 release 2 (WS1, after T-110–T-113) · T-117 DE/FR/ES/IT strings (WS2 + WS3) · T-118 Spain + Italy data (WS3 + WS1) · T-119 /es/es + /it/it (WS2). Decisions 064–066.

**Launch, hero:** T-080 hero shortlist (WS2) · T-067 profile picker + suggested sort (WS2) · T-066 schema shortlist rules (WS0) · T-069 shortlist scores in the release (WS1) · T-068 seed gaps for picks (WS3) · T-081 used price by build year (WS1 + WS3) · T-056 free price indices (WS1) · T-043 loan estimate only (WS2/WS3)
**Launch, catalogue:** T-010 compare · T-045 differences only · T-050 country + language URLs · T-012 i18n · T-051 / T-052 seed coverage · T-041 listing templates · T-062 / T-063 data fixes · T-065 schema follow-ups
**Launch, data:** T-064 releases out of git · T-034 climate · T-032 / T-033 consumption model (winter range) · T-035 back-test · T-031 heat pump seed · open data download (built, Decision 016)
**Launch, content:** T-039 winter range · T-027 charging in 2026 · T-082 batteries + battery health · glossary tooltips
**Launch, infra:** T-040 AppInfra staging · T-013 deploy · T-064 storage part

**Process: verification layer (Decision 062):** Launch: T-120 REVIEW.md (WS0) · T-121 gate-guard (WS0, observe → enforce 24 Nov) · T-122 rule register (WS0) · T-123 release-diff test (WS1) · T-126 verify skill web (WS2) · T-127 verify skill pipeline (WS1) · T-128 Verified stamp + flaky policy + self-merge rule (WS0). Not launch-blocking: T-124 property tests pipeline (WS1) · T-125 property tests web (WS2) · T-129 reviewer eval set (parked, after launch).

**After launch (parked):** T-011 rankings pages · T-019 / T-020 / T-021 / T-022 bidirectional · T-024 / T-025 / T-026 / T-028 charging pages + link-outs (built parts stay flagged off) · T-029 ABRP deep links · T-036 quick range check (absorbed into T-080) · T-037 / T-038 Trip fit routes · T-042 bidi verification · T-044 / T-046–T-049 variant clues + finder · T-053 / T-058 registration history display · T-061 known issues · lease figures (rest of T-043)

## Now
**Open PRs, WS0 reviews and merges in this order:**
- #44 T-123 release diff N vs N-1 (WS1), then #51 T-127 `ev verify` + pipeline verify skill (WS1, builds on #44)
- #49 T-124 pipeline property tests + Decision 045 rung fix (WS1)
- #46 QA launch review 1 (audits/A-35: the fresh review of everything merged without one)
- #48 WS2 status + verify-report request (docs only)

**Chats:** WS1 handing off to a fresh chat · WS2 idle, waiting on WS1 data fields · WS3 paused since 15 Nov (HANDOFF.md) · UX next: differences-only highlight · QA running launch review 1 · WS4 + WS5 not opened yet.

## Next (launch scope only)
- **WS0:** T-128 `Verified:` stamp + flaky-test policy + self-merge rule · gate-guard to enforce on 2026-11-24 (with the review follow-ups listed in T-121) · forward Q-001/Q-070/Q-073 to WS4
- **WS1:** T-063 on-board charger field (**unblocked:** `ac_kw_optional` is in the schema) · winter range quality (START §3 item 6) · T-070 real range + DC km from the calibrated matrix · T-064 part 2 after the first published release
- **WS2:** T-097 hero Nerd table units · winter range on hero cards and T-045 deltas once WS1 ships the field · /learn/batteries links from hero cards
- **WS3:** T-051 seed coverage (with WS1 T-052 pre-2020 specs) · DE/FR/BE/UK price samples need a person (sites block agents)
- **WS4:** T-040 AppInfra staging → T-013 deploy. Nothing is deployed yet; this is the main launch gap.

## Blocked on Menno
- 7 questions in [QUESTIONS.md](QUESTIONS.md): Q-003 PRs on main · Q-008 maker documents · Q-028 listing URL patterns · Q-037 RDW wording · Q-047 KilowattApp curves (blocks EV3/Inster rows) · Q-072 CCD2 warning wording · Q-079 Actions opening data-release PRs
- T-041 listing templates: his tap check on a phone
- Opening the WS4 chat (staging) and the WS5 chat
- Real data in production waits for off-site backups (AppInfra #93). EV holds nothing to back up at launch; the trigger and the AppInfra handoff are in ROADMAP.md Phase 0, "Backups" (2026-11-17)

## Workstreams and file ownership

Workstreams talk through `workstreams/<ws>/INBOX.md`, never through Menno (Decision 014). Full table and rules: [docs/process/README.md](docs/process/README.md).

| Owner | Paths |
|---|---|
| WS0 coordinator | AGENTS.md, CLAUDE.md, BOARD.md, QUESTIONS.md, DECISIONS.md, ROADMAP.md, CHANGELOG.md, docs/spec/, packages/schema/, tasks/, research/, audits/, workstreams/README.md + */START.md, .github/ (not image workflows) |
| WS1 pipeline | pipeline/ (not Dockerfile), data/sources.yaml, data/field_sources.yaml, data/SOURCES.md, data/releases/, data/review/ |
| WS2 web | apps/web/ (not Dockerfile) |
| WS3 curation | data/seed/, data/manual/, data/taxonomy/, content/, config/ |
| WS4 infra | infra/, pipeline/Dockerfile, apps/web/Dockerfile, .github/workflows/image*.yml |
| WS5 growth | docs/outreach/, docs/growth/, docs/brand/ |
| UX design | docs/design/ |
| QA reviewer | audits/, `## Review` sections in tasks/ |
| each WS | its own workstreams/<ws>/STATUS.md and HANDOFF.md; INBOX.md files are append-only for everyone |

## Done
- 2026-11-17: verification layer live: REVIEW.md, gate-guard (observe), rule register G-01–G-33 (#42, #45); T-125 web property tests, T-126 web verify skill, hero a11y + phone fixes, T-096 compare labels (#47–#55); docs tidy + `_archive/` (Decision 063)
- 2026-11-17: batch merge of 10 waiting PRs (#39): T-069 shortlist scores, T-081/T-056 used price bands, T-091 parked flags, T-068 seed gaps, T-031 heat pump, T-041 templates, T-100 glossary, /learn pages (T-082, T-039, T-027), T-093, T-094, T-081 NL aggregates (#38)
- 2026-11-15: hero shortlist (T-080), suggested sort (T-067), differences only (T-045), open data page (T-090), schema for shortlist rules (T-066/T-065), climate (T-034), consumption model + back-test (T-032/T-033/T-035), charging stats (T-025), releases out of git part 1 (T-064)
- 2026-11-15: overnight prototype 1 (#1, waves 1–4 + T-053–T-061) and research pack (#2); spec mirrored to docs/spec; workstreams set up; GitHub repo, CI, templates, security settings
