import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { COUNTRY_SLUGS } from "@/config/countries";
import { loadListingConfig, OUT_FILE, serialize, validateCountry } from "../../scripts/listings.mjs";
import { buildListingUrl, hasUnverified, LISTING_REL, LISTING_SITES, LISTING_TARGET, seeListings } from "./listings";

describe("seeListings", () => {
  it("returns every configured site per country, in priority order, with rel and target", () => {
    for (const c of COUNTRY_SLUGS) {
      const links = seeListings(c, { make_name: "Volkswagen", model_name: "ID.3" });
      expect(links).toHaveLength(LISTING_SITES[c].length);
      const prios = links.map((l) => LISTING_SITES[c].find((s) => s.site === l.id)!.priority);
      expect([...prios].sort((a, b) => a - b)).toEqual(prios);
      for (const l of links) {
        expect(l.rel).toBe("nofollow noopener");
        expect(l.target).toBe("_blank");
        expect(l.url.startsWith("https://")).toBe(true);
        expect(l.url).not.toMatch(/[{}]/); // all placeholders filled
      }
    }
    expect(LISTING_REL).toContain("nofollow");
    expect(LISTING_TARGET).toBe("_blank");
  });

  it("builds slug and name placeholders", () => {
    const nl = seeListings("nl", { make_name: "Mercedes-Benz", model_name: "EQA" });
    expect(nl.find((l) => l.id === "autoscout24-nl")!.url).toBe("https://www.autoscout24.nl/lst/mercedes-benz/eqa?fuel=E");
    expect(nl.find((l) => l.id === "marktplaats")!.url).toBe("https://www.marktplaats.nl/l/auto-s/q/Mercedes-Benz+EQA/");
  });

  it("strips accents in slugs and URL-encodes names", () => {
    const fr = seeListings("fr", { make_name: "Citroën", model_name: "ë-C4" });
    const as24 = fr.find((l) => l.id === "autoscout24-fr")!.url;
    expect(as24).toBe("https://www.autoscout24.fr/lst/citroen/e-c4?fuel=E");
    const lbc = fr.find((l) => l.id === "leboncoin")!.url;
    expect(lbc).toContain(`text=${encodeURIComponent("Citroën")}+${encodeURIComponent("ë-C4")}`);
    const lc = fr.find((l) => l.id === "lacentrale")!.url;
    expect(lc).toContain(encodeURIComponent("CITROËN"));
  });

  it("encodes spaces and dots", () => {
    const uk = seeListings("uk", { make_name: "Kia", model_name: "Niro EV" });
    expect(uk[0]!.url).toBe("https://www.autotrader.co.uk/car-search?make=Kia&model=Niro%20EV&fuel-type=Electric");
    const de = seeListings("de", { make_name: "Volkswagen", model_name: "ID.3" });
    expect(de.find((l) => l.id === "autoscout24-de")!.url).toBe("https://www.autoscout24.de/lst/volkswagen/id-3?fuel=E");
  });

  it("reports unverified patterns (all of them, tonight)", () => {
    for (const c of COUNTRY_SLUGS) expect(hasUnverified(c)).toBe(true);
  });

  it("keeps the mobile.de electric filter", () => {
    const de = seeListings("de", { make_name: "Volkswagen", model_name: "ID.3" });
    expect(de.find((l) => l.id === "mobile-de")!.url).toBe(
      "https://suchen.mobile.de/fahrzeuge/search.html?isSearchRequest=true&q=Volkswagen+ID.3&ft=ELECTRICITY",
    );
  });

  it("applies slug overrides and filter maps", () => {
    const site = {
      site: "x",
      label: "X",
      url_template: "https://x.example/{make}/{model}",
      filters: { electric: { fuel: "E V" } },
      slug_overrides: { "mercedes-benz": "mercedes" },
      priority: 1,
      verified: false,
    };
    expect(buildListingUrl(site, "Mercedes-Benz", "EQA")).toBe("https://x.example/mercedes/eqa?fuel=E%20V");
    expect(buildListingUrl(site, "Mercedes-Benz", "EQA", [])).toBe("https://x.example/mercedes/eqa");
  });
});

describe("listing config (config/countries/*.yaml)", () => {
  it("the generated JSON matches the YAML (run `node scripts/listings.mjs` after editing)", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(serialize(loadListingConfig()));
  });

  it("covers every country, unverified, https only", () => {
    const cfg = loadListingConfig();
    expect(Object.keys(cfg).sort()).toEqual([...COUNTRY_SLUGS].sort());
    for (const sites of Object.values(cfg)) {
      expect(sites.length).toBeGreaterThan(0);
      for (const s of sites) {
        expect(s.verified).toBe(false);
        expect(s.url_template.startsWith("https://")).toBe(true);
      }
    }
  });

  it("rejects bad or private-looking entries (Decision 004)", () => {
    const ok = { site: "a", label: "A", url_template: "https://a.example/{make}", filters: {}, priority: 1, verified: false };
    expect(validateCountry("nl", { country: "nl", listings: [ok] })).toHaveLength(1);
    const bad = (s: Record<string, unknown>) => () => validateCountry("nl", { country: "nl", listings: [{ ...ok, ...s }] });
    expect(bad({ url_template: "http://a.example/" })).toThrow(/https/);
    expect(bad({ url_template: "https://a.example/{brand}" })).toThrow(/placeholder/);
    expect(bad({ verified: "no" })).toThrow(/verified/);
    expect(bad({ priority: "1" })).toThrow(/priority/);
    expect(bad({ sample_rate: 5 })).toThrow(/Decision 004/);
    expect(bad({ url_template: "https://a.example/?affiliate_id=1" })).toThrow(/Decision 004/);
    expect(bad({ filters: { electric: { api_key: "x" } } })).toThrow(/Decision 004/);
    expect(bad({ filters: { year: { y: "1" } } })).toThrow(/unknown filter/);
    expect(() => validateCountry("nl", { country: "de", listings: [ok] })).toThrow(/country/);
    expect(() => validateCountry("nl", { country: "nl", listings: [ok, ok] })).toThrow(/duplicate/);
  });
});
