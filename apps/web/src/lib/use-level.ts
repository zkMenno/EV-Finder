"use client";
// Display level (Simple / Detailed / Nerd) on static pages: `?level=` in the URL wins, else the
// level remembered by Explore (LEVEL_KEY), else "detailed". Static pages are built once, so the
// server snapshot is always "detailed" and the browser switches after hydration.
import { useSyncExternalStore } from "react";
import { readStorage } from "./storage";
import { LEVEL_KEY, LEVELS, type Level } from "./state";

/** Pure: the level from a query string and a stored value. Exported for tests. */
export function resolveLevel(search: string, stored: string | null): Level {
  const q = new URLSearchParams(search).get("level");
  if (q && (LEVELS as readonly string[]).includes(q)) return q as Level;
  if (stored && (LEVELS as readonly string[]).includes(stored)) return stored as Level;
  return "detailed";
}

function subscribe(onChange: () => void): () => void {
  window.addEventListener("storage", onChange);
  window.addEventListener("popstate", onChange);
  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener("popstate", onChange);
  };
}

const snapshot = (): Level => resolveLevel(window.location.search, readStorage(LEVEL_KEY));
const serverSnapshot = (): Level => "detailed";

export function useLevel(): Level {
  return useSyncExternalStore(subscribe, snapshot, serverSnapshot);
}
