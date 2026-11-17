// Used price by build year for one variant in one country (T-094, data T-081 used_prices.json).
// Server component. Model bands are estimates (list price × value kept at that age) and say so;
// low-confidence bands say why. Rows run newest first.
import type { Currency } from "@ev/schema";
import { formatMoney } from "@/lib/format";
import type { VariantBand } from "@/lib/variant-prices";
import type { PageCtx } from "../_lib/context";

export function UsedByYear({ ctx, bands, currency }: { ctx: PageCtx; bands: VariantBand[]; currency: Currency }) {
  const { t } = ctx;
  const money = (n: number) => formatMoney(n, currency, ctx.locale);
  const rows = [...bands].sort((a, b) => b.build_year - a.build_year);
  const anyEstimate = rows.some((b) => b.estimate);
  const anyLow = rows.some((b) => b.confidence === "low");
  return (
    <div data-testid="used-by-year">
      <ul className="grid gap-0.5 tabular-nums">
        {rows.map((b) => (
          <li key={b.build_year}>
            <span className="font-medium">{b.build_year}</span>:{" "}
            {b.p25 !== null && b.p75 !== null ? t("usedYear.range", { low: money(b.p25), high: money(b.p75) }) : t("usedYear.about", { amount: money(b.median) })}
            {b.confidence === "low" ? <span className="text-slate-700"> *</span> : null}
            {b.samples > 0 ? <span className="text-xs text-slate-700"> · {t("usedYear.samples", { n: b.samples })}</span> : null}
          </li>
        ))}
      </ul>
      {anyEstimate ? <p className="mt-1 text-xs text-slate-700">{t("usedYear.estimate")}</p> : null}
      {anyLow ? <p className="mt-0.5 text-xs text-slate-700">* {t("usedYear.low")}</p> : null}
    </div>
  );
}
