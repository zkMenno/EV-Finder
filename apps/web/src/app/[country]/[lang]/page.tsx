import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { siteBase } from "@/lib/site-paths";
import { ChargingLinks } from "@/components/ChargingLinks";
import { Explore } from "@/components/Explore";
import { Hero } from "@/components/Hero";
import { showable } from "@/components/PriceBand";
import { COUNTRIES, isCountrySlug, isServed } from "@/config/countries";
import { tripFitEnabled } from "@/config/features";
import { getClientDict, getT } from "@/i18n";
import { clientCatalogueKey, getCatalogue } from "@/lib/catalogue";
import { chargingLinks } from "@/lib/charging-links";
import { sourceNames, toExploreRow } from "@/lib/explore-data";
import { applyFilters, sortRows } from "@/lib/filters";
import { financeProfile } from "@/lib/finance-profiles";
import { heroFromSearchParams } from "@/lib/hero-state";
import { article, articleTitle } from "@/lib/learn";
import { LISTING_SITES } from "@/lib/listings";
import { rankHero, resolveProfile, type UsedBands } from "@/lib/shortlist";
import { fromSearchParams, hasLevelParam, hasPayParam, hasViewParam } from "@/lib/state";
import { localizeTaxonomy } from "@/lib/taxonomy";
import { pageMeta, servedRoute } from "./ev/_lib/context";

/** Rows rendered on the server; the client takes over with the full list. */
const SSR_ROWS = 25;

type Props = {
  params: Promise<{ country: string; lang: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const route = servedRoute(await params);
  if (!route) return {};
  return pageMeta(route, "", { title: getT(route.lang)("hero.title") });
}

export default async function ExplorePage({ params, searchParams }: Props) {
  const { country, lang } = await params;
  if (!isCountrySlug(country) || !isServed(country, lang)) notFound();
  const cfg = COUNTRIES[country];
  const sp = await searchParams;
  const dict = getClientDict(lang);
  const t = getT(lang);

  const cat = getCatalogue();
  const all = cat.rows().map(toExploreRow);
  const state = fromSearchParams(sp);
  const tripFit = tripFitEnabled();
  // Flag off: the trip filter flag in a shared URL is dropped, so no hidden filter counts as active.
  if (!tripFit) state.filters.tripFit = false;
  const matches = sortRows(applyFilters(all, state.filters, cfg.code), state.sort, state.dir, cfg.code);

  // Hero (T-080): ranked on the server from the URL, re-ranked in the browser on every change.
  const hero = heroFromSearchParams(sp);
  const usedBands: UsedBands = {};
  for (const b of cat.usedPrices()) {
    if (b.country !== cfg.code || !showable(b, cfg.currency)) continue;
    (usedBands[b.generation_id] ??= []).push(b);
  }
  const nowYear = Number(cat.generatedAt().slice(0, 4)) || new Date().getFullYear();
  const profile = resolveProfile(hero.answers);
  const heroResult = profile
    ? rankHero(all, profile, {
        country: cfg.code,
        cond: hero.cond,
        budget: hero.budget,
        filters: hero.filters,
        presetsOff: hero.presetsOff,
        usedBands,
        nowYear,
      })
    : null;
  const makes = [...new Map(all.map((r) => [r.make_id, r.make_name])).entries()]
    .map(([id, name]) => ({ id, name }))
    .sort((a, b) => a.name.localeCompare(b.name));
  const tax = localizeTaxonomy(cat.taxonomy(), lang);
  const heroTerms = Object.fromEntries(
    ["real-range", "loan", "apr", "loan-term", "deposit", "total-cost-over-term", "used-price", "new-price"].map((id) => [id, tax.terms[id]]),
  );
  // Launch /learn pages linked from the hero (Decision 051), only those that exist.
  const learnLinks = ["winter-range", "charging-2026", "batteries", "battery-health", "chemistries"]
    .map((slug) => article(slug))
    .filter((a): a is NonNullable<typeof a> => !!a)
    .slice(0, 3)
    .map((a) => ({ slug: a.slug, title: articleTitle(a, lang), href: `${siteBase(country, lang)}/learn/${a.slug}` }));
  const dataUrl = `/data/catalogue-${clientCatalogueKey(cat)}.json`;

  return (
    <>
      <Hero
        country={country}
        code={cfg.code}
        currency={cfg.currency}
        lang={lang}
        dict={dict}
        base={siteBase(country, lang)}
        initial={hero}
        initialResult={heroResult}
        dataUrl={dataUrl}
        total={all.length}
        finance={financeProfile(cfg.code)}
        usedBands={usedBands}
        nowYear={nowYear}
        makes={makes}
        listingSites={[...LISTING_SITES[country]].sort((a, b) => a.priority - b.priority)}
        terms={heroTerms}
        learnLinks={learnLinks}
      />
      <section id="explore" aria-labelledby="explore-title" className="mt-12 scroll-mt-4">
        <h2 id="explore-title" className="text-2xl font-bold tracking-tight sm:text-3xl">
          {t("explore.title")}
        </h2>
        <p className="mb-6 mt-2 max-w-3xl text-slate-800">{t("explore.intro")}</p>
        <Explore
          country={country}
          code={cfg.code}
          currency={cfg.currency}
          lang={lang}
          dict={dict}
          initialState={state}
          viewFromUrl={hasViewParam(sp)}
          levelFromUrl={hasLevelParam(sp)}
          taxonomy={tax}
          asOf={cat.generatedAt().slice(0, 10)}
          initialRows={matches.slice(0, SSR_ROWS)}
          initialMatches={matches.length}
          total={all.length}
          dataUrl={dataUrl}
          sources={sourceNames(cat.sources())}
          tripFit={tripFit}
          finance={financeProfile(cfg.code)}
          payFromUrl={hasPayParam(sp)}
        />
      </section>
      <ChargingLinks links={chargingLinks(country, { lang })} t={t} statsHref={`${siteBase(country, lang)}/charging`} />
    </>
  );
}
