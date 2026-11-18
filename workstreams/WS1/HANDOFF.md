# WS1 handoff — 2026-11-18 ~09:40 UTC

Chat: https://claude.ai/code/session_01JuyZEVR92pcMFzUGsz5wzo (6th WS1 session). Next chat: "Read workstreams/WS1/HANDOFF.md and START.md and go."

## State (2026-11-18 09:40 UTC)
All merged: #105 (image build fix), #108 (T-136 report R-41), #109 (Pillow), #110 (T-134 photos, pipeline side). No open WS1 PRs.

## Next for WS1 (in order)
1. After the first night run since #110: check the refresh summary `images` (fetched / failed / stopped). Wikimedia 429s sandbox IPs, so the night server is the first real download. If it says `stopped`, it resumes next night.
2. Follow-up task to propose to WS0: a night with only new photos (no data change) is skipped as 'catalogue identical', so photos wait for the next data change.
3. Press photos: when WS3 marks a maker `allowed` in data/images/press-terms.yaml, copy its `photo_hosts` into `maker-press-photos.hosts` in data/sources.yaml and regenerate apps/web's sources.generated.json (`node apps/web/scripts/sources.mjs`).
4. T-136 build tasks: only those WS0 approved from R-41 (see BOARD/tasks).
5. Older open items from the 5th handoff still apply (#58 follow-up test for the ac_kw_optional rows guard; WS3 asks '+' → 'plus', `years:` on manual facts).

## Findings worth keeping
- EEA Discodata POST works from these sessions; 16 grouped queries take ~10 min (scripts in research/R-41-catalogue-coverage/).
- 9.11 M EU BEVs 2010–2025; seed models match 86.7 %; EEA power field is inconsistent across countries (do not use as a variant key alone).
- 22 KilowattApp rows cite ev-database.org (🔴 provenance).
- Local full pytest needs release 2 assets: `cd apps/web && CATALOGUE_FILES=catalogue.json,catalogue.parquet,facts.parquet,charging_stats.json,consumption_matrix.json,run_log.json,shortlist_scores.json,sources.json,used_prices.json,refresh.json node scripts/fetch-release.mjs`.
- Photo licences: Commons CC BY / CC BY-SA incl. 2.0–3.0 country ports (e.g. CC-BY-SA-3.0-DE); 4.0 has no ports.
