// Rankings index (T-011).
import type { Metadata } from "next";
import Link from "next/link";
import { parkedEnabled } from "@/config/features";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { isCountrySlug, isServed } from "@/config/countries";
import { formatMoney } from "@/lib/format";
import { PRICE_THRESHOLD, RANKING_IDS } from "@/lib/rankings";
import { USED_CAP, visibleUsedRankings } from "@/lib/used-rankings";
import { pageCtx, pageMeta, servedRoute } from "../ev/_lib/context";
import { getT } from "@/i18n";

type Props = { params: Promise<{ country: string; lang: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const route = servedRoute(await params);
  if (!route) return {};
  return pageMeta(route, "top", { title: getT(route.lang)("top.title") });
}

export default async function TopIndex({ params }: Props) {
  const { country, lang } = await params;
  // Parked until after launch (Decision 051): RANKINGS=1 or PARKED=1.
  if (!isCountrySlug(country) || !isServed(country, lang) || !parkedEnabled("rankings")) notFound();
  const ctx = pageCtx(country, lang);
  const { base } = ctx;
  const { t, cfg } = ctx;
  const price = formatMoney(PRICE_THRESHOLD[cfg.currency], cfg.currency, ctx.locale);
  // Used-price lists only where enough generations have a sourced used price (none in release 1).
  const used = visibleUsedRankings(ctx.cat.rows(), ctx.cat.usedPrices(), cfg.code, cfg.currency);

  return (
    <>
      <Breadcrumbs label={t("crumb.label")} items={[{ label: t("crumb.home"), href: base }, { label: t("crumb.top") }]} />
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{t("top.title")}</h1>
      <p className="mt-2 max-w-3xl text-slate-800">{t("top.intro")}</p>
      <ul className="mt-6 grid gap-4 md:grid-cols-3">
        {RANKING_IDS.map((id) => (
          <li key={id} className="flex flex-col gap-2 rounded-md border border-slate-300 p-4">
            <h2 className="text-lg font-semibold">
              <Link href={`${base}/top/${id}`} className="text-blue-800 underline underline-offset-2 hover:text-blue-950">
                {t(`top.${id}.title`, { price })}
              </Link>
            </h2>
            <p className="text-sm text-slate-800">{t(`top.${id}.short`, { price, country: cfg.name })}</p>
          </li>
        ))}
        {used.map((id) => {
          const p = formatMoney(USED_CAP[id][cfg.currency], cfg.currency, ctx.locale);
          return (
            <li key={id} className="flex flex-col gap-2 rounded-md border border-slate-300 p-4" data-testid="used-ranking-link">
              <h2 className="text-lg font-semibold">
                <Link href={`${base}/top/${id}`} className="text-blue-800 underline underline-offset-2 hover:text-blue-950">
                  {t("top.used.title", { price: p })}
                </Link>
              </h2>
              <p className="text-sm text-slate-800">{t("top.used.short", { price: p, country: cfg.name, per: formatMoney(1000, cfg.currency, ctx.locale) })}</p>
            </li>
          );
        })}
      </ul>
    </>
  );
}
