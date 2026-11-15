// Official registration counts for the page's country (fleet / new registrations), one line per
// count with kind, period and source; never summed. Model-level counts (generation unknown, e.g.
// RDW shared-year cars, Q-066) say so: "generation unknown, shown on all X generations".
// Server component; numbers through <Num> with provenance key `registrations.<CC>`.
import type { PublishedVariant } from "@ev/schema";
import { Missing, Num } from "@/components/Num";
import { registrationItemKey, registrationsFor, registrationsProvKey } from "@/lib/registrations";
import { sourcesFor, type PageCtx } from "../_lib/context";

export function Registrations({ ctx, row }: { ctx: PageCtx; row: PublishedVariant | undefined }) {
  const code = ctx.cfg.code;
  const list = row ? registrationsFor(row, code) : [];
  if (!row || !list.length) return <Missing label={ctx.labels.noData} />;
  const prov = row.provenance[registrationsProvKey(code)];
  return (
    <ul className="flex flex-col gap-1" data-testid="registrations">
      {list.map((r) => {
        const details = [
          ctx.t(r.kind === "fleet" ? "reg.fleet" : "reg.new"),
          r.period,
          r.level === "model" ? ctx.t("reg.modelLevel", { model: `${row.make_name} ${row.model_name}` }) : undefined,
          ctx.sources[r.source_id] ?? r.source_id,
        ].filter(Boolean);
        return (
          <li
            key={registrationItemKey(r)}
            data-kind={r.kind}
            data-level={r.level ?? "generation"}
            data-period={r.period ?? ""}
            data-source={r.source_id}
            className="flex flex-wrap items-baseline gap-x-1"
          >
            <Num
              value={r.count}
              digits={0}
              provenance={prov}
              sources={sourcesFor(ctx, prov)}
              locale={ctx.locale}
              labels={ctx.labels}
              asOf={ctx.asOf}
            />
            <span className="text-sm font-normal text-slate-800">{details.join(" · ")}</span>
          </li>
        );
      })}
    </ul>
  );
}
