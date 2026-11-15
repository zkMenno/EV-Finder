import type { PublishedVariant } from "@ev/schema";
import { describe, expect, it } from "vitest";
import { catalogue } from "@/test/helpers";
import { cellValue, differingCells, DIFF_KEYS, fieldsFor, rowDiffers, SPEC_FIELDS, specDiff, timelineOrder } from "./spec-diff";

function v(over: Partial<PublishedVariant> & { variant_id: string }): PublishedVariant {
  return {
    release: 1,
    variant_name: over.variant_id,
    generation_id: "g",
    generation_name: "G",
    model_id: "m",
    model_name: "M",
    make_id: "mk",
    make_name: "Make",
    year_start: 2020,
    era: "2018-20",
    quality_tier: "sourced",
    provenance: {},
    ...over,
  };
}

const field = (key: string) => SPEC_FIELDS.find((f) => f.key === key)!;

describe("spec fields", () => {
  it("have unique keys and every diff key exists", () => {
    const keys = SPEC_FIELDS.map((f) => f.key);
    expect(new Set(keys).size).toBe(keys.length);
    expect(fieldsFor(DIFF_KEYS)).toHaveLength(DIFF_KEYS.length);
  });
});

describe("cellValue", () => {
  it("rounds numbers to the field precision and keeps missing as null (never 0)", () => {
    expect(cellValue(v({ variant_id: "a", real_range_km: 412.6 }), field("real_range_km"))).toBe(413);
    expect(cellValue(v({ variant_id: "a", battery_kwh_net: 57.54 }), field("battery_kwh_net"))).toBe(57.5);
    expect(cellValue(v({ variant_id: "a" }), field("real_range_km"))).toBeNull();
    expect(cellValue(v({ variant_id: "a", real_range_km: null }), field("real_range_km"))).toBeNull();
  });
  it("text fields keep raw ids; booleans become strings", () => {
    expect(cellValue(v({ variant_id: "a", chemistry_id: "lfp" }), field("chemistry_id"))).toBe("lfp");
    expect(cellValue(v({ variant_id: "a", charge_100_daily: false }), field("charge_100_daily"))).toBe("false");
  });
  it("price is per country", () => {
    const r = v({ variant_id: "a", price_new: { DE: { amount: 42990, currency: "EUR" } } });
    expect(cellValue(r, field("price_new"), "DE")).toBe("EUR 42990");
    expect(cellValue(r, field("price_new"), "NL")).toBeNull();
  });
});

describe("specDiff", () => {
  it("orders columns by year and marks changes against the previous column", () => {
    const rows = [
      v({ variant_id: "late", year_start: 2022, battery_kwh_net: 77, drivetrain: "rwd" }),
      v({ variant_id: "early", year_start: 2020, battery_kwh_net: 58, drivetrain: "rwd" }),
      v({ variant_id: "mid", year_start: 2021, battery_kwh_net: 58, drivetrain: "awd" }),
    ];
    const d = specDiff(rows, fieldsFor(["battery_kwh_net", "drivetrain", "towing_kg"]));
    expect(d.columns.map((c) => c.variant_id)).toEqual(["early", "mid", "late"]);
    // towing_kg is missing everywhere → row dropped
    expect(d.rows.map((r) => r.field.key)).toEqual(["battery_kwh_net", "drivetrain"]);
    expect(d.rows[0]!.cells.map((c) => c.changed)).toEqual([false, false, true]);
    expect(d.rows[1]!.cells.map((c) => c.changed)).toEqual([false, true, true]);
    expect(d.rows.every((r) => r.changes)).toBe(true);
  });

  it("treats a value appearing or disappearing as a change", () => {
    const d = specDiff([v({ variant_id: "a", year_start: 2019 }), v({ variant_id: "b", year_start: 2020, ac_kw: 11 })], fieldsFor(["ac_kw"]));
    expect(d.rows[0]!.cells.map((c) => c.changed)).toEqual([false, true]);
  });

  it("works on a fixture generation", () => {
    const rows = catalogue.rows.filter((r) => r.generation_id === "hyundai-ioniq-5-ne");
    const d = specDiff(rows, fieldsFor(DIFF_KEYS));
    expect(d.columns).toHaveLength(3);
    const battery = d.rows.find((r) => r.field.key === "battery_kwh_net")!;
    expect(battery.changes).toBe(true);
  });

  it("timelineOrder puts open-ended variants last within a year", () => {
    const out = timelineOrder([v({ variant_id: "open", year_start: 2020, year_end: null }), v({ variant_id: "closed", year_start: 2020, year_end: 2021 })]);
    expect(out.map((r) => r.variant_id)).toEqual(["closed", "open"]);
  });
});

describe("differingCells (compare highlight)", () => {
  it("highlights nothing when all values agree", () => {
    expect(differingCells([1, 1, 1])).toEqual([false, false, false]);
    expect(differingCells([null, null])).toEqual([false, false]);
    expect(rowDiffers([5, 5])).toBe(false);
  });
  it("highlights both cells when two cars differ", () => {
    expect(differingCells([400, 450])).toEqual([true, true]);
  });
  it("highlights only the odd one out when a majority agrees", () => {
    expect(differingCells([400, 400, 450])).toEqual([false, false, true]);
    expect(differingCells(["lfp", "nmc", "nmc", "nmc"])).toEqual([true, false, false, false]);
  });
  it("highlights all when there is no clear majority", () => {
    expect(differingCells([1, 2, 3])).toEqual([true, true, true]);
    expect(differingCells([1, 1, 2, 2])).toEqual([true, true, true, true]);
  });
  it("counts a missing value as different", () => {
    expect(differingCells([11, 11, null])).toEqual([false, false, true]);
    expect(rowDiffers([11, null])).toBe(true);
  });
  it("a single column never differs", () => {
    expect(differingCells([3])).toEqual([false]);
  });
});

describe("EPA range (T-061)", () => {
  it("is its own range row next to WLTP, never the same value or field", () => {
    const keys = SPEC_FIELDS.filter((f) => f.group === "range").map((f) => f.key);
    expect(keys.indexOf("epa_range_km")).toBe(keys.indexOf("wltp_range_km") + 1);
    const r = v({ variant_id: "a", wltp_range_km: 357, epa_range_km: 297.7 });
    expect(cellValue(r, field("wltp_range_km"))).toBe(357);
    expect(cellValue(r, field("epa_range_km"))).toBe(298);
    expect(cellValue(v({ variant_id: "b", wltp_range_km: 357 }), field("epa_range_km"))).toBeNull();
  });
  it("is not part of the generation diff (WLTP stays the headline range)", () => {
    expect(DIFF_KEYS).not.toContain("epa_range_km");
  });
});
