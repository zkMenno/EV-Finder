"use client";
import { useSyncExternalStore } from "react";
import { getEmpty, type ListStore } from "./list-store";

/** Server snapshot is always empty, so SSR and first client render match. */
export function useListStore<T>(store: ListStore<T>): readonly T[] {
  return useSyncExternalStore(store.subscribe, store.get, getEmpty<T>);
}
