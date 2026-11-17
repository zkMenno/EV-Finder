// Charging network in numbers (T-061, Decision 012): public charging points over time and by
// power band, from each country's official open statistics (DE: Bundesnetzagentur, UK: DfT).
// Aggregates only, never charger locations. One chart = one definition_id. Static, server-only
// SVG (no JS); every chart has a data table, its source, licence and period. Linked from the
// "Find a charger / plan a trip" block.
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { parkedEnabled } from "@/config/features";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { LevelGate } from "@/components/LevelGate";
import { LineChart, type ChartSeries } from "@/components/LineChart";
import { Num } from "@/components/Num";
import { TermInfo } from "@/components/Term";
import { isCountrySlug, isServed } from "@/config/countries";
import { getT } from "@/i18n";
import {
  blockNotes,
  chargingBlocks,
  statProvenance,
  statSource,
  type DefinitionBlock,
  type StatPoint,
} from "@/lib/charging-stats";
import { chargingLinks } from "@/lib/charging-links";
import { creditFor } from "@/lib/credits";
import { ChargingLinks } from "@/components/ChargingLinks";
import { pageCtx, pageMeta, servedRoute, type PageCtx } from "../ev/_lib/context";

type Props = { params: Promise<{ country: string; lang: string }> };

const NERD = ["nerd"] as const;
const DETAILED = ["detailed", "nerd"] as const;
const linkCls = "text-blue-800 underline underline-offset-2 hover:text-blue-950";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const route = servedRoute(await params);
  if (!route) return {};
  return pageMeta(route, "charging", { title: getT(route.lang)("charging.stats.title") });
}

/** Chart labels drop the "Germany: " / "UK: " prefix of the taxonomy band labels (the page names the country). */
const shortLabel = (s: string) => s.replace(/^[^:]{1,20}:\s*/, "");

