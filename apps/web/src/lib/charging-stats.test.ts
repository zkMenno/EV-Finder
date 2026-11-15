import type { ChargingStat, ChargingStatsRelease, Taxonomy } from "@ev/schema";
import { describe, expect, it } from "vitest";
import {
  blockNotes,
  chargingBlocks,
  niceTicks,
  statProvenance,
  statSource,
  xLabels,
} from "./charging-stats";

const stat = (
  o: Partial<ChargingStat> & Pick<ChargingStat, "period_end" | "value">,
): ChargingStat => ({
  id: `x:${o.period_end}:${o.power_band_id ?? "all"}:${o.definition_id ?? "d1"}`,
  country: "DE",
  region: null,
  metric_id: "public-points",
  power_band_id: null,
  unit: "count",
  source_id: "bnetza-ladesaeulenregister",
  definition_id: "d1",
  confidence: "high",
  entered_by: "pipeline",
  retrieved_at: "2026-11-15",
  ...o,
});

const tax = {
  charging_definitions: [
    {
      id: "d1",
      label: { en: "Germany: registered points" },
      short: { en: "Official register." },
      counts: "point",
      source_id: "s",
    },
  ],
  charging_metrics: [
    { id: "public-points", label: { en: "Public charging points" }, unit: "count" },
  ],
  power_bands: [
    {
      id: "fast",
      label: { en: "Germany: fast" },
      current: "any",
      min_kw: 22.1,
      short: { en: "Above 22 kW." },
    },
    { id: "normal", label: { en: "Germany: normal" }, current: "any", min_kw: 0 },
  ],
} as unknown as Taxonomy;

const rel: ChargingStatsRelease = {
  release: 1,
  generated_at: "2026-11-15T00:00:00Z",
  sources: [
    {
      id: "bnetza",
      name: "BNetzA",
      licence: "CC-BY-4.0",
    } as ChargingStatsRelease["sources"][number],
  ],
  source_aliases: { "bnetza-ladesaeulenregister": "bnetza" },
  stats: [
    stat({ period_end: "2024-01-01", value: 100 }),
    stat({ period_end: "2023-01-01", value: 80 }),
    stat({ period_end: "2024-01-01", value: 30, power_band_id: "fast" }),
    stat({ period_end: "2024-01-01", value: 70, power_band_id: "normal" }),
    stat({ period_end: "2024-01-01", value: 5, region: "DE-BY" }),
    stat({ period_end: "2024-01-01", value: 999, country: "UK" }),
    stat({ period_end: "2025-01-01", value: 120, definition_id: "d2" }),
  ],
};

describe("chargingBlocks", () => {
  it("is empty without a release or for a country without stats", () => {
    expect(chargingBlocks(null, "DE", tax, "en")).toEqual([]);
    expect(chargingBlocks(rel, "FR", tax, "en")).toEqual([]);
  });

  it("never joins two definitions in one series (Decision 012)", () => {
    const b = chargingBlocks(rel, "DE", tax, "en");
    expect(b.map((x) => x.definitionId)).toEqual(["d1", "d2"]);
    expect(b[0]!.total!.points.map((p) => p.value)).toEqual([80, 100]);
    expect(b[1]!.total!.points.map((p) => p.value)).toEqual([120]);
  });

  it("uses whole-country figures only and one country", () => {
    const values = chargingBlocks(rel, "DE", tax, "en").flatMap((b) =>
      [...(b.total?.points ?? []), ...b.bands.flatMap((s) => s.points)].map((p) => p.value),
    );
    expect(values).not.toContain(5);
    expect(values).not.toContain(999);
  });

  it("labels from the taxonomy, bands from low to high power, period range", () => {
    const b = chargingBlocks(rel, "DE", tax, "en")[0]!;
    expect(b.metricLabel).toBe("Public charging points");
    expect(b.definitionShort).toBe("Official register.");
    expect(b.bands.map((s) => s.bandId)).toEqual(["normal", "fast"]);
    expect(b.bands[1]!.short).toBe("Above 22 kW.");
    expect([b.from, b.to]).toEqual(["2023-01-01", "2024-01-01"]);
  });
});

describe("statProvenance / statSource", () => {
  it("keeps the stat's own source, confidence and id", () => {
    const p = statProvenance(stat({ period_end: "2024-01-01", value: 1, notes: "break" }));
    expect(p).toMatchObject({ source_ids: ["bnetza-ladesaeulenregister"], confidence: "high" });
    expect(p.fact_ids?.[0]).toContain("2024-01-01");
  });
  it("lists each source note once with its periods", () => {
    const r = {
      ...rel,
      stats: [
        stat({ period_end: "2024-01-01", value: 1, notes: "n1" }),
        stat({ period_end: "2024-01-01", value: 2, power_band_id: "fast", notes: "n1" }),
        stat({ period_end: "2023-01-01", value: 3, notes: "n0" }),
      ],
    };
    const b = chargingBlocks(r, "DE", tax, "en")[0]!;
    expect(blockNotes(b)).toEqual([
      { note: "n0", periods: ["2023-01-01"] },
      { note: "n1", periods: ["2024-01-01"] },
    ]);
  });
  it("resolves a taxonomy source id through source_aliases", () => {
    expect(statSource(rel, "bnetza-ladesaeulenregister")?.name).toBe("BNetzA");
    expect(statSource(rel, "missing")).toBeUndefined();
  });
});

describe("axis helpers", () => {
  it("niceTicks starts at 0 and covers the maximum", () => {
    const t = niceTicks(218113);
    expect(t[0]).toBe(0);
    expect(t.at(-1)!).toBeGreaterThanOrEqual(218113);
    expect(t.length).toBeLessThanOrEqual(6);
    expect(niceTicks(0)).toEqual([0, 1]);
  });
  it("xLabels keeps few periods and thins many to one per year", () => {
    expect(xLabels(["2026-01-01", "2026-04-01"])).toEqual(["2026-01-01", "2026-04-01"]);
    const q = [
      "2017",
      "2018",
      "2019",
      "2020",
      "2021",
      "2022",
      "2023",
      "2024",
      "2025",
      "2026",
    ].flatMap((y) => ["01", "04", "07", "10"].map((m) => `${y}-${m}-01`));
    const l = xLabels(q);
    expect(l.length).toBeLessThanOrEqual(8);
    expect(l.every((p) => p.endsWith("-01-01"))).toBe(true);
  });
});
