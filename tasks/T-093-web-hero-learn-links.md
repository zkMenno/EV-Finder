# T-093 Hero links the launch /learn guides
Role: WS2   Lane: apps/web   Wave: 10
Status: done (merged by WS2 with Menno's OK, 2026-11-17)

## Goal
Launch scope §3 names three /learn pages (winter range, charging in 2026, batteries and used battery health). First-time buyers reach them from the hero results ("Good to know before you buy").

## Acceptance criteria
- [x] Up to three links, in order winter range → charging in 2026 → batteries (T-082 slug `batteries` or `battery-health`, else chemistries), only for articles that exist
- [x] Titles in the page language (EN fallback), EN + NL label, e2e

## Handoff notes
- 2026-11-15 WS2: the slug list lives in `app/[country]/[lang]/page.tsx`; when WS3 publishes T-082 under another slug, add it there.

## Review
- Reviewed by QA, 2026-11-17 (main @ d086d49, REVIEW.md draft R0–R3 + triggered D items): changes needed — /learn links pass (e2e); DE/FR/ES/IT strings cover the hero only (A-35 B5).
