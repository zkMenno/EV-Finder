// Rankings index (T-011).
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { COUNTRY_SLUGS, isCountrySlug } from "@/config/countries";
import { formatMoney } from "@/lib/format";
import { PRICE_THRESHOLD, RANKING_IDS } from "@/lib/rankings";
import { requestLang } from "@/lib/request-lang";
import { pageCtx } from "../ev/_lib/context";
import { getT } from "@/i18n";

type Props = { params: Promise<{ country: string }> };

export function generateStaticParams() {
  return COUNTRY_SLUGS.map((country) => ({ country }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { country } = await params;
  if (!isCountrySlug(country)) return {};
  return { title: getT(await requestLang(country))("top.title") };
}

export default async function TopIndex({ params }: Props) {
  const { country } = await params;
  if (!isCountrySlug(country)) notFound();
  const ctx = await pageCtx(country);
  const { t, cfg } = ctx;
  const price = formatMoney(PRICE_THRESHOLD[cfg.currency], cfg.currency, ctx.locale);

  return (
    <>
      <Breadcrumbs label={t("nav.main")} items={[{ label: t("crumb.home"), href: `/${country}` }, { label: t("crumb.top") }]} />
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{t("top.title")}</h1>
      <p className="mt-2 max-w-3xl text-slate-800">{t("top.intro")}</p>
      <ul className="mt-6 grid gap-4 md:grid-cols-3">
        {RANKING_IDS.map((id) => (
          <li key={id} className="flex flex-col gap-2 rounded-md border border-slate-300 p-4">
            <h2 className="text-lg font-semibold">
              <Link href={`/${country}/top/${id}`} className="text-blue-800 underline underline-offset-2 hover:text-blue-950">
                {t(`top.${id}.title`, { price })}
              </Link>
            </h2>
            <p className="text-sm text-slate-800">{t(`top.${id}.short`, { price, country: cfg.name })}</p>
          </li>
        ))}
      </ul>
    </>
  );
}
