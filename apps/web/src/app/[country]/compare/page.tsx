// Compare page (T-010): ?ids=a,b,c,d → side-by-side table, differences highlighted,
// "only differences" toggle (?diff=1, a plain link so it works without JS), share and print.
import type { PublishedVariant } from "@ev/schema";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { CompareTable, type CompareGroupView } from "@/components/CompareTable";
import { isCountrySlug } from "@/config/countries";
import { siteName } from "@/config/site";
import { COMPARE_MAX } from "@/lib/compare-store";
import { formatYears } from "@/lib/format";
import { requestLang } from "@/lib/request-lang";
import { cellValue, differingCells, SPEC_FIELDS, SPEC_GROUPS } from "@/lib/spec-diff";
import { FieldLabel, SpecValue } from "../ev/_components/SpecValue";
import { pageCtx } from "../ev/_lib/context";
import { variantHref } from "../ev/_lib/routes";
import { CompareActions } from "./_components/CompareActions";
import { compareUrl, parseCompareIds } from "./_lib/ids";
import "./print.css";
import { getT } from "@/i18n";

type Props = {
  params: Promise<{ country: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { country } = await params;
  if (!isCountrySlug(country)) return {};
  return { title: getT(await requestLang(country))("compare.title"), robots: { index: false } };
}

export default async function ComparePage({ params, searchParams }: Props) {
  const { country } = await params;
  if (!isCountrySlug(country)) notFound();
  const sp = await searchParams;
  const ctx = await pageCtx(country);
  const { t, cfg } = ctx;
  const ids = parseCompareIds(sp.ids);
  const onlyDiff = sp.diff === "1";
  const cars = ids.map((id) => ctx.cat.variant(id)).filter((r): r is PublishedVariant => !!r);
  const missing = ids.filter((id) => !ctx.cat.variant(id));
  const foundIds = cars.map((c) => c.variant_id);

  const groups: CompareGroupView[] = SPEC_GROUPS.map((group) => ({
    key: group,
    title: t(`variant.group.${group}`),
    rows: SPEC_FIELDS.filter((f) => f.group === group).flatMap((field) => {
      const values = cars.map((c) => cellValue(c, field, cfg.code));
      if (values.every((v) => v === null)) return [];
      const differs = differingCells(values);
      if (onlyDiff && !differs.some(Boolean)) return [];
      return [
        {
          key: field.key,
          label: <FieldLabel ctx={ctx} field={field} />,
          cells: cars.map((c, i) => ({ differs: differs[i] ?? false, content: <SpecValue ctx={ctx} row={c} field={field} /> })),
        },
      ];
    }),
  })).filter((g) => g.rows.length);

  return (
    <div data-compare-page="">
      <Breadcrumbs label={t("nav.main")} items={[{ label: t("crumb.home"), href: `/${country}` }, { label: t("crumb.compare") }]} />
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{t("compare.title")}</h1>
          <p className="mt-2 max-w-3xl text-slate-800">{t("compare.intro", { max: COMPARE_MAX })}</p>
        </div>
        {cars.length ? (
          <CompareActions text={{ share: t("compare.share"), copied: t("compare.copied"), copyFailed: t("compare.copyFailed"), print: t("compare.print") }} />
        ) : null}
      </div>

      {missing.length ? (
        <p className="mt-4 rounded-md border border-amber-700 bg-amber-50 p-3 text-sm" role="status">
          {t("compare.notFound", { ids: missing.join(", ") })}
        </p>
      ) : null}

      {!cars.length ? (
        <p className="mt-6">
          {t("compare.empty")}{" "}
          <Link href={`/${country}`} className="text-blue-800 underline underline-offset-2">
            {t("compare.toExplore")}
          </Link>
        </p>
      ) : (
        <>
          <div className="mt-6 flex flex-wrap items-center justify-between gap-3 print:hidden">
            {cars.length >= 2 ? (
              <Link
                href={compareUrl(country, foundIds, !onlyDiff)}
                className="inline-flex min-h-11 items-center gap-2 rounded-md border border-blue-800 px-4 text-sm font-semibold text-blue-900 hover:bg-blue-50"
                data-testid="compare-diff-toggle"
              >
                <span aria-hidden="true">{onlyDiff ? "☑" : "☐"}</span>
                {onlyDiff ? t("compare.showAll") : t("compare.onlyDiff")}
              </Link>
            ) : (
              <p className="text-sm text-slate-800">{t("compare.addMore")}</p>
            )}
            <p className="text-sm text-slate-700">{t("compare.legend")}</p>
          </div>
          {groups.length ? (
            <div className="mt-3">
              <CompareTable
                caption={t("compare.caption", { n: cars.length })}
                fieldHeader={t("gen.diff.fieldHeader")}
                differsLabel={t("compare.differs")}
                columns={cars.map((c) => {
                  const name = `${c.make_name} ${c.model_name} ${c.variant_name}`;
                  return {
                    key: c.variant_id,
                    header: (
                      <span className="flex flex-col gap-0.5">
                        <Link href={variantHref(country, c)} className="text-blue-800 underline underline-offset-2 hover:text-blue-950">
                          {name}
                        </Link>
                        <span className="text-xs font-normal text-slate-700">
                          {c.generation_name} · <span className="tabular-nums">{formatYears(c.year_start, c.year_end, t("years.now"))}</span>
                        </span>
                        <Link
                          href={compareUrl(
                            country,
                            foundIds.filter((x) => x !== c.variant_id),
                            onlyDiff,
                          )}
                          className="text-xs font-normal text-slate-800 underline underline-offset-2 print:hidden"
                        >
                          {t("compare.remove", { name })}
                        </Link>
                      </span>
                    ),
                  };
                })}
                groups={groups}
              />
            </div>
          ) : (
            <p className="mt-4">{t("compare.noDiffs")}</p>
          )}
          <p className="mt-4 hidden text-xs print:block">
            {t("compare.printNote", { site: siteName, release: ctx.cat.origin() === "fixture" ? "dev" : ctx.cat.release() })}
          </p>
        </>
      )}
    </div>
  );
}
