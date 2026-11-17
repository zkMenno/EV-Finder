# QA — launch review: start here (from WS0, 2026-11-17)

You are the **QA reviewer** for EV Shortlist (working title; repo EV-Finder). Almost every launch task was merged without a fresh reviewer (Status "review"). Your job for the next ~2–3 hours: check the launch build as a buyer and as a reviewer would, fix small things, and list the rest.

## Setup
1. Attach the repo with push access (`add_repo zkMenno/EV-Finder`, access `push`), clone, branch `qa/launch-review-1` from `main`. Add your row to `CHATS.md`.
2. Read `AGENTS.md` · `REVIEW.md` (from `origin/main`; what reviewers check) · open PRs + your HANDOFF.md, `docs/spec/launch-scope.md` (the only scope that counts), `BOARD.md` "Launch scope", `docs/design/README.md`.
3. Run the web app locally on the current release (see `apps/web/README.md`) and the pipeline tests.

## Do, in order
1. **Walk the hero** for each of the 4 profiles × 2 countries (NL, UK) × 2 budgets (€15k, €35k): does it return 10 cars with variant + build years, top 5 marked, a reason line, winter range, a used price band for those years, a working "See listings" link? Screenshot each at 360 px and 1280 px (Playwright), save under `audits/A-35-screens/` (small PNGs only).
2. **Walk the catalogue**: Explore filters + URL state, a model / generation / variant page, Compare with "differences only", Simple / Detailed / Nerd, tooltips, light + dark theme, NL and EN.
3. **Data rules spot-check**: 10 random numbers on variant pages → each has a source, date and licence in Nerd mode; estimates labelled; no number without a source.
4. **Scope check**: anything visible that launch-scope.md parks (trip routes, charging pages, bidi badges, clue box, lease figures, accounts) must be behind a flag and off.
5. **Accessibility**: axe on hero, Explore, a variant page, /learn; WCAG AA contrast (UX hard rule).
6. Fix small things yourself (copy, missing i18n keys, broken links, a11y issues, flags left on) in small commits; one PR "QA launch review 1".
7. Everything else → `audits/A-35-launch-review-1.md`: blocker / should-fix / nice-to-have, with page, steps and screenshot, and which workstream owns it. For each launch task you verified, write "Reviewed by QA, 2026-11-17: pass / changes needed" under `## Review` in its task file (you may edit only that section).

## Numbers you may use
Audits A-35–A-39, tasks T-110–T-119 (for follow-ups). No decisions; propose them in WS0's INBOX.

## Finish
PR open, CI green, one line in `workstreams/WS0/INBOX.md`: "QA review 1 done, PR #x, A-35: n blockers".

## Retro (end of every session)
Answer four questions in STATUS.md: what slowed you down; what Menno had to do by hand; which rule would have prevented it; **what did a check miss, and which check would have caught it?** Proposals go to `workstreams/WS0/INBOX.md`; WS0 records them in `docs/process/rules.md`.
