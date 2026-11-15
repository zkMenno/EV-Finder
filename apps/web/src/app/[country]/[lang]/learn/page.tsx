// /learn index: guides from content/learn/index.yaml, then every glossary term A–Z. Static.
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { isCountrySlug, isServed } from "@/config/countries";
import { getT } from "@/i18n";
import { getCatalogue } from "@/lib/catalogue";
import { articleFile, articles, articleTitle } from "@/lib/learn";
import { siteBase } from "@/lib/site-paths";
import { loc } from "@/lib/taxonomy";
import { pageMeta, servedRoute } from "../ev/_lib/context";

type Props = { params: Promise<{ country: string; lang: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const route = servedRoute(await params);
  return route ? pageMeta(route, "learn", { title: getT(route.lang)("learn.index.title") }) : {};
}

export default async function LearnIndex({ params }: Props) {
  const { country, lang } = await params;
  if (!isCountrySlug(country) || !isServed(country, lang)) notFound();
  const t = getT(lang);
  const base = siteBase(country, lang);
  const terms = [...getCatalogue().taxonomy().glossary_terms].map((g) => ({ id: g.id, label: loc(g.label, lang) })).sort((a, b) => a.label.localeCompare(b.label, lang));
  const linkCls = "text-blue-800 underline underline-offset-2 hover:text-blue-950";
  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold tracking-tight">{t("learn.index.title")}</h1>
      <p className="mt-2 text-slate-800">{t("learn.index.intro")}</p>
      <h2 className="mt-8 text-xl font-semibold">{t("learn.articles")}</h2>
      <ul className="mt-3 flex flex-col gap-2" data-testid="learn-articles">
        {articles().map((a) => {
          const f = articleFile(a, lang);
          return (
            <li key={a.slug}>
              <Link href={`${base}/learn/${a.slug}`} className={`font-medium ${linkCls}`}>
                {articleTitle(a, lang)}
              </Link>
              {f?.file.review === "needed" ? <span className="ml-2 rounded border border-amber-700 px-1 text-xs text-amber-900">{t("learn.draft")}</span> : null}
            </li>
          );
        })}
      </ul>
      <h2 className="mt-8 text-xl font-semibold">{t("learn.glossary")}</h2>
      <ul className="mt-3 columns-1 gap-6 sm:columns-2" data-testid="learn-terms">
        {terms.map((g) => (
          <li key={g.id} className="mb-1">
            <Link href={`${base}/learn/${g.id}`} className={linkCls}>
              {g.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
