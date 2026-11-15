// Learn pages: /learn/<slug> is either a /learn article (content/learn, rendered from the build-time
// tree in src/lib/learn.ts) or a glossary term (Decision 010). Article slugs and glossary ids never
// clash (the content validator guarantees it); an article wins if they ever did. Static.
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ChargingLinks } from "@/components/ChargingLinks";
import { isCountrySlug, isServed } from "@/config/countries";
import { getT } from "@/i18n";
import { getCatalogue } from "@/lib/catalogue";
import { chargingLinks } from "@/lib/charging-links";
import { siteBase } from "@/lib/site-paths";
import { loc, localizeTaxonomy } from "@/lib/taxonomy";
import { LearnBlocks, type LearnTerm } from "@/components/LearnArticle";
import { article, articleFile, articles, articleTitle } from "@/lib/learn";
import type { Lang } from "@/config/countries";
import { pageMeta, servedRoute } from "../../ev/_lib/context";

type Props = { params: Promise<{ country: string; lang: string; term: string }> };

function findTerm(id: string) {
  return getCatalogue().taxonomy().glossary_terms.find((g) => g.id === id);
}

/** One static page per glossary term and served country × language (pairs come from the layout). */
export function generateStaticParams() {
  const ids = new Set([...getCatalogue().taxonomy().glossary_terms.map((g) => g.id), ...articles().map((a) => a.slug)]);
  return [...ids].map((term) => ({ term }));
}

/** Tooltip data for every id an article may use: glossary terms, chemistries, voltage classes. */
function learnTerms(lang: Lang, base: string): Record<string, LearnTerm> {
  const tax = getCatalogue().taxonomy();
  const ui = localizeTaxonomy(tax, lang);
  const out: Record<string, LearnTerm> = {};
  for (const c of ui.chemistries) out[c.id] = { label: c.label, short: c.explainer ?? "", href: `${base}/learn/chemistry` };
  for (const v of ui.voltageClasses) out[v.id] = { label: v.label, short: v.explainer ?? "", href: `${base}/learn/voltage-class` };
  for (const g of Object.values(ui.terms)) out[g.id] = { label: g.label, short: g.short, href: `${base}/learn/${g.id}` };
  return out;
}

function ArticlePage({ slug, lang, base, t, country }: { slug: string; lang: Lang; base: string; t: ReturnType<typeof getT>; country: Parameters<typeof chargingLinks>[0] }) {
  const a = article(slug)!;
  const f = articleFile(a, lang)!;
  const linkCls = "text-blue-800 underline underline-offset-2 hover:text-blue-950";
  return (
    <article className="max-w-3xl" lang={f.lang} data-testid="learn-article">
      <p className="mb-4 text-sm">
        <Link href={`${base}/learn`} className={linkCls}>
          ← {t("learn.all")}
        </Link>
      </p>
      {f.file.review === "needed" ? (
        <p className="mb-4 rounded-md border border-amber-700 bg-amber-50 p-3 text-sm" role="note" data-testid="learn-draft">
          <strong>{t("learn.draft")}.</strong> {t("learn.draft.help")}
        </p>
      ) : null}
      {f.fallback ? (
        <p className="mb-4 rounded-md border border-slate-400 p-3 text-sm" lang={lang} data-testid="learn-fallback">
          {t("learn.fallback")}
        </p>
      ) : null}
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{f.file.title}</h1>
      {f.file.updated ? <p className="mt-1 text-sm text-slate-700">{t("learn.updated", { date: f.file.updated })}</p> : null}
      <LearnBlocks
        blocks={f.file.blocks}
        ctx={{ terms: learnTerms(lang, base), termText: { about: t("term.about"), learnMore: t("term.learnMore") }, newTab: t("learn.newTab") }}
      />
      {f.file.sources.length ? (
        <section className="mt-10" aria-labelledby="learn-sources">
          <h2 id="learn-sources" className="text-lg font-semibold">
            {t("learn.sources")}
          </h2>
          <ol className="mt-2 flex list-decimal flex-col gap-1 pl-5 text-sm" data-testid="learn-sources">
            {f.file.sources.map((s) => (
              <li key={s.url}>
                <a href={s.url} rel="noopener nofollow" target="_blank" className={`break-words ${linkCls}`}>
                  {s.title}
                </a>
                {s.retrieved ? <span className="text-slate-700"> · {t("learn.retrieved", { date: s.retrieved })}</span> : null}
              </li>
            ))}
          </ol>
        </section>
      ) : null}
      <ChargingLinks links={chargingLinks(country, { lang })} t={t} statsHref={`${base}/charging`} />
    </article>
  );
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const p = await params;
  const route = servedRoute(p);
  if (!route) return {};
  const a = article(p.term);
  if (a) return pageMeta(route, `learn/${a.slug}`, { title: articleTitle(a, route.lang) });
  const g = findTerm(p.term);
  if (!g) return {};
  return pageMeta(route, `learn/${g.id}`, { title: loc(g.label, route.lang) });
}

export default async function LearnPage({ params }: Props) {
  const { country, lang, term } = await params;
  if (!isCountrySlug(country) || !isServed(country, lang)) notFound();
  if (article(term)) return <ArticlePage slug={term} lang={lang} base={siteBase(country, lang)} t={getT(lang)} country={country} />;
  const g = findTerm(term);
  if (!g) notFound();
  const t = getT(lang);
  const base = siteBase(country, lang);
  // `related` may point at glossary terms or at chemistry / cooling / voltage-class rows.
  const tax = getCatalogue().taxonomy();
  const terms = new Map(tax.glossary_terms.map((x) => [x.id, { label: x.label, href: `${base}/learn/${x.id}` }]));
  const rows = [...tax.chemistries.map((x) => ({ x, term: "chemistry" })), ...tax.cooling_types.map((x) => ({ x, term: "cooling" })), ...tax.voltage_classes.map((x) => ({ x, term: "voltage-class" }))];
  for (const { x, term: parent } of rows) if (!terms.has(x.id)) terms.set(x.id, { label: x.label, href: `${base}/learn/${parent}` });
  const related = (g.related ?? []).flatMap((id) => {
    const r = terms.get(id);
    return r ? [{ id, ...r }] : [];
  });

  return (
    <article className="max-w-2xl">
      <p className="mb-4 text-sm">
        <Link href={base} className="text-blue-800 underline underline-offset-2">
          ← {t("learn.back")}
        </Link>
      </p>
      <h1 className="text-2xl font-bold tracking-tight">{loc(g.label, lang)}</h1>
      {g.technical ? <p className="text-slate-700">{loc(g.technical, lang)}</p> : null}
      <p className="mt-4 text-lg">{loc(g.short, lang)}</p>
      {g.long ? <p className="mt-4">{loc(g.long, lang)}</p> : null}
      {g.nerd_note ? (
        <section className="mt-6 rounded-md border border-slate-300 bg-slate-50 p-4">
          <h2 className="font-semibold">{t("learn.nerd")}</h2>
          <p className="mt-1 text-sm">{loc(g.nerd_note, lang)}</p>
        </section>
      ) : null}
      {related.length ? (
        <section className="mt-6">
          <h2 className="font-semibold">{t("learn.related")}</h2>
          <ul className="mt-1 list-disc pl-5">
            {related.map((r) => (
              <li key={r.id}>
                <Link href={r.href} className="text-blue-800 underline underline-offset-2">
                  {loc(r.label, lang)}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      <ChargingLinks links={chargingLinks(country, { lang })} t={t} statsHref={`${base}/charging`} />
    </article>
  );
}
