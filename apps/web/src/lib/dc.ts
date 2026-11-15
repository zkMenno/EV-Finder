// One rule for "does this car have DC charging data?" (T-009/T-010 review). Without a DC figure we
// must never describe how the car behaves on DC chargers ("native", "booster · 50 kW", "fast on
// 400 V: yes"): those fields read as missing. Used by Explore, SpecValue, cellValue() (spec diff and
// compare) and the generation key facts. Pure: safe on server and client.
import type { PublishedVariant } from "@ev/schema";

/** DC figures that count as "we know something about DC charging". */
export const DC_FIGURE_KEYS = ["dc_peak_kw", "dc_avg_10_80_kw", "dc_minutes_10_80"] as const;

/** Fields that describe DC behaviour and are only shown when the car has DC data. */
export const DC_DEPENDENT_KEYS = ["charger_400v_mode", "charger_400v_kw", "fast_on_400v"] as const;

export type DcDependentKey = (typeof DC_DEPENDENT_KEYS)[number];

type DcRow = Partial<Pick<PublishedVariant, (typeof DC_FIGURE_KEYS)[number]>>;

const positive = (v: unknown): boolean => typeof v === "number" && Number.isFinite(v) && v > 0;

/** True when the row has at least one positive DC figure (peak kW, 10-80 % average kW or minutes). */
export function hasDcData(row: DcRow): boolean {
  return DC_FIGURE_KEYS.some((k) => positive(row[k]));
}

export function isDcDependent(key: string): key is DcDependentKey {
  return (DC_DEPENDENT_KEYS as readonly string[]).includes(key);
}

/** True when `key` must read as missing for this row (a DC-behaviour field on a car without DC data). */
export function hiddenForNoDc(row: DcRow, key: string): boolean {
  return isDcDependent(key) && !hasDcData(row);
}
