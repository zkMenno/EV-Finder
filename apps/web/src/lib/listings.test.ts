import { describe, expect, it } from "vitest";
import { COUNTRIES, COUNTRY_SLUGS } from "@/config/countries";
import { hasUnverified, LISTING_REL, LISTING_TARGET, seeListings } from "./listings";

describe("seeListings", () => {
  it("returns every configured site per country, in priority order, with rel and target", () => {
    for (const c of COUNTRY_SLUGS) {
      const links = seeListings(c, { make_name: "Volkswagen", model_name: "ID.3" });
      expect(links).toHaveLength(COUNTRIES[c].listings.length);
      const prios = links.map((l) => COUNTRIES[c].listings.find((s) => s.id === l.id)!.priority);
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
    expect(nl.find((l) => l.id === "marktplaats")!.url).toBe("https://www.marktplaats.nl/q/Mercedes-Benz+EQA/");
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
});
