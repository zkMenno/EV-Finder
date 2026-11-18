// The optional bigger on-board AC charger (T-063, field `ac_kw_optional`): shown next to the
// standard one as "7.4 kW (11 kW optional)". Pure, safe anywhere.
import type { PublishedVariant } from "@ev/schema";

/** The optional AC power to show next to `ac_kw`, or null: only a real number above the standard one. */
export function acOptionalKw(row: Pick<PublishedVariant, "ac_kw" | "ac_kw_optional">): number | null {
  const std = row.ac_kw;
  const opt = row.ac_kw_optional;
  if (typeof opt !== "number" || !Number.isFinite(opt) || opt <= 0) return null;
  if (typeof std === "number" && Number.isFinite(std) && opt <= std) return null;
  return opt;
}
