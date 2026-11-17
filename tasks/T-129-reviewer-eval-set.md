# T-129 Test the reviewer against bugs we really had (after launch)
Role: WS0 + QA   Lane: audits/review-evals/   Wave: after launch (parked)
Status: todo (parked until after launch)

## Goal
Know whether our reviewer setup catches the bugs that mattered, before tuning its prompt or adding rules.

## Acceptance criteria
- [ ] `audits/review-evals/cases.yaml`: each past miss = commit before the fix, one-sentence answer key, severity. Start with A-20 B1 (stale release), A-30 EPA range-class wrong attachments, MG4 near-duplicates, consumption 22 % low vs EPA, Model Y LR vs Juniper identical values, P7+ normalisation, tokens.generated.css stale.
- [ ] Same number of clean merged PRs as controls (to catch over-flagging).
- [ ] Run the reviewer (REVIEW.md + fresh agent) on each; credit only findings that match the answer key. Report recall and false alarms; keep tuning cases separate from the fixed test cases.
- [ ] Every missed case → a REVIEW item or test (T-122).

## Inputs
Article: track reverts and rejected changes, recreate the repo at review time, one-sentence answer key, controls, separate tuning and test sets.

## Handoff notes

## Review
