// Explore and the hero (T-080) share one set of filters and URL params on the landing page. Each
// keeps its own React state; this browser event keeps the two in step without a server round trip.
import type { ExploreFilters } from "./state";

export const FILTER_EVENT = "ev-finder:filters";

export interface FilterEventDetail {
  filters: ExploreFilters;
  /** Who sent it, so a component ignores its own echo. */
  from: "explore" | "hero";
}

export function publishFilters(detail: FilterEventDetail): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent<FilterEventDetail>(FILTER_EVENT, { detail }));
}

/** Subscribes to filter changes sent by the other component; returns the unsubscribe function. */
export function onFilters(me: FilterEventDetail["from"], fn: (f: ExploreFilters) => void): () => void {
  if (typeof window === "undefined") return () => {};
  const h = (e: Event) => {
    const d = (e as CustomEvent<FilterEventDetail>).detail;
    if (d && d.from !== me) fn(d.filters);
  };
  window.addEventListener(FILTER_EVENT, h);
  return () => window.removeEventListener(FILTER_EVENT, h);
}
