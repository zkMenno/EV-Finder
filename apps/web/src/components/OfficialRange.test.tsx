// T-143 (Decision 085): the "Official (WLTP)" line next to our real range.
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { getT } from "@/i18n";
import { numLabels } from "./num-labels";
import { OfficialRange } from "./OfficialRange";

const t = getT("en");
const text = { label: t("range.wltp.label"), notKnown: t("range.wltp.notKnown"), tip: t("range.wltp.tip") };
const base = { locale: "en-GB", labels: numLabels(t), text };

describe("OfficialRange (T-143)", () => {
  it("labels the figure 'Official (WLTP)' with km", () => {
    const html = renderToStaticMarkup(<OfficialRange {...base} value={452} />);
    expect(html).toContain("Official (WLTP)");
    expect(html).toContain("452");
    expect(html).toContain("km");
    expect(html).toContain('data-known="1"');
  });

  it("missing WLTP says 'not known', never a number in its place", () => {
    for (const v of [null, undefined, 0]) {
      const html = renderToStaticMarkup(<OfficialRange {...base} value={v} />);
      expect(html).toContain("not known");
      expect(html).toContain('data-known="0"');
      expect(html).not.toMatch(/\d+\s*km/);
    }
  });

  it("the ⓘ explains the difference in one sentence", () => {
    const html = renderToStaticMarkup(<OfficialRange {...base} value={452} info={{ href: "/nl/en/learn/wltp", termText: { about: "About {term}", learnMore: "Learn more" } }} />);
    expect(html).toContain("About Official (WLTP)");
    expect(html).toContain(text.tip.replace(/'/g, "&#x27;"));
    // One sentence: a single full stop, at the end.
    expect(text.tip.trim().split(/[.!?](\s|$)/).filter((s) => s.trim()).length).toBe(1);
    expect(html).toContain("/nl/en/learn/wltp");
  });

  it("cards pass a span text", () => {
    const html = renderToStaticMarkup(<OfficialRange {...base} value={450} valueText="380–450" />);
    expect(html).toContain("380–450");
  });
});
