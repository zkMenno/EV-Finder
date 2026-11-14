# Changelog — EV Finder

What shipped, per wave. Written at the end of each wave, not per commit. Focuses on what changed and why.

---

## 2026-11-15 — Repo set up

Created the public repo with an AGPL-3.0 licence for code and CC BY 4.0 for published data (Decision 002). Added the agent scaffold and the workflow files from the spec: AGENTS.md, CLAUDE.md, BOARD.md, QUESTIONS.md, DECISIONS.md, ROADMAP.md, a task template, and `research/` and `audits/` folders (Decision 001).

Added a CI workflow that runs repo checks on every push and pull request, and turns on web and pipeline jobs automatically once `apps/web` and `pipeline` exist. Added Dependabot for GitHub Actions, issue templates (bug, data issue, idea), a PR template, CODEOWNERS, SECURITY.md and CONTRIBUTING.md. Security settings (secret scanning, push protection, Dependabot alerts, private vulnerability reporting) and the `main` ruleset are switched on by hand in GitHub settings.

<!-- Agentic Scaffold v0.5.0 | https://github.com/montymerlin/agentic-scaffold-plugin -->
