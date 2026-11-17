// Explore and the hero (T-080) share one set of filters and URL params on the landing page. Each
// keeps its own React state; this browser event keeps the two in step without a server round trip.
import type { Answers } from "./shortlist";
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

/** The hero's picker answers (T-067: Explore's "Suggested" sort follows the hero's profile). */
export const PROFILE_EVENT = "ev-finder:profile";

export function publishAnswers(a: Answers): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent<Answers>(PROFILE_EVENT, { detail: a }));
}

export function onAnswers(fn: (a: Answers) => void): () => void {
  if (typeof window === "undefined") return () => {};
  const h = (e: Event) => {
    const d = (e as CustomEvent<Answers>).detail;
    if (d) fn(d);
  };
  window.addEventListener(PROFILE_EVENT, h);
  return () => window.removeEventListener(PROFILE_EVENT, h);
}
