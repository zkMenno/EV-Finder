"use client";
// Brand include / exclude picker for the hero's refine step (T-141, Decision 056).
// Ariakit combobox: type to narrow the list, pick several brands, remove them as chips.
// Loaded on demand (next/dynamic from Hero) so it adds nothing to the landing page's first load.
import {
  Combobox,
  ComboboxItem,
  ComboboxItemCheck,
  ComboboxLabel,
  ComboboxPopover,
  ComboboxProvider,
} from "@ariakit/react";
import { useMemo, useState } from "react";

export interface BrandPickerText {
  label: string;
  placeholder: string;
  /** "Remove {name}" */
  remove: string;
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
}: {
  makes: Brand[];
  selected: string[];
  onChange: (ids: string[]) => void;
  text: BrandPickerText;
  testid: string;
}) {
  const [query, setQuery] = useState("");
  // Filter synchronously: a deferred list let Enter pick a stale first row (found in T-141 verify).
  const matches = useMemo(() => matchBrands(makes, query), [makes, query]);
  const name = (id: string) => makes.find((m) => m.id === id)?.name ?? id;

  return (
    <div data-testid={testid}>
      <ComboboxProvider
        selectedValue={selected}
        setSelectedValue={(ids) => onChange([...ids].sort())}
        value={query}
        setValue={setQuery}
        resetValueOnHide
      >
        <ComboboxLabel className="block text-sm font-semibold">{text.label}</ComboboxLabel>
        <Combobox
          autoSelect
          placeholder={text.placeholder}
          className="mt-1 min-h-11 w-full max-w-sm rounded-md border border-slate-400 bg-white px-3 text-base text-slate-900"
          data-testid={`${testid}-input`}
        />
        <ComboboxPopover
          gutter={4}
          sameWidth
          unmountOnHide
          className="z-50 max-h-72 overflow-y-auto rounded-md border border-slate-300 bg-white p-1 text-slate-900 shadow-lg"
          data-testid={`${testid}-list`}
        >
          {matches.length ? (
            matches.map((m) => (
              <ComboboxItem
                key={m.id}
                value={m.id}
                focusOnHover
                className="flex min-h-11 cursor-pointer items-center gap-2 rounded px-2 data-[active-item]:bg-blue-50"
              >
                <ComboboxItemCheck className="w-4 text-blue-800" />
                {m.name}
              </ComboboxItem>
            ))
          ) : (
            <div className="px-2 py-3 text-sm text-slate-700">{text.none}</div>
          )}
        </ComboboxPopover>
      </ComboboxProvider>
      {selected.length ? (
        <ul className="mt-2 flex flex-wrap gap-2" aria-label={text.label}>
          {selected.map((id) => (
            <li key={id}>
              <button
                type="button"
                onClick={() => onChange(selected.filter((x) => x !== id))}
                aria-label={text.remove.replace("{name}", name(id))}
                className="inline-flex min-h-11 items-center gap-1 rounded-full border border-blue-800 bg-blue-50 px-3 text-sm text-blue-900"
              >
                {name(id)}
                <span aria-hidden="true">×</span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
