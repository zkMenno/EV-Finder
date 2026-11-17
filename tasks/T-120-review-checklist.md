# T-120 Diff-triggered review checklist (REVIEW.md)
Role: WS0   Lane: REVIEW.md, AGENTS.md (review section)   Wave: process
Status: todo

## Goal
Reviewers check only what a diff triggers, against rules that live on `main`, with evidence instead of opinions.

## Acceptance criteria
- [ ] `workstreams/WS0/drafts/REVIEW.md` reviewed, adjusted and moved to `/REVIEW.md` on main
- [ ] AGENTS.md "Reviewer / tester" row and review flow point to REVIEW.md and say: read it from `origin/main`, not the PR branch
- [ ] QA START.md and every workstream START.md mention REVIEW.md in "read first"
- [ ] Task `## Review` sections list the triggered item ids (e.g. "R0–R3, D1, D3: pass")
- [ ] One review is for one commit: if the head moves during review, re-run R0 and the triggered items

## Inputs
Article: Claude Code team on verification (diff-triggered reliability checklist, one reviewer with multiple rounds, REVIEW.md from base branch). Proposed in the verification-analysis chat (CHATS.md).

## Out of scope
More reviewer chats. Tune one reviewer; don't stack reviewers.

## Handoff notes

## Review
