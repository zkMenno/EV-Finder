// Generation-year badge (T-061), shared by the model, generation and variant pages so the
// three always agree: "years checked against Wikidata", "Wikidata disagrees" (what it says at
// Nerd level) or the existing "years not yet checked". Server component; text, not colour alone.
import { LevelGate } from "@/components/LevelGate";
import { TermInfo } from "@/components/Term";
import type { PageCtx } from "../_lib/context";
import type { YearsStatus } from "../_lib/data";

const NERD = ["nerd"] as const;

export function YearsBadge({
  ctx,
  status,
  yearStart,
  yearEnd,
  compact = false,
}: {
  ctx: PageCtx;
  status: YearsStatus;
  yearStart: number;
  yearEnd: number | null;
  /** Model page cards: badge + ⓘ only, no Nerd details. */
  compact?: boolean;
}) {
  const { t } = ctx;
  if (status.kind === "none") return null;
  const info = <TermInfo term={ctx.tax.terms["model-years"]} base={ctx.base} text={ctx.termText} />;
  if (status.kind === "unchecked") {
    return (
      <>
        <span
          className="rounded border border-amber-700 px-1 text-xs text-amber-900"
          data-testid="years-badge"
          data-kind="unchecked"
        >
          {t("years.unchecked")}
          <span className="sr-only">. {t("years.unchecked.help")}</span>
        </span>
        {info}
      </>
    );
  }
  const ok = status.kind === "corroborated";
  return (
    <>
      <span
        className={`rounded border px-1 text-xs ${ok ? "border-green-700 text-green-900" : "border-amber-700 text-amber-900"}`}
        data-testid="years-badge"
        data-kind={status.kind}
      >
        {ok ? t("years.wikidata.ok") : t("years.wikidata.disagrees")}
        <span className="sr-only">
          .{" "}
          {ok
            ? t("years.wikidata.ok.help", { n: status.tolerance })
            : t("years.wikidata.disagrees.help")}
        </span>
      </span>
      {/* A Wikidata check explains itself with its own term; falls back to model-years if the row is missing. */}
      <TermInfo term={ctx.tax.terms["wikidata-years"] ?? ctx.tax.terms["model-years"]} base={ctx.base} text={ctx.termText} />
      {compact ? null : (
        <LevelGate show={NERD}>
          <span className="block basis-full text-xs text-slate-700" data-testid="years-nerd">
            {status.checks.map((c, i) => (
              <span key={`${c.boundary}-${c.year}-${i}`} className="block">
                {t(c.boundary === "start" ? "years.check.start" : "years.check.end", {
                  year: c.year,
                  ours: c.boundary === "start" ? yearStart : (yearEnd ?? t("years.now")),
                  label: c.label ?? c.source_record ?? c.source_id,
                })}{" "}
                ·{" "}
                {c.agrees
                  ? t("years.check.agrees", { n: status.tolerance })
                  : t("years.check.off", { n: status.tolerance })}
                {c.source_record ? <code className="ml-1 break-all">{c.source_record}</code> : null}{" "}
                · {c.retrieved_at}
              </span>
            ))}
          </span>
        </LevelGate>
      )}
    </>
  );
}
