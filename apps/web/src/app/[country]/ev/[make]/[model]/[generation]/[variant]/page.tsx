// Variant page (T-009): full spec sheet in groups, every number through <Num>; compare + heart.
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ChargingLinks } from "@/components/ChargingLinks";
import { abrpLink, chargingLinks } from "@/lib/charging-links";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { PriceBand } from "@/components/PriceBand";
import { SeeListings } from "@/components/SeeListings";
import { isCountrySlug } from "@/config/countries";
import { getCatalogue } from "@/lib/catalogue";
import { COMPARE_MAX } from "@/lib/compare-store";
import { formatYears } from "@/lib/format";
import { seeListings } from "@/lib/listings";
import { SPEC_FIELDS, SPEC_GROUPS, timelineOrder } from "@/lib/spec-diff";
import { Registrations } from "../../../../_components/Registrations";
import { FieldLabel, SpecValue } from "../../../../_components/SpecValue";
import { VariantActions } from "../../../../_components/VariantActions";
import { pageCtx } from "../../../../_lib/context";
import { withCountries } from "../../../../_lib/data";
import { findVariant, generationHref, generationRows, modelHref, variantHref, variantParams } from "../../../../_lib/routes";

type Props = { params: Promise<{ country: string; make: string; model: string; generation: string; variant: string }> };

export function generateStaticParams() {
  return withCountries(variantParams(getCatalogue().rows()));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { make, model, generation, variant } = await params;
  const r = findVariant(getCatalogue().rows(), make, model, generation, variant);
  return r ? { title: `${r.make_name} ${r.model_name} ${r.variant_name} (${r.generation_name})` } : {};
}

export default async function VariantPage({ params }: Props) {
  const { country, make, model, generation, variant } = await params;
  if (!isCountrySlug(country)) notFound();
  const ctx = await pageCtx(country);
  const all = ctx.cat.rows();
  const row = findVariant(all, make, model, generation, variant);
  if (!row) notFound();
  const { t, cfg } = ctx;
  const modelName = `${row.make_name} ${row.model_name}`;
  const name = `${modelName} ${row.variant_name}`;
  const siblings = timelineOrder(generationRows(all, make, model, generation)).filter((r) => r.variant_id !== row.variant_id);

  return (
    <>
      <Breadcrumbs
        label={t("nav.main")}
        items={[
          { label: t("crumb.home"), href: `/${country}` },
          { label: modelName, href: modelHref(country, row) },
          { label: row.generation_name, href: generationHref(country, row) },
          { label: row.variant_name },
        ]}
      />
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{name}</h1>
          <p className="mt-1 flex flex-wrap items-center gap-2 text-slate-800">
            <span>{row.generation_name}</span>
            <span className="tabular-nums">· {formatYears(row.year_start, row.year_end, t("years.now"))}</span>
            {row.generation_uncertain ? (
              <span className="rounded border border-amber-700 px-1 text-xs text-amber-900">{t("years.unchecked")}</span>
            ) : null}
            <span className="rounded border border-slate-400 px-1 text-xs">
              {t("variant.quality", { tier: t(`tier.${row.quality_tier}`) })}
            </span>
          </p>
        </div>
        <VariantActions
          id={row.variant_id}
          name={name}
          text={{
            favAdd: t("fav.add", { name }),
            favRemove: t("fav.remove", { name }),
            compareAdd: t("compare.add"),
            compareAddLabel: t("compare.addLabel", { name }),
            compareRemoveLabel: t("compare.removeLabel", { name }),
            compareFull: t("compare.full", { max: COMPARE_MAX }),
            compare: t("compare.add"),
          }}
        />
      </div>

      <h2 className="mt-8 text-xl font-semibold">{t("variant.specs")}</h2>
      <div className="mt-3 grid gap-6 lg:grid-cols-2">
        {SPEC_GROUPS.map((group) => {
          const fields = SPEC_FIELDS.filter((f) => f.group === group);
          const title = t(`variant.group.${group}`);
          return (
            <table key={group} className="w-full border-collapse text-sm">
              <caption className="pb-1 text-left text-base font-semibold">{title}</caption>
              <thead className="sr-only">
                <tr>
                  <th scope="col">{t("gen.diff.fieldHeader")}</th>
                  <th scope="col">{t("variant.valueHeader")}</th>
                </tr>
              </thead>
              <tbody>
                {fields.map((f) => (
                  <tr key={f.key} className="border-t border-slate-200">
                    <th scope="row" className="w-1/2 py-2 pr-3 text-left align-top font-normal text-slate-800">
                      <FieldLabel ctx={ctx} field={f} />
                    </th>
                    <td className="py-2 align-top font-medium">
                      <SpecValue ctx={ctx} row={row} field={f} />
                    </td>
                  </tr>
                ))}
                {group === "availability" ? (
                  <tr className="border-t border-slate-200">
                    <th scope="row" className="py-2 pr-3 text-left align-top font-normal text-slate-800">
                      {t("reg.title", { country: cfg.name })}
                    </th>
                    <td className="py-2 align-top font-medium">
                      <Registrations ctx={ctx} row={row} />
                    </td>
                  </tr>
                ) : null}
                {group === "availability" ? (
                  <tr className="border-t border-slate-200">
                    <th scope="row" className="py-2 pr-3 text-left align-top font-normal text-slate-800">
                      {t("gen.usedPrice", { country: cfg.name })}
                    </th>
                    <td className="py-2 align-top">
                      <PriceBand currency={cfg.currency} locale={ctx.locale} notEnoughLabel={t("price.notEnough")} samplesLabel={t("price.samples")} />
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          );
        })}
      </div>

      <div className="mt-8">
        <SeeListings
          links={seeListings(country, row)}
          text={{
            title: t("listings.title"),
            intro: t("listings.intro", { name: modelName, country: cfg.name }),
            newTab: t("listings.newTab"),
            unverified: t("listings.unverified"),
            none: t("listings.none"),
          }}
        />
      </div>

      {siblings.length ? (
        <section aria-labelledby="siblings" className="mt-8">
          <h2 id="siblings" className="text-xl font-semibold">
            {t("variant.otherVariants")}
          </h2>
          <ul className="mt-2 flex flex-wrap gap-2">
            {siblings.map((s) => (
              <li key={s.variant_id}>
                <Link href={variantHref(country, s)} className="inline-flex min-h-11 items-center rounded-md border border-slate-300 px-3 text-sm text-blue-800 underline underline-offset-2 hover:bg-slate-50">
                  {s.variant_name}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      <ChargingLinks links={chargingLinks(country, { withoutAbrp: true })} abrp={abrpLink()} t={t} />
    </>
  );
}
