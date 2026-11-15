// Small hand-written SVG line chart (T-061): server component, no JS, no chart library.
// Colours come from the design tokens (--chart-1…4, --ink-2, --line), so it follows the
// Day trip / Night drive theme. Series differ by colour AND dash pattern (legend under the chart
// with the same swatch), and each line ends in its latest value (colour-blind safe). The SVG is role="img" with a text summary; pages put the
// exact figures in a data table next to it (the accessible fallback).
import { niceTicks, xLabels } from "@/lib/charging-stats";

export interface ChartSeries {
  label: string;
  points: { period: string; value: number }[];
}

const W = 640;
const H = 260;
const M = { top: 16, right: 64, bottom: 36, left: 64 };
const STROKES = [
  "stroke-[var(--chart-1)]",
  "stroke-[var(--chart-2)]",
  "stroke-[var(--chart-3)]",
  "stroke-[var(--chart-4)]",
];
const FILLS = [
  "fill-[var(--chart-1)]",
  "fill-[var(--chart-2)]",
  "fill-[var(--chart-3)]",
  "fill-[var(--chart-4)]",
];
const DASHES = [undefined, "6 4", "2 3", "10 3 2 3"];

const time = (p: string) => Date.parse(`${p.slice(0, 10)}T00:00:00Z`);

/** Spread end labels so they never overlap (min 14 px apart), keeping their order. */
function spread(ys: number[], gap = 14): number[] {
  const order = ys.map((y, i) => ({ y, i })).sort((a, b) => a.y - b.y);
  for (let k = 1; k < order.length; k++) order[k]!.y = Math.max(order[k]!.y, order[k - 1]!.y + gap);
  const out = [...ys];
  for (const o of order) out[o.i] = o.y;
  return out;
}

export function LineChart({
  id,
  title,
  summary,
  series,
  locale,
  testId,
}: {
  id: string;
  title: string;
  /** One or two sentences: what the chart shows and the latest values (screen readers). */
  summary: string;
  series: ChartSeries[];
  locale: string;
  testId?: string;
}) {
  const periods = [...new Set(series.flatMap((s) => s.points.map((p) => p.period)))].sort();
  if (!periods.length) return null;
  const t0 = time(periods[0]!);
  const t1 = time(periods[periods.length - 1]!);
  const max = Math.max(...series.flatMap((s) => s.points.map((p) => p.value)));
  const ticks = niceTicks(max);
  const yMax = ticks[ticks.length - 1]!;
  const pw = W - M.left - M.right;
  const ph = H - M.top - M.bottom;
  const x = (p: string) =>
    t1 === t0 ? M.left + pw / 2 : M.left + ((time(p) - t0) / (t1 - t0)) * pw;
  const y = (v: number) => M.top + ph - (v / yMax) * ph;
  const compact = new Intl.NumberFormat(locale, { notation: "compact", maximumFractionDigits: 1 });
  const many = periods.length > 8;
  const dateFmt = new Intl.DateTimeFormat(
    locale,
    many
      ? { year: "numeric", timeZone: "UTC" }
      : { month: "short", year: "numeric", timeZone: "UTC" },
  );
  const labels = xLabels(periods);
  const ends = series.map((s) => s.points[s.points.length - 1]);
  const endY = spread(ends.map((p) => (p ? y(p.value) : 0)));

  return (
    <>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-labelledby={`${id}-title ${id}-desc`}
        className="h-auto w-full max-w-3xl"
        data-testid={testId}
      >
        <title id={`${id}-title`}>{title}</title>
        <desc id={`${id}-desc`}>{summary}</desc>
        {ticks.map((v) => (
          <g key={v}>
            <line
              x1={M.left}
              x2={M.left + pw}
              y1={y(v)}
              y2={y(v)}
              className="stroke-[var(--line)]"
              strokeWidth={1}
            />
            <text
              x={M.left - 8}
              y={y(v)}
              dy="0.32em"
              textAnchor="end"
              className="fill-[var(--ink-2)] text-[11px]"
            >
              {compact.format(v)}
            </text>
          </g>
        ))}
        {labels.map((p) => (
          <text
            key={p}
            x={x(p)}
            y={H - M.bottom + 18}
            textAnchor="middle"
            className="fill-[var(--ink-2)] text-[11px]"
          >
            {dateFmt.format(time(p))}
          </text>
        ))}
        <line
          x1={M.left}
          x2={M.left + pw}
          y1={M.top + ph}
          y2={M.top + ph}
          className="stroke-[var(--line-strong)]"
          strokeWidth={1}
        />
        {series.map((s, i) => {
          const pts = s.points
            .map((p) => `${x(p.period).toFixed(1)},${y(p.value).toFixed(1)}`)
            .join(" ");
          const end = ends[i];
          return (
            <g key={s.label}>
              {s.points.length > 1 ? (
                <polyline
                  points={pts}
                  fill="none"
                  className={STROKES[i % 4]}
                  strokeWidth={2.5}
                  strokeDasharray={DASHES[i % 4]}
                  strokeLinejoin="round"
                />
              ) : null}
              {s.points.length <= 8
                ? s.points.map((p) => (
                    <circle
                      key={p.period}
                      cx={x(p.period)}
                      cy={y(p.value)}
                      r={3.5}
                      className={FILLS[i % 4]}
                    />
                  ))
                : null}
              {end ? (
                <text
                  x={x(end.period) + 8}
                  y={endY[i]}
                  dy="0.32em"
                  className="fill-[var(--ink)] text-[11px]"
                >
                  {compact.format(end.value)}
                </text>
              ) : null}
            </g>
          );
        })}
      </svg>
      {series.length > 1 ? (
        <ul className="mt-1 flex flex-wrap gap-x-5 gap-y-1 text-sm" data-testid="chart-legend">
          {series.map((s, i) => (
            <li key={s.label} className="flex items-center gap-2">
              <svg width="28" height="10" aria-hidden="true" className="shrink-0">
                <line
                  x1="1"
                  x2="27"
                  y1="5"
                  y2="5"
                  className={STROKES[i % 4]}
                  strokeWidth={2.5}
                  strokeDasharray={DASHES[i % 4]}
                />
              </svg>
              {s.label}
            </li>
          ))}
        </ul>
      ) : null}
    </>
  );
}
