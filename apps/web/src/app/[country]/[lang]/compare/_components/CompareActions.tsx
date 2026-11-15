"use client";
// Share (copy URL) and print buttons for the compare page.
import { useRef, useState } from "react";

export interface CompareActionsText {
  share: string;
  copied: string;
  copyFailed: string;
  print: string;
}

/** Old-browser / insecure-context fallback: copy via a hidden textarea. */
function legacyCopy(text: string): boolean {
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(ta);
    return ok;
  } catch {
    return false;
  }
}

export function CompareActions({ text }: { text: CompareActionsText }) {
  const [status, setStatus] = useState<"idle" | "copied" | "failed">("idle");
  const [url, setUrl] = useState("");
  const input = useRef<HTMLInputElement>(null);

  async function share() {
    const href = window.location.href;
    setUrl(href);
    let ok = false;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(href);
        ok = true;
      }
    } catch {
      ok = false;
    }
    if (!ok) ok = legacyCopy(href);
    setStatus(ok ? "copied" : "failed");
    if (!ok) requestAnimationFrame(() => input.current?.select());
  }

  return (
    <div className="flex flex-wrap items-center gap-2 print:hidden">
      <button
        type="button"
        onClick={share}
        className="inline-flex min-h-11 items-center rounded-md border border-slate-500 px-4 text-sm font-semibold hover:bg-slate-100"
        data-testid="compare-share"
      >
        {text.share}
      </button>
      <button
        type="button"
        onClick={() => window.print()}
        className="inline-flex min-h-11 items-center rounded-md border border-slate-500 px-4 text-sm font-semibold hover:bg-slate-100"
      >
        {text.print}
      </button>
      <span role="status" aria-live="polite" className="text-sm">
        {status === "copied" ? text.copied : null}
      </span>
      {status === "failed" ? (
        <label className="flex w-full flex-col gap-1 text-sm">
          {text.copyFailed}
          <input ref={input} readOnly value={url} className="w-full rounded border border-slate-400 px-2 py-1" onFocus={(e) => e.currentTarget.select()} />
        </label>
      ) : null}
    </div>
  );
}
