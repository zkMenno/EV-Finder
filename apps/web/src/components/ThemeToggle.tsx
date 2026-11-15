"use client";
// Night drive (dark) on/off. Default follows the system; a click remembers the choice
// (src/lib/theme.ts) and sets <html data-theme>, which /theme-init.js re-applies on every load.
import { useSyncExternalStore } from "react";
import { effectiveTheme, readTheme, writeTheme, type Theme } from "@/lib/theme";

const EVENT = "ev-theme-change";
const MQ = "(prefers-color-scheme: dark)";

function subscribe(cb: () => void): () => void {
  const mq = window.matchMedia?.(MQ);
  mq?.addEventListener("change", cb);
  window.addEventListener(EVENT, cb);
  window.addEventListener("storage", cb);
  return () => {
    mq?.removeEventListener("change", cb);
    window.removeEventListener(EVENT, cb);
    window.removeEventListener("storage", cb);
  };
}

function current(): Theme {
  const attr = document.documentElement.getAttribute("data-theme");
  if (attr === "light" || attr === "dark") return attr;
  return effectiveTheme(readTheme(), !!window.matchMedia?.(MQ).matches);
}

export function ThemeToggle({ label, help }: { label: string; help: string }) {
  // Server render (and the first client render) don't know the theme: null until hydrated.
  const theme = useSyncExternalStore<Theme | null>(subscribe, current, () => null);
  const dark = theme === "dark";
  return (
    <button
      type="button"
      aria-pressed={theme === null ? undefined : dark}
      title={help}
      data-testid="theme-toggle"
      onClick={() => {
        const next: Theme = dark ? "light" : "dark";
        writeTheme(next);
        document.documentElement.setAttribute("data-theme", next);
        window.dispatchEvent(new Event(EVENT));
      }}
      className="inline-flex min-h-9 items-center gap-1 rounded-md border border-slate-400 bg-white px-2 py-1.5 text-sm text-slate-900 hover:border-slate-600"
    >
      <span aria-hidden="true">{dark ? "☾" : "☀"}</span>
      {label}
    </button>
  );
}
