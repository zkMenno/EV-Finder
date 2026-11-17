# WS1 handoff — 2026-11-17 ~07:00 local (06:00 UTC)

Chat: https://claude.ai/code/session_01JuyZEWFXbkeYSii8dVSWnx (3rd WS1 session). Next chat prompt:

```
Attach github.com/zkMenno/EV-Finder with push access (add_repo, access: push), then read workstreams/WS1/HANDOFF.md and START.md and go.
```

## State: 3 PRs open
| PR | Branch | What |
|---|---|---|
| [#44](https://github.com/zkMenno/EV-Finder/pull/44) | `t-123-release-diff` | T-123: blocking `release_diff` QA check, config/approved_changes.yaml, Decision 044. CI green. |
| [#51](https://github.com/zkMenno/EV-Finder/pull/51) | `t-127-verify-pipeline` | T-127: `ev verify` + skill, audits/A-32, this handoff. **Branched from #44**: merge #44 first. |
| [#49](https://github.com/zkMenno/EV-Finder/pull/49) | `t-124-property-tests` | T-124: Hypothesis property tests; Decision 045 (sibling rung by WLTP ratio). From main. |

DECISIONS.md: #44 adds 044, #49 adds 045 at the same spot → a two-entry conflict; keep both.

## Open work for WS1 (next, in order)
1. Review notes on #44 / #49 / #51 if they show up in the INBOX.
2. A-32 findings 1–2 (task number from WS0): which source/rule changed `consumption_kwh_100km` (−11 % median on 45 variants) and why 19 variants lost `wltp_range_km`. Use `ev verify --data-dir <scratch>` and its `-release-diff.csv`.
3. WS3 asks still open: '+' → 'plus' in `normalise.key` (T-068; flip the strict xfail in test_t124_properties when done), KBA/DfT/EEA aliases for the new models, optional `years:` on manual facts (T-031).
4. WS0 delegated: Catalogue.retired_ids + FactField entries for ac_kw_optional/EPA/one_pedal/regen_paddles/ota_updates (unblocks T-063).
5. rdw-tgk refresh failed (SnapshotError: nothing to snapshot).

## Live staging
Recorded today in /tmp/live/data on the session machine (gone with the session). Recreate: copy data/ to a scratch dir, `EV_DATA_DIR=<dir> uv run ev refresh --sources <all> --no-release` (~15 min, peak 413 MB).

## Decisions this chat
- 044: release diff N vs N-1 blocks unapproved changes.
- 045: sibling-variant real range scales by WLTP ratio.
