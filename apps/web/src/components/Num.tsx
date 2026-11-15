"use client";
// Every number on the site goes through <Num>: it shows the value and, on hover, focus or tap,
// where the value comes from (source + confidence). Reusable on server pages: pass plain
// strings in `labels` (build them with numLabels(t) from "@/components/num-labels").
import type { FieldProvenance } from "@ev/schema";
import { DASH, formatNumber } from "@/lib/format";
import type { Level } from "@/lib/state";
import type { NumLabels } from "./num-labels";
import { usePopover } from "./use-popover";

export interface NumProps {
  value: number | null | undefined;
  /** Metric unit shown after the value, e.g. "km", "kWh". */
  unit?: string;
  provenance?: FieldProvenance | undefined;
  /** source id → display name. */
  sources?: Record<string, string>;
  locale: string;
  labels: NumLabels;
  /** Max fraction digits (default 1). Nerd level shows up to 2. */
  digits?: number;
  /** Pre-formatted text (e.g. money) instead of formatNumber(value). */
  text?: string;
  /** Small line under the value, e.g. the real-range rung. */
  note?: string;
  /** Value is a maker claim, not measured (e.g. dc_peak_kw_is_claim). */
  claim?: boolean;
  /**
   * simple: value only (details in the popover); detailed (default): + text badges;
   * nerd: + raw value, sources and confidence inline.
   */
  level?: Level;
  /** Release date, shown with sources at nerd level (FieldProvenance has no date yet). */
  asOf?: string;
  /** Screen-reader text for the missing-value "—" (default labels.noData). */
  missingLabel?: string;
  /**
   * false: not a Tab stop (hover and tap still open the popover). Explore's table uses this so a
   * row costs a few Tab stops, not one per number; provenance stays reachable from the variant page.
   */
  focusable?: boolean;
}

/** The missing-value dash, with text for screen readers ("—" alone is read as "dash" or skipped). */
export function Missing({ label }: { label: string }) {
  return (
    <span className="text-slate-500" data-testid="num-missing">
      <span aria-hidden="true">{DASH}</span>
      <span className="sr-only">{label}</span>
    </span>
  );
}

/** Text badges for a value (Decision 009). Text, not colour alone. Exported for tests. */
export function numBadges(provenance: FieldProvenance | undefined, labels: NumLabels, claim = false): string[] {
  const out: string[] = [];
  if (claim) out.push(labels.claim);
  if (provenance?.estimate) out.push(labels.estimate);
  const n = provenance?.agreeing_sources;
  if (typeof n === "number" && n >= 2) out.push(labels.agree.replace("{n}", String(n)));
  else if (n === 1) out.push(labels.oneSource);
  return out;
}

export function Num({
  value,
  unit,
  provenance,
  sources,
  locale,
  labels,
  digits = 1,
  text,
  note,
  claim = false,
  level = "detailed",
  asOf,
  missingLabel,
  focusable = true,
}: NumProps) {
  const { buttonProps, popoverProps } = usePopover();

  if (value === null || value === undefined || !Number.isFinite(value)) {
    return <Missing label={missingLabel ?? labels.noData} />;
  }

  const shown = text ?? `${formatNumber(value, locale, level === "nerd" ? Math.max(digits, 2) : digits)}${unit ? `\u00a0${unit}` : ""}`;
  const names = provenance?.source_ids.map((s) => sources?.[s] ?? s).join(", ");
  const badges = level === "simple" ? [] : numBadges(provenance, labels, claim);

  return (
    <span className="inline-flex flex-col items-start">
      <button
        {...buttonProps}
        tabIndex={focusable ? undefined : -1}
        className="whitespace-nowrap rounded-sm tabular-nums underline decoration-slate-400 decoration-dotted underline-offset-4 hover:decoration-slate-800"
      >
        {shown}
      </button>
      {note ? <span className="text-xs text-slate-600">{note}</span> : null}
      {badges.length ? (
        <span className="flex flex-wrap gap-1" data-testid="num-badges">
          {badges.map((b) => (
            <span key={b} className="whitespace-nowrap rounded border border-slate-400 px-1 text-[0.7rem] leading-4 text-slate-700">
              {b}
            </span>
          ))}
        </span>
      ) : null}
      {level === "nerd" ? (
        <span className="max-w-48 text-left text-[0.7rem] leading-4 text-slate-700" data-testid="num-nerd">
          {text ? <span className="block tabular-nums">raw: {value}</span> : null}
          {provenance ? (
            <span className="block">
              {names} · {labels.conf[provenance.confidence]}
              {asOf ? ` · ${asOf}` : ""}
            </span>
          ) : (
            <span className="block">{labels.noSource}</span>
          )}
          {provenance?.note ? <span className="block">{provenance.note}</span> : null}
        </span>
      ) : null}
      <span {...popoverProps}>
        <span className="sr-only">{labels.details}: </span>
        {provenance ? (
          <>
            <span className="block">
              <span className="font-semibold">{labels.source}:</span> {names}
            </span>
            <span className="block">
              <span className="font-semibold">{labels.confidence}:</span> {labels.conf[provenance.confidence]}
            </span>
            {numBadges(provenance, labels, claim).map((b) => (
              <span key={b} className="block">
                {b}
              </span>
            ))}
            {provenance.derived ? <span className="block">{labels.derived}</span> : null}
            {claim ? <span className="block">{labels.claimHelp}</span> : null}
            {provenance.note ? <span className="block text-slate-700">{provenance.note}</span> : null}
          </>
        ) : (
          <span className="block">{labels.noSource}</span>
        )}
      </span>
    </span>
  );
}
