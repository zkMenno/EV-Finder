import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ChargingLinks } from "@/components/ChargingLinks";
import { Explore } from "@/components/Explore";
import { COUNTRIES, isCountrySlug } from "@/config/countries";
import { tripFitEnabled } from "@/config/features";
import { getClientDict, getT } from "@/i18n";
import { clientCatalogueKey, getCatalogue } from "@/lib/catalogue";
import { chargingLinks } from "@/lib/charging-links";
import { sourceNames, toExploreRow } from "@/lib/explore-data";
import { applyFilters, sortRows } from "@/lib/filters";
import { requestLang } from "@/lib/request-lang";
import { fromSearchParams, hasLevelParam, hasViewParam } from "@/lib/state";
import { localizeTaxonomy } from "@/lib/taxonomy";

/** Rows rendered on the server; the client takes over with the full list. */
const SSR_ROWS = 25;

type Props = {
  params: Promise<{ country: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { country } = await params;
  if (!isCountrySlug(country)) return {};
  const t = getT(await requestLang(country));
  return { title: t("explore.title") };
}

export default async function ExplorePage({ params, searchParams }: Props) {
  const { country } = await params;
  if (!isCountrySlug(country)) notFound();
  const cfg = COUNTRIES[country];
  const sp = await searchParams;
  const lang = await requestLang(country);
  const dict = getClientDict(lang);
  const t = getT(lang);

  const cat = getCatalogue();
  const all = cat.rows().map(toExploreRow);
  const state = fromSearchParams(sp);
  const tripFit = tripFitEnabled();
  // Flag off: the trip filter flag in a shared URL is dropped, so no hidden filter counts as active.
  if (!tripFit) state.filters.tripFit = false;
  const matches = sortRows(applyFilters(all, state.filters, cfg.code), state.sort, state.dir, cfg.code);

  return (
    <>
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{t("explore.title")}</h1>
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
        taxonomy={localizeTaxonomy(cat.taxonomy(), lang)}
        asOf={cat.generatedAt().slice(0, 10)}
        initialRows={matches.slice(0, SSR_ROWS)}
        initialMatches={matches.length}
        total={all.length}
        dataUrl={`/data/catalogue-${clientCatalogueKey(cat)}.json`}
        sources={sourceNames(cat.sources())}
        tripFit={tripFit}
      />
      <ChargingLinks links={chargingLinks(country)} t={t} />
    </>
  );
}
