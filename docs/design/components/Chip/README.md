# Chip

Chips qualify a car or a number with a short fact; they are not buttons.

| Variant | Class | Means |
|---|---|---|
| Money | `evs-chip--money` | A saving or cost fact. Sunflower tint |
| Checked | `evs-chip--checked` | Data quality tier "checked" (2+ agreeing sources) |
| Caution | `evs-chip--caution` | Air-cooled pack, single source, estimate, older 400 V only |
| Fault | `evs-chip--fault` | A known issue from inspection data |
| Plain | `evs-chip--plain` | Years, body type, neutral tags |

- Always an icon plus words: colour alone never carries the meaning.
- Put a caution chip right next to the number it qualifies, not in a pile at the top.
- At most three chips per card in Simple mode.
- Filter pills are a different thing (toggle buttons with `aria-pressed`) and use `radius-sm` with a `line-strong` border.
