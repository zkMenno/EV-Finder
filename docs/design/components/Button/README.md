# Button

Buttons start an action; there is one primary button per view.

| Variant | Class | Use |
|---|---|---|
| Primary | `evs-btn evs-btn--primary` | The one main action: "See listings", "Show cars", "Compare 3 cars" |
| Secondary | `evs-btn evs-btn--secondary` | Other important actions: "Share your shortlist", "Rule out" |
| Ghost | `evs-btn evs-btn--ghost` | Low-stakes actions that read as links: "Clear filters", "Read more" |

- 48px tall (`control-h`), label in `label` style (17px bold Atkinson), `radius-md`.
- Primary uses `action` + `on-action` (4.8:1 light, 7.4:1 dark) and `shadow-sticker`; hover `action-hover`; pressed moves 1px down.
- Verb first, sentence case, 1–4 words. The resulting toast repeats the verb ("Added to compare").
- An external destination gets the external-link icon after the label and names the site.
- Don't disable. Keep it active and explain on press what is missing.
- Use `<a>` for navigation (listings, pages) and `<button>` for actions.
