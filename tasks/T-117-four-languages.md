# T-117 DE, FR, ES and IT drafts for every public string
Role: builder   Lane: WS2 (+ WS3 wording): apps/web/src/i18n/, apps/web tests   Wave: launch fixes (A-35)
Status: merged (PR #72, #75)

## Goal
No English UI strings on DE, FR, ES or IT pages.

## Acceptance criteria
- [ ] Every public key in EN has a DE, FR, ES and IT draft (staff-only keys excepted, as for NL); drafts labelled per D6
- [ ] `i18n.test.ts` checks all six languages for every public key
- [ ] e2e: /de/de and /fr/fr hero, Explore, generation, variant, compare, footer show no English UI strings (allow-list for brand and model names)
- [ ] Glossary terms in all six
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
audits/A-35 B5; REVIEW D6

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- **Keys (public = EN minus 12 `staff.*`, 737):** before DE 186, FR 186, ES 168, IT 168 → after 737 each (NL 737). Translated by an agent (DE Sie, FR vous, ES tú, IT tu, matching the existing hero strings); every file carries a `_draft` label (`DRAFT (German): written by an agent…`). `getDict` drops it (only keys EN has), a test proves it never reaches a page.
- **Fixed 2 stale drafts:** `hero.card.priceUsed` / `priceUsedOne` in DE/FR/ES/IT still had `in {country}`, which EN dropped; now match EN.
- **Terms:** FR lease = « location » (as in the existing `pay.lease`); level Nerd = DE „Nerd“, FR/ES/IT Expert/Experto/Esperto; learn = Wissen / Comprendre / Aprende / Impara.
- **Glossary:** `data/taxonomy/glossary_terms.yaml` now has DE/FR/ES/IT `label` + `short` for all 104 terms (drafts, header comment says so; every `short` ≤ 20 words; `validate_taxonomy.py` 0 errors). Cross-lane (data/taxonomy) because the task needs glossary terms in all six. **They reach the site only after the next data release is built** (release 1 has EN + NL only; Q-070).
- **Tests:** `i18n.test.ts` now checks for all five non-EN languages: every public key, no extra keys, no empty strings, same `{placeholders}` as EN; the draft label; glossary label + short in all six. Test-change: two old assertions expected DE/FR to fall back to English (`nav.explore`, `compare.title`, FR `printNote`); they now assert the translations, and the key-by-key fallback is tested on a staff key instead.
- **e2e `e2e/no-english.spec.ts`:** /de/de and /fr/fr hero + Explore + footer, generation, variant and compare pages: no English dictionary string in visible text or aria-labels (browser locale de-DE / fr-FR, so no "also available in English" banner). Taxonomy text from the release (glossary labels, chemistry, cooling, voltage) is stripped first and counted in an annotation: on release 1 it is still English (e.g. "Battery type", "Years", "No active cooling"). Mutation check: pointed at /de/en and /fr/en, it fails with nav.explore, explore.title etc.
- **Open for WS0:** (1) rebuild the release so the glossary drafts show; (2) glossary `technical`, `long`, `nerd_note` and chemistries / cooling / voltage-class labels are still EN + NL only: new task; (3) apps/web/AGENTS.md rule 9 still says other languages fall back to EN (gate file, not touched); (4) `verify --lang de` screenshots the /nl country (DE is not served there), so DE/FR hero screenshots were taken separately.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B5 fixed. -->

WS0 subagent, 2026-11-17, d0a762a: R0–R3, D6, D8, D13 pass; 737/737 public keys in DE/FR/ES/IT; no-english e2e passes on release 2. **A-35 B5 (strings) fixed.**

Reviewed by QA, 2026-11-17 (A-36): pass for B5 strings (no-english e2e passes on release 2). Superseded by Decision 082: drafts must be hidden at launch (A-36 B4, T-137).
