---
name: verify
description: Prove a web change works the way a buyer uses it — walk the flows in e2e/feature-map.yaml on a production build, take screenshots, and produce the evidence pack for the PR. Use before opening or updating any apps/web PR, and when reviewing one.
---

# Verify the web app (T-126)

"Done means proven." This skill runs the real site, clicks through what a buyer does, checks
each expected result and writes a report you paste into the PR. Commits then end with
`Verified: verify-web (<headline>)`.

## 1. Build once

```bash
cd apps/web
APP_URL=https://ev.example.com pnpm build          # published release (data/releases/<latest>)
```

On the dev fixture instead (38 variants, no release needed): build with an empty catalogue dir,
then pass `--fixture` to verify.

```bash
mkdir -p /tmp/empty-cat && CATALOGUE_DIR=/tmp/empty-cat APP_URL=https://ev.example.com pnpm build
```

## 2. Run

```bash
pnpm --filter @ev/web verify --changed     # only flows your diff touches (vs origin/main)
pnpm --filter @ev/web verify               # every flow: before a release or a big change
pnpm --filter @ev/web verify --repeat 3    # stress test: a flow that passes 2 of 3 is FLAKY
```

Other options: `--only hero-nerd,tooltip` · `--fixture` · `--url http://localhost:3100`
(reuse a running `next start`; otherwise verify starts its own on port 3199) · `--no-shots` ·
`--lang de` (second language for screenshots, default nl) · `--base <ref>`.

Exit code 0 = all pass; 1 = a check failed or was flaky; 2 = setup problem (no build, bad map).

## 3. Read the output

`apps/web/verify-report/` (git-ignored):

- `summary.md` — the evidence pack. Paste it into the PR body under **Evidence**.
- `verify-report.md` — per flow: every step with timing, every check (✓/✗), and links to the
  screenshots. A failure reads like a bug report: *what* broke, *why it matters*, expected vs found.
- `<flow>--360-light.png`, `--360-dark`, `--1280-light`, `--1280-dark`, `--nl-360-light` —
  attach the ones that show your change (drag into the PR, or SendUserFile for Menno).

Every page a flow ends on is also checked for: no script crash, no raw dictionary key
(`hero.card.price`) on screen, the right `<html lang>`, and (at 360 px) no sideways scroll.

## 4. Pick the flows: the feature map

`apps/web/e2e/feature-map.yaml` lists each buyer flow: steps, expected results in buyer words,
and `triggers` (source globs). `--changed` walks every flow whose triggers match your diff.

- **New user-facing feature?** Add a flow in the same PR. Reviewers grade against the map.
- **Changing an existing flow's checks?** That's changing the rubric: own PR, WS0 approves
  (REVIEW R3 — checks stay out of reach of the change they judge).
- `@name` means `[data-testid="name"]` (not inside XPath). Quote globs with brackets:
  `"src/app/[[]country]/[[]lang]/page.tsx"`.
- Counts that depend on how many cars we publish get `on: release`.
- `src/lib/verify-map.test.ts` fails CI if the map is invalid or a trigger matches no file.

## 5. Flaky or failing

Never retry until green, never add sleeps. Read the step trace: a timeout names the selector
that never appeared. Fix the cause (app or selector); if a flow can't be made stable, remove it
in a gate PR and open a task (docs/process/rules.md).

## Reviewers

Run `verify --changed` on the PR head yourself (fresh build) rather than trusting the pasted
summary; compare the screenshots with the claims in the PR. REVIEW D8 (screenshots 360/1280 ×
light/dark) is satisfied by this report plus axe for new UI.
