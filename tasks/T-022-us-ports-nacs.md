# T-022 US charging ports per model year + Supercharger filter
Role: builder (WS1 data, WS2 web)   Lane: data/seed, apps/web   Wave: phase 4 (Next)
Status: todo (parked until US phase)

## Goal
ChargingPort rows for US variants per model year (CCS1 / native NACS / adapter / Magic Dock) and the "Plugs into Tesla Superchargers" filter with "no adapter needed" sub-filter.

## Acceptance criteria
- [ ] Every US variant has ports per model year (e.g. GM 2026 mostly CCS1 + adapter, GM 2027 native NACS; Hyundai Ioniq 5 2025+ native)
- [ ] Note adapters needed the other way (NACS→CCS1, J1772 for home L2)
- [ ] Verify R-01 🔴: older Teslas at third-party J3400 sites; bidirectional over NACS
- [ ] Sources: maker NACS pages (GM, Ford, Hyundai…), tesla.com/NACS, AFDC connector stats

## Inputs
research/R-01-bidirectional-and-connectors.md §5

## Handoff notes

## Review
