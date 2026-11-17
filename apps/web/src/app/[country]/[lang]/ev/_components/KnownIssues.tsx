// Known issues on generation pages (T-061): RDW APK defect rates per first-registration year.
// Server component. Every rate is set next to the baseline of the SAME first-registration year
// only (Q-078); cohorts with too few reports show "not enough inspections yet". RDW labels are
// Dutch, shown as published; source wording follows the Q-037 interim line.
import { Fragment } from "react";
import { parkedEnabled } from "@/config/features";
import { LevelGate, LevelNum } from "@/components/LevelGate";
import { TermInfo } from "@/components/Term";
import {
  knownIssuesFor,
  RDW_INTERIM_NAME,
  SIMPLE_TOP_N,
  versusBaseline,
  type CohortView,
  type KnownIssuesView,
} from "@/lib/known-issues";
import type { PageCtx } from "../_lib/context";

const DETAILED = ["detailed", "nerd"] as const;
const NERD = ["nerd"] as const;

function Rate({ ctx, v, value }: { ctx: PageCtx; v: KnownIssuesView; value: number }) {
  return (
    <LevelNum
      value={value}
      digits={1}
      provenance={v.provenance}
      sources={{ [v.sourceId]: RDW_INTERIM_NAME }}
      locale={ctx.locale}
      labels={ctx.labels}
      asOf={v.retrievedAt}
    />
  );
}

function Count({ ctx, v, value }: { ctx: PageCtx; v: KnownIssuesView; value: number }) {
  return (
    <LevelNum
      value={value}
      digits={0}
      provenance={{ ...v.provenance, derived: false }}
      sources={{ [v.sourceId]: RDW_INTERIM_NAME }}
      locale={ctx.locale}
      labels={ctx.labels}
      asOf={v.retrievedAt}
    />
  );
}

