// Used-price band for one generation in one country (schema `UsedPriceBand`: median = typical,
// p25–p75 = the band). Renders "Not enough data" without a sourced band of ≥ MIN_SAMPLES samples,
// or when the band's currency is not the market's (always, until T-056 publishes used prices).
// No hooks: works in server and client components.
import type { Currency, UsedPriceBand } from "@ev/schema";
import { formatMoney } from "@/lib/format";

export const MIN_SAMPLES = 5;

export interface PriceBandProps {
  band?: UsedPriceBand;
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

/** True when a band may be shown on a market priced in `currency`. Exported for tests. */
export function showable(band: UsedPriceBand | undefined, currency: Currency): band is UsedPriceBand {
  return !!band && band.source_id.length > 0 && band.samples >= MIN_SAMPLES && band.median > 0 && band.currency === currency;
}

export function PriceBand({
  band,
  currency = "EUR",
  locale = "en-GB",
  notEnoughLabel = "Not enough data",
  samplesLabel = "Based on {n} listings",
}: PriceBandProps) {
  if (!showable(band, currency)) {
    return <span className="text-sm italic text-slate-600">{notEnoughLabel}</span>;
  }
  const money = (v: number) => formatMoney(v, band.currency, locale);
  const ranged = band.p25 != null && band.p75 != null && band.p75 >= band.p25;
  return (
    <span className="inline-flex flex-col">
      <span className="tabular-nums">{ranged ? `${money(band.p25!)} – ${money(band.p75!)}` : money(band.median)}</span>
      <span className="text-xs text-slate-600">{samplesLabel.replace("{n}", String(band.samples))}</span>
    </span>
  );
}
