// One ranking list (T-011), with a method note on the metric, its sources and estimate status.
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { Num } from "@/components/Num";
import { RankingTable } from "@/components/RankingTable";
import { COUNTRIES, COUNTRY_SLUGS, isCountrySlug } from "@/config/countries";
import { formatMoney, formatYears, localeFor } from "@/lib/format";
import { pagesT } from "@/lib/pages-i18n";
import { isRankingId, PRICE_THRESHOLD, ranking, RANKING_IDS, type RankEntry, type RankingId } from "@/lib/rankings";
import { requestLang } from "@/lib/request-lang";
import { pageCtx, sourcesFor, type PageCtx } from "../../ev/_lib/context";
import { generationTitle } from "../../ev/_lib/data";
import { generationHref, variantHref } from "../../ev/_lib/routes";

type Props = { params: Promise<{ country: string; list: string }> };

export function generateStaticParams() {
  return COUNTRY_SLUGS.flatMap((country) => RANKING_IDS.map((list) => ({ country, list })));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { country, list } = await params;
  if (!isCountrySlug(country) || !isRankingId(list)) return {};
  const lang = await requestLang(country);
  const cfg = COUNTRIES[country];
  return { title: pagesT(lang)(`top.${list}.title`, { price: formatMoney(PRICE_THRESHOLD[cfg.currency], cfg.currency, localeFor(lang)) }) };
}

const UNIT: Record<RankingId, string | undefined> = {
  "longest-real-range-under-30k": "km",
  "fastest-dc": "km",
  "most-available-nl": undefined,
};

function metricCell(ctx: PageCtx, e: RankEntry, unit: string | undefined) {
  const prov = e.row.provenance[e.field];
  const note =
    e.field === "real_range_km" && e.row.real_range_rung
      ? ctx.t(`rung.${e.row.real_range_rung}`)
      : undefined;
  return (
    <Num
      value={e.value}
      unit={unit}
      digits={0}
      provenance={prov}
      sources={sourcesFor(ctx, prov)}
      locale={ctx.locale}
      labels={ctx.labels}
      note={note}
      asOf={ctx.asOf}
    />
  );
}

export default async function RankingPage({ params }: Props) {
  const { country, list } = await params;
  if (!isCountrySlug(country) || !isRankingId(list)) notFound();
  const ctx = await pageCtx(country);
  const { t, pt, cfg } = ctx;
  const price = formatMoney(PRICE_THRESHOLD[cfg.currency], cfg.currency, ctx.locale);
  const title = pt(`top.${list}.title`, { price });
  const entries = ranking(list, ctx.cat.rows(), cfg.code, cfg.currency);
  const estimates = entries.filter((e) => e.estimate).length;
  const perGeneration = list === "most-available-nl";

  const headers = [
    perGeneration ? pt("top.most-available-nl.generation") : pt("top.car"),
    pt(`top.${list}.metric`),
    ...(list === "longest-real-range-under-30k" ? [pt("top.longest-real-range-under-30k.price")] : []),
  ];

  const rows = entries.map((e) => {
    const r = e.row;
    const years = formatYears(r.year_start, r.year_end, t("years.now"));
    const car = perGeneration ? (
      <span className="flex flex-col">
        <Link href={generationHref(country, r)} className="text-blue-800 underline underline-offset-2 hover:text-blue-950">
          {generationTitle(r)}
        </Link>
      </span>
    ) : (
      <span className="flex flex-col">
        <Link href={variantHref(country, r)} className="text-blue-800 underline underline-offset-2 hover:text-blue-950">
          {r.make_name} {r.model_name} {r.variant_name}
        </Link>
        <span className="text-xs font-normal text-slate-700">
          {r.generation_name} · <span className="tabular-nums">{years}</span>
        </span>
      </span>
    );
    const cells = [car, metricCell(ctx, e, UNIT[list])];
    if (list === "longest-real-range-under-30k") {
      const m = r.price_new?.[cfg.code];
      const prov = r.provenance[`price_new.${cfg.code}`];
      cells.push(
        <Num
          value={m?.amount}
          text={m ? formatMoney(m.amount, m.currency, ctx.locale) : undefined}
          provenance={prov}
          sources={sourcesFor(ctx, prov)}
          locale={ctx.locale}
          labels={ctx.labels}
          asOf={ctx.asOf}
        />,
      );
    }
    return { key: perGeneration ? r.generation_id : r.variant_id, rank: e.rank, cells };
  });

  const emptyText = list === "longest-real-range-under-30k" ? pt("top.longest-real-range-under-30k.empty") : pt("top.empty");

  return (
    <>
      <Breadcrumbs
        label={t("nav.main")}
        items={[{ label: pt("crumb.home"), href: `/${country}` }, { label: pt("crumb.top"), href: `/${country}/top` }, { label: title }]}
      />
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{title}</h1>
      <p className="mt-2 max-w-3xl text-slate-800">{pt(`top.${list}.short`, { price, country: cfg.name })}</p>

      <section aria-labelledby="method" className="mt-4 max-w-3xl rounded-md border border-slate-300 bg-slate-50 p-4">
        <h2 id="method" className="font-semibold">
          {pt("top.method")}
        </h2>
        <p className="mt-1 text-sm">{pt(`top.${list}.method`, { price, country: cfg.name })}</p>
        {entries.length && estimates ? (
          <p className="mt-2 text-sm font-medium" data-testid="estimate-note">
            {estimates === entries.length ? pt("top.allEstimates") : pt("top.estimates", { n: estimates, total: entries.length })}
          </p>
        ) : null}
      </section>

      <div className="mt-6">
        {rows.length ? (
          <RankingTable caption={pt("top.caption", { title })} rankHeader={pt("top.rank")} headers={headers} rows={rows} />
        ) : (
          <p className="rounded-md border border-slate-300 p-4" data-testid="ranking-empty">
            {emptyText}
          </p>
        )}
      </div>
    </>
  );
}
