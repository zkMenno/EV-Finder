# LegendTooltip

The ⓘ legend is the glossary: one or two plain sentences explaining a term, styled like a map's legend box.

- Trigger: `evs-info`, a 28px circle with a 48px hit area. Opens on tap or click, not hover alone, and closes on Escape or an outside tap.
- Panel: `evs-legend`, a 1.5px ink border, `radius-md`, `shadow-lift`, max 320px wide.
- Content comes from the `glossary_terms` table (6 languages): map symbol, plain name, one or two sentences, a "Read more" link to /learn.
- Every plain label pairs with its technical term (`evs-label` + `evs-term`) and one legend.
- Only one legend is open at a time. It is the one floating layer.
- Give the trigger an aria-label that asks the question: "What is 400 V compatibility?"
