"use client";
// Brand include / exclude picker for the hero's refine step (T-141, Decision 056).
// Ariakit combobox: type to narrow the list, pick several brands (removed via BrandChips).
// Loaded on demand (next/dynamic from Hero) so it adds nothing to the landing page's first load.
import {
  Combobox,
  ComboboxItem,
  ComboboxItemCheck,
  ComboboxPopover,
  ComboboxProvider,
} from "@ariakit/react";
import { useMemo, useState } from "react";

export interface BrandPickerText {
  placeholder: string;
  none: string;
}

export interface Brand {
  id: string;
  name: string;
}

/** Brands whose name contains the query (case- and accent-insensitive), in the given order. */
export function matchBrands(makes: Brand[], query: string): Brand[] {
  const fold = (s: string) => s.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase().trim();
  const q = fold(query);
  if (!q) return makes;
  return makes.filter((m) => fold(m.name).includes(q));
}

export function BrandPicker({
  makes,
  selected,
  onChange,
  text,
  testid,
  inputId,
  hintId,
}: {
  makes: Brand[];
  selected: string[];
  onChange: (ids: string[]) => void;
  text: BrandPickerText;
  testid: string;
  /** The <label htmlFor> and hint live outside this lazy chunk (Hero), so nothing jumps on load. */
  inputId: string;
  hintId: string;
}) {
  const [query, setQuery] = useState("");
  // Filter synchronously: a deferred list let Enter pick a stale first row (found in T-141 verify).
  const matches = useMemo(() => matchBrands(makes, query), [makes, query]);

  // Styling follows the design system (docs/design/components): Field = `evs-input` + `evs-hint`,
  // the list = the one floating layer (`evs-legend`: 1.5px ink border, radius-md, shadow-lift),
  // ticked rows = the "picked" sunflower tint. The picked brands render outside this lazy chunk
  // (BrandChips), and the label and hint in Hero, so they show on first paint.
  return (
    <ComboboxProvider
      selectedValue={selected}
      setSelectedValue={(ids) => onChange([...ids].sort())}
      value={query}
      setValue={setQuery}
      resetValueOnHide
    >
      <Combobox
        id={inputId}
        autoSelect
        placeholder={text.placeholder}
        aria-describedby={hintId}
        className="block h-12 w-full rounded-[6px] border-[1.5px] border-slate-400 bg-white px-3.5 py-2.5 text-[17px] leading-6 text-[var(--ink)] placeholder:text-slate-500"
        data-testid={`${testid}-input`}
      />
      <ComboboxPopover
        gutter={6}
        sameWidth
        unmountOnHide
        className="z-50 max-h-72 overflow-y-auto rounded-[10px] border-[1.5px] border-[var(--ink)] bg-white p-1.5 text-[var(--ink)] shadow-[var(--shadow-lift)]"
        data-testid={`${testid}-list`}
      >
        {matches.length ? (
          matches.map((m) => (
            <ComboboxItem
              key={m.id}
              value={m.id}
              focusOnHover
              // Ticked rows: sunflower tint + bold (the design system's "picked" state). Active row:
              // link fill + surface text, ≥ 6.6:1 against the list in both themes (T-141 review).
              className="flex min-h-12 cursor-pointer items-center gap-2 rounded-[6px] px-2.5 text-[17px] leading-6 aria-selected:bg-[var(--sunflower-tint)] aria-selected:font-bold data-[active-item]:bg-blue-800 data-[active-item]:text-white"
            >
              <ComboboxItemCheck className="w-4" />
              {m.name}
            </ComboboxItem>
          ))
        ) : (
          <div className="px-2.5 py-3 text-[15px] leading-[22px] text-slate-500">{text.none}</div>
        )}
      </ComboboxPopover>
    </ComboboxProvider>
  );
}
