"use client";
// "Differences only" on generation pages (T-045, Decision 019): a toggle that hides spec rows all
// variants share. Static page, so the state lives in `?diff=1` (read after hydration) and the
// rows are hidden with CSS (`data-same` rows inside a `data-only-diff` wrapper); nothing reloads.
import { useEffect, useState, type ReactNode } from "react";

export function DiffOnly({ label, children, enabled = true }: { label: string; children: ReactNode; enabled?: boolean }) {
  const [on, setOn] = useState(false);
  useEffect(() => {
    // Browser-only state after hydration (URL of a static page).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setOn(new URLSearchParams(window.location.search).get("diff") === "1");
  }, []);
  const toggle = () => {
    const next = !on;
    setOn(next);
    const url = new URL(window.location.href);
    if (next) url.searchParams.set("diff", "1");
    else url.searchParams.delete("diff");
    window.history.replaceState(null, "", url.pathname + url.search + url.hash);
  };
  return (
    <div className="group" data-only-diff={on || undefined}>
      {enabled ? (
        <button
          type="button"
          aria-pressed={on}
          onClick={toggle}
          className="mb-2 inline-flex min-h-11 items-center gap-2 rounded-md border border-slate-400 bg-white px-3 py-2 text-sm aria-pressed:border-blue-800 aria-pressed:bg-blue-100 aria-pressed:font-semibold print:hidden"
          data-testid="diff-only"
        >
          <span aria-hidden="true">{on ? "☑" : "☐"}</span>
          {label}
        </button>
      ) : null}
      {children}
    </div>
  );
}
