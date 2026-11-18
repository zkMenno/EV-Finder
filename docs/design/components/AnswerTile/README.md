# AnswerTile

One answer to a hero question (T-132, signed off 2026-11-17). Reference: `explorations/staging-r1/` (CSS classes `.opt`, `.opts`, `.opts.two` in `workstreams/UX/tools/staging_r1.py`).

- A radio inside a `fieldset` per question; the tile is the label. Full width, min 64 px tall, `radius-md`, 2 px `line-strong` border, `shadow-sticker`.
- Bold label (18 px) + optional one-line hint (15 px, `ink-2`). Optional 28 px Symbol on the left.
- Right edge: empty ring when not picked, the tick-V when picked. Picked also gets a 3 px `ink` border and `paper-sea` fill: never colour alone.
- Country uses two columns (`.opts.two`), every other question one column.
- Tapping an answer moves on to the next question after ≈250 ms (instant with reduced motion). Back link under the tiles; the answer trail above them (pills with a pencil, tap = jump back).
