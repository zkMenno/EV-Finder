"use client";
// Picked brands as removable "picked" toggles (design system `evs-pick[aria-pressed=true]`: ink
// border, sunflower tint). Kept out of the lazy BrandPicker chunk so brands already in the URL
// render on first paint and nothing jumps when the picker arrives (T-141 re-review).

export function BrandChips({
  ids,
  name,
  onRemove,
  removeLabel,
  inputTestId,
}: {
  ids: string[];
  name: (id: string) => string;
  onRemove: (ids: string[]) => void;
  /** "Remove {name}" */
  removeLabel: string;
  /** Focus goes back to this input when the last chip is removed. */
  inputTestId: string;
}) {
  if (!ids.length) return null;
  const remove = (id: string, list: HTMLElement | null) => {
    const i = ids.indexOf(id);
    onRemove(ids.filter((x) => x !== id));
    // The focused chip unmounts: move focus to the next chip, else the previous one, else the input.
    requestAnimationFrame(() => {
      const chips = list?.querySelectorAll("button");
      const target: HTMLElement | null | undefined = chips?.length
        ? chips[Math.min(i, chips.length - 1)]
        : document.querySelector<HTMLElement>(`[data-testid="${inputTestId}"]`);
      target?.focus();
    });
  };
  return (
    <ul className="mt-3 flex flex-wrap gap-2">
      {ids.map((id) => (
        <li key={id}>
          <button
            type="button"
            onClick={(e) => remove(id, e.currentTarget.closest("ul"))}
            aria-label={removeLabel.replace("{name}", name(id))}
            className="inline-flex min-h-12 items-center gap-2 rounded-[10px] border-2 border-[var(--ink)] bg-[var(--sunflower-tint)] py-2.5 pl-3 pr-4 text-[17px] leading-6 font-bold text-[var(--ink)]"
          >
            <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" className="shrink-0">
              <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            {name(id)}
          </button>
        </li>
      ))}
    </ul>
  );
}