function Cohort({
  ctx,
  v,
  c,
  name,
}: {
  ctx: PageCtx;
  v: KnownIssuesView;
  c: CohortView;
  name: string;
}) {
  const { t } = ctx;
  const headId = `ki-${c.year}`;
  const heading = (
    <h3 id={headId} className="text-base font-semibold">
      {t("gen.ki.cohort", { year: String(c.year) })}
      <TermInfo term={ctx.tax.terms["first-registration-year"]} base={ctx.base} text={ctx.termText} />{" "}
      <span className="font-normal text-slate-700">
        · {t("gen.ki.age", { n: String(c.ageYears) })}
      </span>
    </h3>
  );
  if (c.hidden) {
    return (
      <section
        aria-labelledby={headId}
        className="rounded-md border border-slate-300 p-3"
        data-testid="ki-cohort-hidden"
        data-year={c.year}
      >
        {heading}
        <p className="mt-1 text-sm text-slate-800">{t("gen.ki.fewReports")}</p>
        <LevelGate show={NERD}>
          <p className="mt-1 text-xs text-slate-700" data-testid="ki-nerd">
            {t("gen.ki.nerd.sample")}: <Count ctx={ctx} v={v} value={c.sampleCars} /> ·{" "}
            {t("gen.ki.nerd.withAny")}: <Count ctx={ctx} v={v} value={c.carsWithAnyDefect} />
          </p>
        </LevelGate>
      </section>
    );
  }
  const verdict = versusBaseline(c.anyPer100, c.baseline.anyPer100);
  return (
    <section
      aria-labelledby={headId}
      className="rounded-md border border-slate-300 p-3"
      data-testid="ki-cohort"
      data-year={c.year}
    >
      {heading}
      <p className="mt-1 text-sm text-slate-900" data-testid="ki-any">
        {t("gen.ki.any")}: <Rate ctx={ctx} v={v} value={c.anyPer100} /> {t("gen.ki.per100")}
        <TermInfo term={ctx.tax.terms["defect-rate"]} base={ctx.base} text={ctx.termText} /> ·{" "}
        {t("gen.ki.baseline", { year: String(c.year) })}:{" "}
        <Rate ctx={ctx} v={v} value={c.baseline.anyPer100} /> {t("gen.ki.per100short")}
      </p>
      <p className="text-sm text-slate-800" data-testid="ki-verdict">
        {t(`gen.ki.verdict.${verdict}`, { name, year: String(c.year) })}
      </p>
      <LevelGate show={NERD}>
        <p className="mt-1 text-xs text-slate-700" data-testid="ki-nerd">
          {t("gen.ki.nerd.sample")}: <Count ctx={ctx} v={v} value={c.sampleCars} /> ·{" "}
          {t("gen.ki.nerd.withAny")}: <Count ctx={ctx} v={v} value={c.carsWithAnyDefect} /> ·{" "}
          {t("gen.ki.nerd.baselineSample", { year: String(c.year) })}:{" "}
          <Count ctx={ctx} v={v} value={c.baseline.sampleCars} /> · {c.ageBand}
        </p>
      </LevelGate>
      {c.defects.length ? (
        <div className="mt-2 overflow-x-auto">
          <table className="w-full min-w-[28rem] border-collapse text-sm" data-testid="ki-table">
            <caption className="sr-only">
              {t("gen.ki.caption", { name, year: String(c.year) })}
            </caption>
            <thead>
              <tr className="border-b border-slate-300 text-left">
                <th scope="col" className="py-1 pr-3 font-semibold">
                  {t("gen.ki.col.defect")}
                </th>
                <LevelGate show={NERD}>
                  <th scope="col" className="py-1 pr-3 font-semibold">
                    {t("gen.ki.col.code")}
                  </th>
                </LevelGate>
                <th scope="col" className="py-1 pr-3 font-semibold">
                  {t("gen.ki.col.this", { name })}
                </th>
                <th scope="col" className="py-1 pr-3 font-semibold">
                  {t("gen.ki.col.baseline", { year: String(c.year) })}
                </th>
                <LevelGate show={NERD}>
                  <th scope="col" className="py-1 font-semibold">
                    {t("gen.ki.col.cars")}
                  </th>
                </LevelGate>
              </tr>
            </thead>
            <tbody>
              {c.defects.map((d, i) => {
                const row = (
                  <tr
                    className="border-b border-slate-200 align-top"
                    data-testid="ki-defect"
                    data-code={d.code}
                  >
                    <th scope="row" className="py-1 pr-3 text-left font-normal">
                      <span lang="nl">{d.labelNl}</span>
                    </th>
                    <LevelGate show={NERD}>
                      <td className="py-1 pr-3 font-mono text-xs">
                        {d.code}
                        {d.article ? (
                          <span className="block text-slate-700">
                            {t("gen.ki.article", { article: d.article })}
                          </span>
                        ) : null}
                      </td>
                    </LevelGate>
                    <td className="py-1 pr-3">
                      <Rate ctx={ctx} v={v} value={d.per100} />
                    </td>
                    <td className="py-1 pr-3">
                      <Rate ctx={ctx} v={v} value={d.cohortPer100} />
                    </td>
                    <LevelGate show={NERD}>
                      <td className="py-1">
                        <Count ctx={ctx} v={v} value={d.carsWithDefect} />
                      </td>
                    </LevelGate>
                  </tr>
                );
                return i < SIMPLE_TOP_N ? (
                  <Fragment key={d.code}>{row}</Fragment>
                ) : (
                  <LevelGate key={d.code} show={DETAILED}>
                    {row}
                  </LevelGate>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="mt-1 text-sm text-slate-800">{t("gen.ki.noCodes")}</p>
      )}
    </section>
  );
}

export function KnownIssues({
  ctx,
  generationId,
  name,
}: {
  ctx: PageCtx;
  generationId: string;
  name: string;
}) {
  // Parked until after launch (Decision 051): KNOWN_ISSUES=1 or PARKED=1 shows it.
  if (!parkedEnabled("knownIssues")) return null;
  const { t } = ctx;
  const v = knownIssuesFor(ctx.cat.knownIssues(), generationId);
  const terms = ctx.tax.terms;
  return (
    <section aria-labelledby="known-issues" className="mt-8 max-w-3xl" data-testid="known-issues">
      <h2 id="known-issues" className="flex items-center gap-1 text-xl font-semibold">
        {t("gen.ki.title")}
        <TermInfo term={terms["known-issues"]} base={ctx.base} text={ctx.termText} />
      </h2>
      {!v ? (
        <p className="mt-2 text-slate-800" data-testid="ki-none">
          {t("gen.ki.none")}
        </p>
      ) : (
        <>
          <p className="mt-1 text-sm text-slate-800">
            {t("gen.ki.intro")}
            <TermInfo term={terms["apk"]} base={ctx.base} text={ctx.termText} />
          </p>
          <p className="mt-1 text-sm text-slate-800">{t("gen.ki.sameYear")}</p>
          <p className="mt-1 text-sm text-slate-700">{t("gen.ki.dutchLabels")}</p>
          <div className="mt-3 flex flex-col gap-3">
            {v.cohorts.map((c) => (
              <Cohort key={c.year} ctx={ctx} v={v} c={c} name={name} />
            ))}
          </div>
          <p className="mt-3 text-xs text-slate-700" data-testid="ki-source">
            {t("gen.ki.source", { source: RDW_INTERIM_NAME })}
            {v.reportedFrom && v.reportedTo
              ? ` · ${t("gen.ki.period", { from: v.reportedFrom, to: v.reportedTo })}`
              : ""}{" "}
            · {t("gen.ki.retrieved", { date: v.retrievedAt })}
          </p>
          <LevelGate show={NERD}>
            <div className="mt-1 text-xs text-slate-700" data-testid="ki-method">
              <p>
                {t("gen.ki.nerd.basis")}: {v.rateBasis}
              </p>
              {v.inspection ? (
                <p>
                  {t("gen.ki.nerd.inspection")}: <span lang="nl">{v.inspection}</span>
                </p>
              ) : null}
              {v.sampleRule ? (
                <p className="break-words">
                  {t("gen.ki.nerd.rule")}: <code>{v.sampleRule}</code>
                </p>
              ) : null}
            </div>
          </LevelGate>
        </>
      )}
    </section>
  );
}
