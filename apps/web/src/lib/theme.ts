// Light "Day trip" / dark "Night drive" (design system v2). The default follows the system
// (prefers-color-scheme); a choice made with the toggle is remembered in localStorage and applied
// before first paint by /theme-init.js (app/theme-init.js/route.ts).
import { readStorage, writeStorage, type KeyValueStorage } from "./storage";

export const THEME_KEY = "ev-finder:theme:v1";
export type Theme = "light" | "dark";

/** Body of /theme-init.js: sets <html data-theme> from the remembered choice, before first paint. */
export const THEME_INIT_JS = `(function(){try{var t=window.localStorage.getItem(${JSON.stringify(THEME_KEY)});if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}catch(e){}})();\n`;

export function isTheme(v: unknown): v is Theme {
  return v === "light" || v === "dark";
}

/** The remembered choice, or null (= follow the system). */
export function readTheme(storage?: KeyValueStorage | null): Theme | null {
  const v = storage === undefined ? readStorage(THEME_KEY) : readStorage(THEME_KEY, storage);
  return isTheme(v) ? v : null;
}

export function writeTheme(theme: Theme, storage?: KeyValueStorage | null): boolean {
  return storage === undefined ? writeStorage(THEME_KEY, theme) : writeStorage(THEME_KEY, theme, storage);
}

/** What is showing: the remembered choice, else the system setting. */
export function effectiveTheme(stored: Theme | null, systemDark: boolean): Theme {
  return stored ?? (systemDark ? "dark" : "light");
}
