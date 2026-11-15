// Model overview (T-009): its generations with years, honest "years not yet checked" flag.
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { Num } from "@/components/Num";
import { TermInfo } from "@/components/Term";
import { isCountrySlug } from "@/config/countries";
import { getCatalogue } from "@/lib/catalogue";
import { formatYears } from "@/lib/format";
import { pageCtx, sourcesFor } from "../../_lib/context";
import { firstWith, groupGenerations, withCountries } from "../../_lib/data";
import { generationHref, modelParams, modelRows } from "../../_lib/routes";

type Props = { params: Promise<{ country: string; make: string; model: string }> };

export function generateStaticParams() {
  return withCountries(modelParams(getCatalogue().rows()));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { make, model } = await params;
  const r = modelRows(getCatalogue().rows(), make, model)[0];
  return r ? { title: `${r.make_name} ${r.model_name}` } : {};
}

export default async function ModelPage({ params }: Props) {
  const { country, make, model } = await params;
  if (!isCountrySlug(country)) notFound();
  const ctx = await pageCtx(country);
  const rows = modelRows(ctx.cat.rows(), make, model);
  const first = rows[0];
  if (!first) notFound();
  const { t } = ctx;
  const rdwTerm = ctx.tax.terms["registrations-nl"];
  const gens = groupGenerations(ctx.cat, rows);
  const name = `${first.make_name} ${first.model_name}`;

  return (
    <>
      <Breadcrumbs label={t("nav.main")} items={[{ label: t("crumb.home"), href: `/${country}` }, { label: name }]} />
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{name}</h1>
      <p className="mt-2 text-slate-800">
        {gens.length === 1
          ? t("model.intro.one", { variants: rows.length })
          : t("model.intro", { generations: gens.length, variants: rows.length })}
      </p>

      <h2 className="mt-8 text-xl font-semibold">{t("model.generations")}</h2>
      <ul className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {gens.map((g) => {
          const rdw = firstWith(g.rows, "registered_count_nl");
          return (
            <li key={g.id} className="flex flex-col gap-2 rounded-md border border-slate-300 p-4">
              <h3 className="text-lg font-semibold">
                <Link href={generationHref(country, g.rows[0]!)} className="text-blue-800 underline underline-offset-2 hover:text-blue-950">
                  {g.name}
                </Link>
              </h3>
              <p className="text-sm">
                <span className="sr-only">{t("years.label")}: </span>
                <span className="tabular-nums">{formatYears(g.yearStart, g.yearEnd, t("years.now"))}</span>
                {g.uncertain ? (
                  <span className="ml-2 rounded border border-amber-700 px-1 text-xs text-amber-900" title={t("years.unchecked.help")}>
                    {t("years.unchecked")}
                  </span>
                ) : null}
              </p>
              <p className="text-sm text-slate-800">{t("model.variants", { n: g.rows.length })}</p>
              {rdw ? (
                <p className="text-sm">
                  <Num
                    value={rdw.registered_count_nl}
                    digits={0}
                    provenance={rdw.provenance.registered_count_nl}
                    sources={sourcesFor(ctx, rdw.provenance.registered_count_nl)}
                    locale={ctx.locale}
                    labels={ctx.labels}
                    asOf={ctx.asOf}
                  />{" "}
                  {t("gen.rdw")}
                  <TermInfo term={rdwTerm} country={country} text={ctx.termText} />
                </p>
              ) : null}
            </li>
          );
        })}
      </ul>
    </>
  );
}
