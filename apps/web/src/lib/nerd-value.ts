// The Value column of the hero's Nerd score table (T-097): the car's own figure in buyer units
// ("387 km in 20 min"), not the factor's internal scoring value (raw × scale, e.g. km/h).
// Pure and client-safe, so the unit wording is testable without rendering the hero.
import type { MsgKey, T } from "@/i18n/t";
import { formatNumber } from "./format";
import type { FactorView } from "./shortlist";

/** Unit message (with `{v}`) and max fraction digits per numeric rule field. */
const NUMERIC: Record<string, { key: MsgKey; digits: number; div?: number }> = {
  dc_km_per_20min: { key: "hero.nerd.unit.dc_km_per_20min", digits: 0 },
  real_range_km: { key: "hero.nerd.unit.real_range_km", digits: 0 },
  // The release's own winter estimate (−10 °C) and real efficiency, as the release scores them (T-114).
  winter_range_km: { key: "hero.nerd.unit.winter_range_km", digits: 0 },
  real_wh_km: { key: "hero.nerd.unit.real_wh_km", digits: 0 },
  boot_l: { key: "hero.nerd.unit.boot_l", digits: 0 },
  consumption_kwh_100km: { key: "hero.nerd.unit.consumption_kwh_100km", digits: 1 },
  ac_kw: { key: "hero.nerd.unit.ac_kw", digits: 1 },
  // Length in metres, as the card's own "why" line says it ("4,25 m long").
  length_mm: { key: "hero.nerd.unit.length_mm", digits: 2, div: 1000 },
};

/** Text values (heat pump, cooling) with a label; anything else shows as written. */
const WORDS: Record<string, MsgKey> = {
  standard: "hero.nerd.val.standard",
  option: "hero.nerd.val.option",
  none: "hero.nerd.val.none",
  liquid: "hero.nerd.val.liquid",
  refrigerant: "hero.nerd.val.refrigerant",
  air: "hero.nerd.val.air",
  passive: "hero.nerd.val.passive",
};

export function nerdValue(f: Pick<FactorView, "field" | "raw">, t: T, locale: string): string {
  if (f.raw === null) return t("hero.card.notKnown");
  if (typeof f.raw === "boolean") return t(f.raw ? "hero.nerd.val.yes" : "hero.nerd.val.no");
  if (typeof f.raw === "number") {
    const u = f.field ? NUMERIC[f.field] : undefined;
    // A field without a unit entry still shows its own figure, never the scaled one.
    return u ? t(u.key, { v: formatNumber(f.raw / (u.div ?? 1), locale, u.digits) }) : formatNumber(f.raw, locale, 1);
  }
  const w = WORDS[f.raw];
  return w ? t(w) : f.raw;
}

/**
 * Splits a value into number and word parts, so the Value cell can let words break when a
 * narrow card or a wider system font needs it while every number stays whole ("1.161,6", "4,25").
 */
export function numberParts(text: string): { text: string; num: boolean }[] {
  return text
    .split(/(\d[\d.,\u202f\u00a0]*\d|\d)/)
    .filter((s) => s !== "")
    .map((s) => ({ text: s, num: /^\d/.test(s) }));
}
