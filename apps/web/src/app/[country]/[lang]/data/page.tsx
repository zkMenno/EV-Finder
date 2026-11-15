// Open data download (Decision 016, T-090): the CC BY 4.0 bundle of the current release, linked
// from the release manifest (files live as release assets, Decision 035). Static server page.
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { isCountrySlug, isServed } from "@/config/countries";
import { siteName } from "@/config/site";
import { getT } from "@/i18n";
import { formatNumber, localeFor } from "@/lib/format";
import { openDataBundle } from "@/lib/open-data";
import { pageCtx, pageMeta, servedRoute } from "../ev/_lib/context";

type Props = { params: Promise<{ country: string; lang: string }> };

const CC_BY = "https://creativecommons.org/licenses/by/4.0/";
const linkCls = "text-blue-800 underline underline-offset-2 hover:text-blue-950";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const route = servedRoute(await params);
  if (!route) return {};
  return pageMeta(route, "data", { title: getT(route.lang)("opendata.title") });
}

function size(bytes: number, locale: string): string {
  if (bytes >= 1_000_000) return `${formatNumber(bytes / 1_000_000, locale, 1)} MB`;
  if (bytes >= 1_000) return `${formatNumber(bytes / 1_000, locale, 0)} KB`;
  return `${formatNumber(bytes, locale, 0)} B`;
}

export default async function OpenDataPage({ params }: Props) {
  const { country, lang } = await params;
  if (!isCountrySlug(country) || !isServed(country, lang)) notFound();
  const ctx = pageCtx(country, lang);
  const { t, base, cat } = ctx;
  const locale = localeFor(lang);
  const bundle = cat.origin() === "fixture" ? null : openDataBundle();
  const date = bundle?.generatedAt.slice(0, 10) || ctx.asOf;
  const cite = t("opendata.citeLine", { app: siteName, n: bundle?.release ?? "—", date });

  return (
    <>
      <Breadcrumbs label={t("crumb.label")} items={[{ label: t("crumb.home"), href: base }, { label: t("opendata.title") }]} />
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{t("opendata.title")}</h1>
      <p className="mt-2 max-w-3xl text-slate-800">{t("opendata.intro", { app: siteName })}</p>

      {bundle ? (
        <section aria-labelledby="od-files" className="mt-6 max-w-3xl" data-testid="open-data">
          <h2 id="od-files" className="text-xl font-semibold">
            {t("opendata.files", { n: bundle.release, date })}
          </h2>
          <ul className="mt-3 grid gap-3">
            {bundle.files.map((f) => (
              <li key={f.name} className="rounded-md border border-slate-300 p-3">
                <a href={f.url} rel="noopener" className={`${linkCls} font-semibold`} data-testid="open-file">
                  {f.name}
                </a>{" "}
                <span className="text-sm text-slate-700">· {size(f.bytes, locale)}</span>
                {t(`opendata.file.${f.name}` as Parameters<typeof t>[0]) !== `opendata.file.${f.name}` ? (
                  <p className="mt-1 text-sm text-slate-800">{t(`opendata.file.${f.name}` as Parameters<typeof t>[0])}</p>
                ) : null}
                <p className="mt-1 break-all font-mono text-xs text-slate-700">sha256 {f.sha256}</p>
              </li>
            ))}
          </ul>
          <p className="mt-2 text-sm text-slate-700">{t("opendata.hosted")}</p>
        </section>
      ) : (
        <p className="mt-6 text-slate-800" data-testid="open-data-none">
          {t("opendata.none")}
        </p>
      )}

      <section aria-labelledby="od-licence" className="mt-8 max-w-3xl">
        <h2 id="od-licence" className="text-xl font-semibold">
          {t("opendata.licence.title")}
        </h2>
        <p className="mt-2">
          {t("opendata.licence.body")}{" "}
          <a href={CC_BY} rel="noopener" className={linkCls}>
            CC BY 4.0
          </a>
        </p>
        <p className="mt-3 font-semibold">{t("opendata.cite.title")}</p>
        <blockquote className="mt-1 border-l-4 border-slate-300 pl-3 font-mono text-sm" data-testid="open-cite">
          {cite}
        </blockquote>
        <p className="mt-3 text-sm text-slate-800">{t("opendata.caveats")}</p>
        <p className="mt-3 text-sm">
          <Link href={`${base}/about`} className={linkCls}>
            {t("opendata.about")}
          </Link>
        </p>
      </section>
    </>
  );
}
