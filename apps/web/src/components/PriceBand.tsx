// Used-price band. Renders "Not enough data" below MIN_SAMPLES (always, until price sampling exists).
// No hooks: works in server and client components.
import type { Currency } from "@ev/schema";
import { formatMoney } from "@/lib/format";

export const MIN_SAMPLES = 5;

export interface PriceBandProps {
  samples?: number[];
  currency?: Currency;
  locale?: string;
  notEnoughLabel?: string;
  /** e.g. "Based on {n} listings" — {n} is replaced. */
  samplesLabel?: string;
}

/** 25th–75th percentile (linear interpolation). Exported for tests. */
export function quartiles(samples: number[]): [number, number] {
  const s = [...samples].sort((a, b) => a - b);
  const q = (p: number) => {
    const i = (s.length - 1) * p;
    const lo = Math.floor(i);
    const hi = Math.ceil(i);
    return (s[lo] ?? 0) + ((s[hi] ?? 0) - (s[lo] ?? 0)) * (i - lo);
  };
  return [q(0.25), q(0.75)];
}

export function PriceBand({
  samples,
  currency = "EUR",
  locale = "en-GB",
  notEnoughLabel = "Not enough data",
  samplesLabel = "Based on {n} listings",
}: PriceBandProps) {
  const valid = (samples ?? []).filter((x) => Number.isFinite(x) && x > 0);
  if (valid.length < MIN_SAMPLES) {
    return <span className="text-sm italic text-slate-600">{notEnoughLabel}</span>;
  }
  const [lo, hi] = quartiles(valid);
  return (
    <span className="inline-flex flex-col">
      <span className="tabular-nums">
        {formatMoney(lo, currency, locale)} – {formatMoney(hi, currency, locale)}
      </span>
      <span className="text-xs text-slate-600">{samplesLabel.replace("{n}", String(valid.length))}</span>
    </span>
  );
}
