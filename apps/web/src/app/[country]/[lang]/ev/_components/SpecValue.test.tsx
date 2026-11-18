// The optional bigger on-board charger next to the standard one (T-063 field ac_kw_optional).
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { SPEC_FIELDS } from "@/lib/spec-diff";
import { pageCtx } from "../_lib/context";
import { SpecValue } from "./SpecValue";

const ctx = pageCtx("nl", "en");
const field = SPEC_FIELDS.find((f) => f.key === "ac_kw")!;
const base = ctx.cat.rows()[0]!;
const text = (html: string) => html.replace(/<[^>]+>/g, "").replace(/&nbsp;|\u00a0/g, " ").replace(/\s+/g, " ");

describe("SpecValue: AC charging power", () => {
  it('shows "7.4 kW (11 kW optional)" when a bigger charger is optional', () => {
    const row = { ...base, ac_kw: 7.4, ac_kw_optional: 11 };
    const html = renderToStaticMarkup(<SpecValue ctx={ctx} row={row} field={field} />);
    expect(html).toContain('data-testid="ac-optional"');
    expect(text(html)).toMatch(/7\.4 kW[\s\S]*\(11 kW[\s\S]* optional\)$/);
  });

  it("shows only the standard power without an optional one", () => {
    const row = { ...base, ac_kw: 11, ac_kw_optional: null };
    const html = renderToStaticMarkup(<SpecValue ctx={ctx} row={row} field={field} />);
    expect(html).not.toContain("ac-optional");
    expect(text(html)).not.toContain("optional");
    expect(text(html)).toMatch(/11(\.0)? kW/);
  });
});
