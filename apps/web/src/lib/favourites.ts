// Local favourites (heart). localStorage only until accounts exist.
import { createListStore, type ListStore } from "./list-store";
import type { KeyValueStorage } from "./storage";

export const FAV_KEY = "ev-finder:favourites:v1";

export function parseFavourites(raw: unknown): string[] {
  if (!Array.isArray(raw)) return [];
  return [...new Set(raw.filter((x): x is string => typeof x === "string" && x.length > 0))];
}

export interface FavouriteStore extends ListStore<string> {
  toggle(id: string): boolean;
}

export function createFavouriteStore(storage?: () => KeyValueStorage | null): FavouriteStore {
  const base = createListStore<string>({ key: FAV_KEY, parse: parseFavourites, storage });
  return {
    ...base,
    toggle(id) {
      const cur = base.get();
      const on = !cur.includes(id);
      base.set(on ? [...cur, id] : cur.filter((x) => x !== id));
      return on;
    },
  };
}

export const favouriteStore: FavouriteStore = createFavouriteStore();
