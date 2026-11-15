import { describe, expect, it } from "vitest";
import { numBadges } from "@/components/Num";
import { numLabels } from "@/components/num-labels";
import { quartiles } from "@/components/PriceBand";
import { swapCountry, withLang } from "@/components/Switchers";
import { COUNTRIES, listingLinks } from "@/config/countries";
import { getT } from "@/i18n";
import { DASH, formatMoney, formatNumber, formatYears, localeFor } from "./format";

const nbsp = (s: string) => s.replace(/[\u00a0\u202f]/g, " ");

describe("formatters", () => {
  it("formats numbers per language locale", () => {
    expect(formatNumber(1234.56, localeFor("en"))).toBe("1,234.6");
    expect(nbsp(formatNumber(1234.56, localeFor("nl")))).toBe("1.234,6");
    expect(nbsp(formatNumber(1234.56, localeFor("fr")))).toBe("1 234,6");
  });
  it("shows a dash for missing values", () => {
    expect(formatNumber(null, "en-GB")).toBe(DASH);
    expect(formatNumber(Number.NaN, "en-GB")).toBe(DASH);
    expect(formatMoney(undefined, "EUR", "en-GB")).toBe(DASH);
  });
  it("formats money with the country currency", () => {
    expect(formatMoney(39990, "GBP", localeFor("en"))).toBe("£39,990");
    expect(nbsp(formatMoney(39990, "EUR", localeFor("nl")))).toBe("€ 39.990");
  });
  it("UK uses GBP, the rest EUR", () => {
    expect(COUNTRIES.uk.currency).toBe("GBP");
    for (const c of ["nl", "de", "fr", "be"] as const) expect(COUNTRIES[c].currency).toBe("EUR");
  });
  it("formats year spans", () => {
    expect(formatYears(2019, 2023, "now")).toBe("2019–2023");
    expect(formatYears(2024, null, "now")).toBe("2024–now");
    expect(formatYears(2020, 2020, "now")).toBe("2020");
  });
});

describe("Num badges (Decision 009)", () => {
  const labels = numLabels(getT("en"));
  it("N sources agree / 1 source / estimate / claim", () => {
    expect(numBadges({ source_ids: ["a"], confidence: "high", agreeing_sources: 3 }, labels)).toEqual(["3 sources agree"]);
    expect(numBadges({ source_ids: ["a"], confidence: "low", agreeing_sources: 1 }, labels)).toEqual(["1 source"]);
    expect(numBadges({ source_ids: ["a"], confidence: "low", estimate: true }, labels)).toEqual(["estimate"]);
    expect(numBadges(undefined, labels, true)).toEqual(["claim"]);
    expect(numBadges({ source_ids: ["a"], confidence: "low" }, labels)).toEqual([]);
  });
});

describe("price band", () => {
  it("quartiles", () => {
    expect(quartiles([1, 2, 3, 4, 5])).toEqual([2, 4]);
  });
});

describe("switchers and listing links", () => {
  it("country switch keeps the path and query", () => {
    expect(swapCountry("/nl/compare", "?ids=a,b", "de")).toBe("/de/compare?ids=a,b");
    expect(swapCountry("/nl", "", "uk")).toBe("/uk");
  });
  it("language switch keeps the URL and sets ?lang", () => {
    expect(withLang("/nl", "?price=30000&lang=nl", "en")).toBe("/nl?price=30000&lang=en");
  });
  it("builds unverified deep links, priority order", () => {
    const links = listingLinks("nl", "Volkswagen", "ID.3");
    expect(links.map((l) => l.id)).toEqual(["autoscout24-nl", "marktplaats", "gaspedaal"]);
    expect(links[0]!.url).toBe("https://www.autoscout24.nl/lst/volkswagen/id-3?fuel=E");
    expect(links.every((l) => !l.verified)).toBe(true);
  });
});