function dateLabel(locale: string, iso: string): string {
  return new Intl.DateTimeFormat(locale, {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(Date.parse(`${iso}T00:00:00Z`));
}

function StatNum({
  ctx,
  p,
  sources,
}: {
  ctx: PageCtx;
  p: StatPoint | undefined;
  sources: Record<string, string>;
}) {
  return (
    <Num
      value={p?.value}
      digits={0}
      provenance={p ? statProvenance(p.stat) : undefined}
      sources={sources}
      locale={ctx.locale}
      labels={ctx.labels}
      asOf={p?.stat.retrieved_at}
      focusable={false}
    />
  );
}

function DataTable({
  ctx,
  block,
  sources,
  caption,
}: {
  ctx: PageCtx;
  block: DefinitionBlock;
  sources: Record<string, string>;
  caption: string;
}) {
  const { t } = ctx;
  const cols = [...(block.total ? [block.total] : []), ...block.bands];
  const periods = [...new Set(cols.flatMap((c) => c.points.map((p) => p.period)))].sort().reverse();
  const at = (i: number, period: string) => cols[i]!.points.find((p) => p.period === period);
  return (
    <details className="mt-2">
      <summary className="cursor-pointer text-sm font-medium text-blue-800 underline underline-offset-2">
        {t("charging.stats.table")}
      </summary>
      <div className="mt-2 max-h-96 overflow-auto">
        <table className="w-full border-collapse text-sm" data-testid="charging-table">
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr className="border-b border-slate-300 text-left">
              <th scope="col" className="py-1 pr-3 font-semibold">
                {t("charging.stats.col.period")}
              </th>
              {cols.map((c) => (
                <th key={c.bandId ?? "all"} scope="col" className="py-1 pr-3 font-semibold">
                  {c.bandId ? c.label : t("charging.stats.col.all")}
                </th>
              ))}
              <LevelGate show={NERD}>
                <th scope="col" className="py-1 font-semibold">
                  {t("charging.stats.col.labels")}
                </th>
              </LevelGate>
            </tr>
          </thead>
          <tbody>
            {periods.map((period) => {
              return (
                <tr key={period} className="border-b border-slate-200 align-top">
                  <th scope="row" className="py-1 pr-3 text-left font-normal tabular-nums">
                    {dateLabel(ctx.locale, period)}
                  </th>
                  {cols.map((c, i) => (
                    <td key={c.bandId ?? "all"} className="py-1 pr-3">
                      <StatNum ctx={ctx} p={at(i, period)} sources={sources} />
                    </td>
                  ))}
                  <LevelGate show={NERD}>
                    <td className="py-1 text-xs text-slate-700">
                      {cols.map((c, i) => {
                        const s = at(i, period)?.stat;
                        return s?.source_label ? (
                          <span key={c.bandId ?? "all"} className="block">
                            <span lang={s.country === "DE" ? "de" : "en"}>{s.source_label}</span>
                          </span>
                        ) : null;
                      })}
                    </td>
                  </LevelGate>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </details>
  );
}

function Block({
  ctx,
  block,
  idx,
  sources,
  sourceLine,
}: {
  ctx: PageCtx;
  block: DefinitionBlock;
  idx: number;
  sources: Record<string, string>;
  sourceLine: ReactNode;
}) {
  const { t } = ctx;
  const id = `chg-${idx}`;
  const period = { from: dateLabel(ctx.locale, block.from), to: dateLabel(ctx.locale, block.to) };
  const fmt = new Intl.NumberFormat(ctx.locale, { maximumFractionDigits: 0 });
  const latest = (pts: StatPoint[]) => pts[pts.length - 1];
  const totalSeries: ChartSeries[] = block.total
    ? [{ label: t("charging.stats.col.all"), points: block.total.points }]
    : [];
  const bandSeries: ChartSeries[] = block.bands.map((b) => ({
    label: shortLabel(b.label),
    points: b.points,
  }));
  const summary = (series: ChartSeries[]) =>
    series
      .map((s) => {
        const p = s.points[s.points.length - 1]!;
        return t("charging.stats.summary", {
          label: s.label,
          value: fmt.format(p.value),
          date: dateLabel(ctx.locale, p.period),
        });
      })
      .join(" ");
  const last = block.total ? latest(block.total.points) : undefined;
  return (
    <section
      aria-labelledby={`${id}-h`}
      className="mt-8"
      data-testid="charging-block"
      data-definition={block.definitionId}
    >
      <h2 id={`${id}-h`} className="flex flex-wrap items-center gap-1 text-xl font-semibold">
        {block.metricLabel}
        <TermInfo term={ctx.tax.terms["charging-point"]} base={ctx.base} text={ctx.termText} />
      </h2>
      <p className="mt-1 text-sm text-slate-800">
        {block.definitionLabel}
        {block.definitionShort ? (
          <span className="block text-slate-700">{block.definitionShort}</span>
        ) : null}
      </p>
      {last ? (
        <p className="mt-2 text-lg" data-testid="charging-latest">
          <StatNum ctx={ctx} p={last} sources={sources} />{" "}
          <span className="text-sm text-slate-700">
            {t("charging.stats.asOf", { date: dateLabel(ctx.locale, last.period) })}
          </span>
        </p>
      ) : null}
      {totalSeries.length ? (
        <figure className="mt-3">
          <figcaption className="text-sm font-semibold">{t("charging.stats.overTime")}</figcaption>
          <LineChart
            id={`${id}-time`}
            title={`${block.metricLabel}: ${t("charging.stats.overTime")}`}
            summary={summary(totalSeries)}
            series={totalSeries}
            locale={ctx.locale}
            testId="charging-chart"
          />
        </figure>
      ) : null}
      {bandSeries.length ? (
        <figure className="mt-4">
          <figcaption className="flex items-center gap-1 text-sm font-semibold">
            {t("charging.stats.byBand")}
            <TermInfo term={ctx.tax.terms["power-band"]} base={ctx.base} text={ctx.termText} />
          </figcaption>
          <LineChart
            id={`${id}-band`}
            title={`${block.metricLabel}: ${t("charging.stats.byBand")}`}
            summary={summary(bandSeries)}
            series={bandSeries}
            locale={ctx.locale}
            testId="charging-chart"
          />
          <LevelGate show={DETAILED}>
            <ul className="mt-1 text-xs text-slate-700">
              {block.bands
                .filter((b) => b.short)
                .map((b) => (
                  <li key={b.bandId}>
                    {shortLabel(b.label)}: {b.short}
                  </li>
                ))}
            </ul>
          </LevelGate>
        </figure>
      ) : null}
      {blockNotes(block).length ? (
        <LevelGate show={DETAILED}>
          <div className="mt-2 max-w-3xl text-xs text-slate-700" data-testid="charging-notes">
            <p className="font-semibold">{t("charging.stats.col.notes")}</p>
            <ul className="list-disc pl-5">
              {blockNotes(block).map((n) => (
                <li key={n.note}>
                  {n.periods.map((p) => dateLabel(ctx.locale, p)).join(", ")}: {n.note}
                </li>
              ))}
            </ul>
          </div>
        </LevelGate>
      ) : null}
      <DataTable
        ctx={ctx}
        block={block}
        sources={sources}
        caption={`${block.metricLabel} (${block.definitionLabel}), ${period.from} – ${period.to}`}
      />
      <p className="mt-2 text-xs text-slate-700" data-testid="charging-source">
        {sourceLine} · {t("charging.stats.period", period)} ·{" "}
        {t("charging.stats.retrieved", { date: block.retrievedAt })}
      </p>
      <LevelGate show={NERD}>
        <p className="text-xs text-slate-700">
          {t("charging.stats.nerd.ids", {
            definition: block.definitionId,
            metric: block.metricId,
            unit: block.unit,
          })}
        </p>
      </LevelGate>
    </section>
  );
}

export default async function ChargingPage({ params }: Props) {
  const { country, lang } = await params;
  // Parked until after launch (Decision 051): CHARGING_PAGES=1 or PARKED=1.
  if (!isCountrySlug(country) || !isServed(country, lang) || !parkedEnabled("chargingPages")) notFound();
  const ctx = pageCtx(country, lang);
  const { t, cfg, base, cat } = ctx;
  const rel = cat.chargingStats();
  const blocks = chargingBlocks(rel, cfg.code, cat.taxonomy(), lang);

  const sourceFor = (id: string) => (rel ? statSource(rel, id) : undefined);
  const sourceNames: Record<string, string> = Object.fromEntries(
    blocks.map((b) => [b.sourceId, sourceFor(b.sourceId)?.name ?? b.sourceId]),
  );
  const sourceLine = (b: DefinitionBlock) => {
    const s = sourceFor(b.sourceId);
    if (!s) return <>{t("charging.stats.source", { source: b.sourceId })}</>;
    const c = creditFor(s);
    return (
      <>
        {t("charging.stats.source", { source: s.name })} ·{" "}
        {c.licenceUrl ? (
          <a href={c.licenceUrl} rel="noopener" className={linkCls}>
            {c.licenceLabel}
          </a>
        ) : (
          c.licenceLabel
        )}
        {c.lines.length ? ` · ${c.lines.join(" ")}` : ""}
      </>
    );
  };

  return (
    <>
      <Breadcrumbs
        label={t("crumb.label")}
        items={[{ label: t("crumb.home"), href: base }, { label: t("charging.stats.title") }]}
      />
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{t("charging.stats.title")}</h1>
      <p className="mt-2 max-w-3xl text-slate-800">
        {t("charging.stats.intro", { country: cfg.name })}
      </p>
      <p className="mt-1 max-w-3xl text-sm text-slate-700">{t("charging.stats.oneDefinition")}</p>
      {blocks.length ? (
        blocks.map((b, i) => (
          <Block
            key={`${b.metricId}-${b.definitionId}`}
            ctx={ctx}
            block={b}
            idx={i}
            sources={sourceNames}
            sourceLine={sourceLine(b)}
          />
        ))
      ) : (
        <p
          className="mt-6 max-w-3xl rounded-md border border-slate-300 p-4 text-slate-800"
          data-testid="charging-none"
        >
          {t("charging.stats.none", { country: cfg.name })}
        </p>
      )}
      <ChargingLinks links={chargingLinks(country, { lang })} t={t} />
    </>
  );
}
