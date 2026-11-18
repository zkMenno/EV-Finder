# T-147 Design system: confirm --line-strong, contrast checker on all grounds, font licences

Role: builder   Lane: UX (docs/design, workstreams/UX/tools)   Wave: launch
Status: todo

## Goal
The web batch (#158) raised `--line-strong` to ≥ 3:1 (light `#7789a5`, dark `#5e7195`) on paper, paper-sea, surface and surface-sunk; #154 shipped the brand fonts. The design system docs and checker must match.

## Acceptance criteria
- [ ] Accept the two `--line-strong` values or adjust them (keep ≥ 3:1 against all four grounds in both themes; AA is the standard) in docs/design/tokens.json; if adjusted, hand the values to the next web batch via workstreams/WS0/INBOX.md.
- [ ] workstreams/UX/tools/contrast.py checks UI pairs (borders, focus, icons) against all four grounds (paper, paper-sea, surface, surface-sunk), both themes; fails under 3:1 for non-text and 4.5:1 for text.
- [ ] docs/design/README.md contrast line (~line 87) states the measured ratios from the script output.
- [ ] docs/design/fonts/ gets the SIL Open Font License texts (OFL.txt) for Atkinson Hyperlegible, Bitter and Patrick Hand, with copyright lines from the font sources.
- [ ] One PR, script output in the PR body, fresh review, "Verified:" on every commit.

## Handoff notes

## Review
