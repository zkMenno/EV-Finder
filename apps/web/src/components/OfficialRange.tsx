// T-143 (Decision 085): the official WLTP range, shown right next to our real range in a secondary
// style, labelled "Official (WLTP)". A missing figure reads "not known": never our estimate in its place.
// No "use client": it renders the client parts (Num, InfoTip) and works from server pages and from Explore.
import type { FieldProvenance } from "@ev/schema";
import type { Level } from "@/lib/state";
import { Num } from "./Num";
import type { NumLabels } from "./num-labels";
import { InfoTip, type TermText } from "./Term";

export interface OfficialRangeText {
  /** "Official (WLTP)" */
  label: string;
  /** "not known" */
  notKnown: string;
  /** One sentence: how the official figure differs from our real range. */
  tip: string;
}

export interface OfficialRangeProps {
  /** One value, or a span over a generation's variants (cards). */
  value: number | null | undefined;
  min?: number;
  provenance?: FieldProvenance;
  sources?: Record<string, string>;
  locale: string;
  labels: NumLabels;
  level?: Level;
  asOf?: string;
  focusable?: boolean;
  text: OfficialRangeText;
  /** The ⓘ with the one-sentence difference (left out inside Explore's table: Tab stops, AGENTS.md rule 12). */
  info?: { href: string; termText: TermText } | false;
  /** Pre-formatted number text (cards' "380–450"). */
  valueText?: string;
  /** Show the label (off where a row header already says "Official (WLTP)"). */
  showLabel?: boolean;
  className?: string;
  testId?: string;
}

export function OfficialRange({
  value,
  provenance,
  sources,
  locale,
  labels,
  level = "simple",
  asOf,
  focusable,
  text,
  info,
  valueText,
  showLabel = true,
  className = "",
  testId = "wltp-range",
}: OfficialRangeProps) {
  const known = typeof value === "number" && Number.isFinite(value) && value > 0;
  return (
    <span
      className={`inline-flex min-w-0 flex-wrap items-center gap-x-1 text-xs font-normal text-slate-700 ${className}`}
      data-testid={testId}
      data-known={known ? "1" : "0"}
      data-km={known ? Math.round(value) : undefined}
    >
      {showLabel ? <span>{text.label}</span> : null}
      {known ? (
        <span className="font-semibold tabular-nums text-slate-800">
          <Num
            value={value}
            text={valueText ? `${valueText}\u00a0km` : undefined}
            unit={valueText ? undefined : "km"}
            digits={0}
            provenance={provenance}
            sources={sources}
            locale={locale}
            labels={labels}
            level={level}
            asOf={asOf}
            focusable={focusable}
          />
        </span>
      ) : (
        <span data-testid="wltp-not-known">{text.notKnown}</span>
      )}
      {info ? (
        <InfoTip label={text.label} href={info.href} text={info.termText}>
          <span className="block">{text.tip}</span>
        </InfoTip>
      ) : null}
    </span>
  );
}
