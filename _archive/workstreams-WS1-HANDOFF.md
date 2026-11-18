# WS1 handoff — 2026-11-18 ~10:50 UTC (8th session)

Chat: https://claude.ai/code/session_01JuyZEUgHKypBRfx6deGhfu. A 7th WS1 chat (https://claude.ai/code/session_01JuyZEWZpw9k11fdnaAKr2X) owns T-073 (PR #127): check its STATUS before touching RDW/TGK variant work.
Next chat: "Read workstreams/WS1/HANDOFF.md and START.md and go."

## Open WS1 PRs (all CI green or running, waiting on WS0 review)
- #131 `ev manual check`: facts on retired ids are errors (A-36 S7)
- #133 check-release verifies stored image files by sha256 (#110 nit)
- #134 photo-only nights publish (#110 should-fix 3; replaces old HANDOFF item 2)
- #135 '+' → 'plus' in match keys (WS3 ask). Same-data rebuild: 276 ids unchanged; XPENG P7 x2, P7+ x2, Leaf e+ 62 change. 🟡 Leaf e+ winter range went up (225 → 239) while EPA went down (364 → 346): not traced.
- #136 `years: [from, to]` on generation manual facts (WS3 ask, Decision 059)
- #127 T-073 (7th chat, not mine)

## Next for WS1 (in order)
1. Answer review notes on #131 #133 #134 #135 #136.
2. After the first night run since #110: check refresh.json `images` (fetched / failed / stopped, and `pending_generations` once #134 is in).
3. Ioniq 5 facelift: RDW variant codes F5E62 etc. land on facelift-base (WS3 T-140 item 2). Overlaps T-073: coordinate with the 7th chat.
4. Press photos: only when WS3 marks a maker `allowed` in data/images/press-terms.yaml (none today).
5. #110 nit not done: COMMONS_LICENCE accepts any 2-letter CC port. Needs the real CC 2.0–3.0 port list from creativecommons.org (fetch needed approval; not guessed).
6. Older: #58 follow-up test for the ac_kw_optional rows guard.

## Findings worth keeping
- Full same-data rebuild recipe: detached worktree of origin/main, `uv run ev refresh --force --no-release` (all 16 sources ok, ~20 min, peak 446 MB), then `build_release(data_dir)` with old and new code and diff rows + facts. Copy release 2 assets into the worktree first.
- Release 2 assets for local pytest: see the 6th handoff command (fetch-release.mjs with CATALOGUE_FILES).
