// Public charging statistics for the charging page (T-061, Decision 012: aggregates only).
// Pure logic, no React. A chart draws exactly one definition_id: a definition change starts a new
// series (and a new chart), never a joined line. Whole-country figures only (region = null).
import type {
  ChargingStat,
  ChargingStatsRelease,
  Country,
  FieldProvenance,
  Source,
  Taxonomy,
} from "@ev/schema";
import type { Lang } from "@/config/countries";
import { loc } from "./taxonomy";

export interface StatPoint {
  period: string;
  value: number;
  stat: ChargingStat;
}

export interface StatSeries {
  /** power_bands id, or null = all bands. */
  bandId: string | null;
  label: string;
  short?: string;
  points: StatPoint[];
}

/** One chart's worth of data: one metric, one definition. */
export interface DefinitionBlock {
  definitionId: string;
  definitionLabel: string;
  definitionShort?: string;
  metricId: string;
  metricLabel: string;
  unit: string;
  sourceId: string;
  /** All bands together, over time (may be empty when a source only gives bands). */
  total: StatSeries | null;
  /** Per power band, over time (bands of this definition only). */
  bands: StatSeries[];
  /** First and last period across total + bands. */
  from: string;
  to: string;
  retrievedAt: string;
}

/** Metrics drawn on the page, in order: all public points first, then DC-only counts. */
export const CHART_METRICS = ["public-points", "public-points-dc"] as const;

const byPeriod = (a: StatPoint, b: StatPoint) => a.period.localeCompare(b.period);

/**
 * The page's chart blocks for one country. A metric that has no total and no bands is skipped.
 * Per metric, one block per definition_id, oldest definition first (by first period).
 */
export function chargingBlocks(
  rel: ChargingStatsRelease | null,
  country: Country,
  tax: Taxonomy,
  lang: Lang,
): DefinitionBlock[] {
  if (!rel) return [];
  const stats = rel.stats.filter(
    (s) => s.country === country && (s.region ?? null) === null && Number.isFinite(s.value),
  );
  const defs = new Map((tax.charging_definitions ?? []).map((d) => [d.id, d]));
  const metrics = new Map((tax.charging_metrics ?? []).map((m) => [m.id, m]));
  const bands = new Map((tax.power_bands ?? []).map((b) => [b.id, b]));
  const out: DefinitionBlock[] = [];
  for (const metricId of CHART_METRICS) {
    const forMetric = stats.filter((s) => s.metric_id === metricId);
    const defIds = [...new Set(forMetric.map((s) => s.definition_id))];
    const blocks: DefinitionBlock[] = [];
    for (const definitionId of defIds) {
      const rows = forMetric.filter((s) => s.definition_id === definitionId);
      const series = new Map<string | null, StatPoint[]>();
      for (const s of rows) {
        const k = s.power_band_id ?? null;
        series.set(k, [
          ...(series.get(k) ?? []),
          { period: s.period_end, value: s.value, stat: s },
        ]);
      }
      const total = series.get(null)?.sort(byPeriod) ?? [];
      const bandSeries: StatSeries[] = [...series.entries()]
        .filter(([k]) => k !== null)
        .map(([k, pts]) => {
          const b = bands.get(k!);
          const short = b?.short ? loc(b.short, lang) : "";
          return {
            bandId: k,
            label: b ? loc(b.label, lang) : k!,
            ...(short ? { short } : {}),
            points: pts.sort(byPeriod),
          };
        })
        // Lower power bands first (taxonomy min_kw), unknown bands last.
        .sort(
          (a, b) =>
            (bands.get(a.bandId!)?.min_kw ?? Infinity) - (bands.get(b.bandId!)?.min_kw ?? Infinity),
        );
      const all = [...total, ...bandSeries.flatMap((s) => s.points)].sort(byPeriod);
      if (!all.length) continue;
      const d = defs.get(definitionId);
      const m = metrics.get(metricId);
      const dShort = d?.short ? loc(d.short, lang) : "";
      blocks.push({
        definitionId,
        definitionLabel: d ? loc(d.label, lang) : definitionId,
        ...(dShort ? { definitionShort: dShort } : {}),
        metricId,
        metricLabel: m ? loc(m.label, lang) : metricId,
        unit: all[0]!.stat.unit,
        sourceId: all[0]!.stat.source_id,
        total: total.length
          ? { bandId: null, label: m ? loc(m.label, lang) : metricId, points: total }
          : null,
        bands: bandSeries,
        from: all[0]!.period,
        to: all[all.length - 1]!.period,
        retrievedAt: all
          .map((p) => p.stat.retrieved_at)
          .sort()
          .at(-1)!,
      });
    }
    out.push(...blocks.sort((a, b) => a.from.localeCompare(b.from)));
  }
  return out;
}

/**
 * Provenance for one figure (each stat carries its own source and date). Source notes are long
 * paragraphs, so they are listed once per chart (blockNotes), not repeated on every number.
 */
export function statProvenance(s: ChargingStat): FieldProvenance {
  return {
    source_ids: [s.source_id],
    confidence: s.confidence,
    fact_ids: [s.id],
    agreeing_sources: 1,
  };
}

/** Distinct source notes in a block, with the periods they apply to (oldest first). */
export function blockNotes(b: DefinitionBlock): { note: string; periods: string[] }[] {
  const by = new Map<string, Set<string>>();
  for (const p of [...(b.total?.points ?? []), ...b.bands.flatMap((s) => s.points)]) {
    if (!p.stat.notes) continue;
    by.set(p.stat.notes, (by.get(p.stat.notes) ?? new Set()).add(p.period));
  }
  return [...by.entries()]
    .map(([note, ps]) => ({ note, periods: [...ps].sort() }))
    .sort((a, b) => a.periods[0]!.localeCompare(b.periods[0]!));
}

/** The release source behind a stat's source_id (taxonomy id or its registry alias). */
export function statSource(rel: ChargingStatsRelease, sourceId: string): Source | undefined {
  return (
    rel.sources.find((s) => s.id === sourceId) ??
    rel.sources.find((s) => s.id === rel.source_aliases?.[sourceId])
  );
}

/** "Nice" axis maximum and ticks from 0 (1, 2, 2.5, 5 × 10^n steps). Exported for tests. */
export function niceTicks(max: number, count = 4): number[] {
  if (!(max > 0)) return [0, 1];
  const raw = max / count;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw)!;
  const ticks: number[] = [];
  for (let v = 0; v < max + step * 0.999; v += step) ticks.push(Math.round(v * 1e6) / 1e6);
  return ticks;
}

/** Periods (ISO dates) on the x axis: one label per year when there are many, else every period. */
export function xLabels(periods: string[], maxLabels = 8): string[] {
  if (periods.length <= maxLabels) return periods;
  const years = [...new Set(periods.map((p) => p.slice(0, 4)))];
  const firsts = years.map((y) => periods.find((p) => p.startsWith(y))!);
  const every = Math.ceil(firsts.length / maxLabels);
  return firsts.filter((_, i) => i % every === 0);
}
