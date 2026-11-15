// Renders one spec field of one variant: numbers through <Num> (source + confidence + badges),
// taxonomy ids as localised labels. Server component; shared by variant, generation and compare pages.
import type { PublishedVariant } from "@ev/schema";
import { Num } from "@/components/Num";
import { Term } from "@/components/Term";
import type { MsgKey } from "@/i18n";
import { DASH, formatMoney } from "@/lib/format";
import { hasPageKey } from "@/lib/pages-i18n";
import type { SpecField } from "@/lib/spec-diff";
import { sourcesFor, type PageCtx } from "../_lib/context";

const ND = "not-disclosed";

export function fieldLabel(ctx: PageCtx, field: SpecField): string {
  const k = `field.${field.key}`;
  return hasPageKey(k) ? ctx.pt(k, { country: ctx.cfg.name }) : field.key;
}

/** Plain-language label with the glossary ⓘ (safe inside <th>, not inside <label>/<button>). */
export function FieldLabel({ ctx, field }: { ctx: PageCtx; field: SpecField }) {
  const label = fieldLabel(ctx, field);
  const term = field.term ? ctx.tax.terms[field.term] : undefined;
  return <Term term={term ? { ...term, label } : undefined} fallback={label} country={ctx.country} text={ctx.termText} showTechnical={false} />;
}

function msg(ctx: PageCtx, key: string, fallback: string): string {
  const out = ctx.t(key as MsgKey);
  return out === key ? fallback : out;
}

/** Display text for a text/boolean field. */
export function textValue(ctx: PageCtx, row: PublishedVariant, key: Extract<SpecField, { kind: "text" }>["key"]): string {
  const v = row[key];
  if (v === null || v === undefined || v === "") return DASH;
  if (v === ND) return ctx.t("notDisclosed");
  if (typeof v === "boolean") return ctx.t(v ? "yes" : "no");
  switch (key) {
    case "chemistry_id":
      return ctx.tax.chemistries.find((c) => c.id === v)?.label ?? String(v);
    case "cooling_id":
      return ctx.tax.coolings.find((c) => c.id === v)?.label ?? String(v);
    case "voltage_class_id":
      return ctx.tax.voltageClasses.find((c) => c.id === v)?.label ?? String(v);
    case "charger_400v_mode":
      return msg(ctx, `c400.${v}`, String(v));
    case "body":
      return msg(ctx, `body.${v}`, String(v));
    case "segment":
      return msg(ctx, `segment.${v}`, String(v));
    case "drivetrain": {
      const k = `drivetrain.${v}`;
      return hasPageKey(k) ? ctx.pt(k) : String(v);
    }
    default:
      return String(v);
  }
}

export function SpecValue({ ctx, row, field }: { ctx: PageCtx; row: PublishedVariant; field: SpecField }) {
  if (field.kind === "text") return <span>{textValue(ctx, row, field.key)}</span>;
  if (field.kind === "price") {
    const m = row.price_new?.[ctx.cfg.code];
    const prov = row.provenance[`price_new.${ctx.cfg.code}`];
    return (
      <Num
        value={m?.amount}
        text={m ? formatMoney(m.amount, m.currency, ctx.locale) : undefined}
        provenance={prov}
        sources={sourcesFor(ctx, prov)}
        locale={ctx.locale}
        labels={ctx.labels}
        asOf={ctx.asOf}
      />
    );
  }
  const v = row[field.key];
  const prov = row.provenance[field.key];
  const note =
    field.key === "real_range_km" && row.real_range_rung ? msg(ctx, `rung.${row.real_range_rung}`, row.real_range_rung) : undefined;
  return (
    <Num
      value={typeof v === "number" ? v : null}
      unit={field.unit}
      digits={field.digits}
      provenance={prov}
      sources={sourcesFor(ctx, prov)}
      locale={ctx.locale}
      labels={ctx.labels}
      note={note}
      claim={field.key === "dc_peak_kw" && !!row.dc_peak_kw_is_claim}
      asOf={ctx.asOf}
    />
  );
}
