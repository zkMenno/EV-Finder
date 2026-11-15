// Compare tray state: max 4 variants, persisted in localStorage so it survives
// navigation and reloads. Never cleared implicitly.
import { createListStore, type ListStore } from "./list-store";
import type { KeyValueStorage } from "./storage";

export const COMPARE_MAX = 4;
export const COMPARE_KEY = "ev-finder:compare:v1";

export interface CompareItem {
  id: string;
  /** Display label cached so the tray can render on any page without the catalogue. */
  label: string;
}

export function parseCompare(raw: unknown): CompareItem[] {
  if (!Array.isArray(raw)) return [];
  const out: CompareItem[] = [];
  for (const x of raw) {
    if (!x || typeof x !== "object") continue;
    const { id, label } = x as Record<string, unknown>;
    if (typeof id !== "string" || !id || out.some((o) => o.id === id)) continue;
    out.push({ id, label: typeof label === "string" && label ? label : id });
    if (out.length === COMPARE_MAX) break;
  }
  return out;
}

export type AddResult = "added" | "exists" | "full";

export function addItem(items: readonly CompareItem[], item: CompareItem): { items: readonly CompareItem[]; result: AddResult } {
  if (items.some((i) => i.id === item.id)) return { items, result: "exists" };
  if (items.length >= COMPARE_MAX) return { items, result: "full" };
  return { items: [...items, item], result: "added" };
}

export function removeItem(items: readonly CompareItem[], id: string): readonly CompareItem[] {
  return items.filter((i) => i.id !== id);
}

export function compareHref(country: string, items: readonly CompareItem[]): string {
  return `/${country}/compare?ids=${items.map((i) => encodeURIComponent(i.id)).join(",")}`;
}

export interface CompareStore extends ListStore<CompareItem> {
  add(item: CompareItem): AddResult;
  remove(id: string): void;
  clear(): void;
  has(id: string): boolean;
}

export function createCompareStore(storage?: () => KeyValueStorage | null): CompareStore {
  const base = createListStore<CompareItem>({ key: COMPARE_KEY, parse: parseCompare, storage });
  return {
    ...base,
    add(item) {
      const { items, result } = addItem(base.get(), item);
      if (result === "added") base.set(items);
      return result;
    },
    remove(id) {
      base.set(removeItem(base.get(), id));
    },
    clear() {
      base.set([]);
    },
    has(id) {
      return base.get().some((i) => i.id === id);
    },
  };
}

/** The app-wide instance (browser). */
export const compareStore: CompareStore = createCompareStore();
