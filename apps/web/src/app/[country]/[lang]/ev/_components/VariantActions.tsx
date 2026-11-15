"use client";
// Heart + add-to-compare for a variant page. Reuses the tray's stores (read-only import).
import { COMPARE_MAX, compareStore } from "@/lib/compare-store";
import { favouriteStore } from "@/lib/favourites";
import { useListStore } from "@/lib/use-list-store";

export interface VariantActionsText {
  favAdd: string;
  favRemove: string;
  compareAdd: string;
  compareAddLabel: string;
  compareRemoveLabel: string;
  compareFull: string;
  compare: string;
}

export function VariantActions({ id, name, text }: { id: string; name: string; text: VariantActionsText }) {
  const favs = useListStore(favouriteStore);
  const cmp = useListStore(compareStore);
  const fav = favs.includes(id);
  const inCmp = cmp.some((c) => c.id === id);
  const full = !inCmp && cmp.length >= COMPARE_MAX;
  return (
    <div className="flex flex-wrap items-center gap-2 print:hidden">
      <button
        type="button"
        aria-pressed={inCmp}
        aria-label={inCmp ? text.compareRemoveLabel : full ? text.compareFull : text.compareAddLabel}
        title={full ? text.compareFull : undefined}
        disabled={full}
        data-testid="compare-toggle"
        onClick={() => (inCmp ? compareStore.remove(id) : compareStore.add({ id, label: name }))}
        className={`inline-flex min-h-11 items-center gap-2 rounded-md border px-4 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50 ${inCmp ? "border-blue-800 bg-blue-800 text-white" : "border-slate-500 text-slate-900 hover:bg-slate-100"}`}
      >
        <span aria-hidden="true">{inCmp ? "✓" : "+"}</span>
        {text.compare}
      </button>
      <button
        type="button"
        aria-pressed={fav}
        aria-label={fav ? text.favRemove : text.favAdd}
        onClick={() => favouriteStore.toggle(id)}
        className="grid h-11 w-11 place-items-center rounded-full border border-slate-400 hover:bg-slate-100"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true" className={`h-5 w-5 ${fav ? "fill-red-700 stroke-red-700" : "fill-none stroke-slate-700"}`} strokeWidth="2">
          <path d="M12 21s-7.5-4.6-9.5-9.2C1 8.2 3.4 4.5 7 4.5c2 0 3.6 1.1 5 3 1.4-1.9 3-3 5-3 3.6 0 6 3.7 4.5 7.3C19.5 16.4 12 21 12 21z" />
        </svg>
      </button>
    </div>
  );
}
