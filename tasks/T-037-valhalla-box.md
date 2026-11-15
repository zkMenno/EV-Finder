# T-037 Valhalla sizing test and routing box
Role: WS4   Lane: infra   Wave: 7
Status: todo

## Goal
Size and run the routing server for Trip fit routes.

## Acceptance criteria
- [ ] Sizing test on a temporary machine for NL+BE+LU+DE+FR+UK: RAM, disk, build time
- [ ] Cheapest Hetzner Arm box that fits (expected €5–15/month; above €50 → ask Menno)
- [ ] Route-summary endpoint behind Caddy, no request logging, coordinates rounded upstream
- [ ] Monthly tile rebuild documented

## Inputs
Decision 013, docs/spec/trip-fit.md §7.

## Out of scope
Scoring (browser).

## Handoff notes

## Review
