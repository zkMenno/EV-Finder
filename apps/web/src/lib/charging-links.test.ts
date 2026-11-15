import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { COUNTRY_SLUGS } from "@/config/countries";
import { tripFitEnabled } from "@/config/features";
import { loadChargingLinks, OUT_FILE, serialize, validateChargingLinks } from "../../scripts/charging-links.mjs";
import { validateCountry } from "../../scripts/listings.mjs";
import { abrpLink, chargingConfig, chargingLinks, linkRel, withUtm, type ChargingLinkConfig } from "./charging-links";

// Fixture shaped like the spec's Netherlands row (Chargemap, ABRP, Chargeprice, PlugShare).
const fixture = {
  nl: [
    { job: "route-planner", label: "ABRP", url: "https://abetterrouteplanner.com/", order: 2, tool: "abrp", official: false, utm: true },
    { job: "map", label: "Chargemap", url: "https://chargemap.com/", order: 1, tool: "chargemap", official: false, utm: true },
    { job: "price-compare", label: "Chargeprice", url: "https://www.chargeprice.app/?x=1", order: 3, tool: "chargeprice", official: false, utm: true },
    { job: "official-map", label: "Ladesäulenkarte", url: "https://www.bundesnetzagentur.de/", order: 4, tool: "bnetza", official: true, utm: false },
  ],
  de: [],
  fr: [],
  be: [],
  uk: [],
} as unknown as Record<(typeof COUNTRY_SLUGS)[number], ChargingLinkConfig[]>;

describe("charging links: rendering rules", () => {
  it("orders by config, adds our UTM tag, new tab, noopener (+ nofollow for third parties)", () => {
    const links = chargingLinks("nl", { config: fixture });
    expect(links.map((l) => l.label)).toEqual(["Chargemap", "ABRP", "Chargeprice", "Ladesäulenkarte"]);
    const cm = links[0]!;
    expect(cm.url).toBe("https://chargemap.com/?utm_source=evfinder&utm_medium=referral&utm_campaign=charging_links");
    expect(cm.target).toBe("_blank");
    expect(cm.rel).toBe("nofollow noopener");
    expect(links[2]!.url).toBe("https://www.chargeprice.app/?x=1&utm_source=evfinder&utm_medium=referral&utm_campaign=charging_links");
    // Official site: no nofollow; this one opts out of UTM in config.
    expect(links[3]!.rel).toBe("noopener");
    expect(links[3]!.url).toBe("https://www.bundesnetzagentur.de/");
  });

  it("renders nothing for a country without links, and never more than five", () => {
    expect(chargingLinks("de", { config: fixture })).toEqual([]);
    const many = { ...fixture, nl: Array.from({ length: 7 }, (_, i) => ({ ...fixture.nl[1]!, url: `https://e${i}.example/`, order: i })) };
    expect(chargingLinks("nl", { config: many })).toHaveLength(5);
  });

  it("model pages drop ABRP from the block (they get the plain ABRP line instead)", () => {
    expect(chargingLinks("nl", { config: fixture, withoutAbrp: true }).map((l) => l.label)).not.toContain("ABRP");
    const a = abrpLink();
    expect(a.url.startsWith("https://abetterrouteplanner.com/?")).toBe(true);
    expect(a.url).toContain("utm_source=evfinder");
    expect(new URL(a.url).searchParams.size).toBe(3); // only UTM: no car pre-selection yet (T-029)
    expect(a.url).not.toMatch(/car_model|typecode/); // no car pre-selection yet (T-029)
    expect(a.rel).toBe("nofollow noopener");
  });

  it("keeps an existing UTM tag; rel helper", () => {
    expect(withUtm("https://x.example/?utm_source=a")).toBe("https://x.example/?utm_source=a");
    expect(linkRel(true)).toBe("noopener");
    expect(linkRel(false)).toBe("nofollow noopener");
  });

  it("CHARGING_LINKS_FILE overrides the generated config (e2e fixture)", () => {
    const dir = mkdtempSync(path.join(tmpdir(), "cl-"));
    const file = path.join(dir, "links.json");
    writeFileSync(file, JSON.stringify(fixture));
    expect(chargingConfig({ CHARGING_LINKS_FILE: file }).nl).toHaveLength(4);
    expect(Object.keys(chargingConfig({}))).toEqual(expect.arrayContaining([...COUNTRY_SLUGS]));
  });
});

describe("charging links: config validation (scripts/charging-links.mjs)", () => {
  const ok = { job: "map", label: "Chargemap", url: "https://chargemap.com/", order: 1 };

  it("a missing list is fine (renders nothing)", () => {
    expect(validateChargingLinks("nl", undefined)).toEqual([]);
  });

  it("normalises defaults and sorts by order", () => {
    const out = validateChargingLinks("nl", [{ ...ok, order: 2 }, { ...ok, url: "https://www.plugshare.com/", label: "PlugShare", order: 1 }]);
    expect(out.map((l) => l.label)).toEqual(["PlugShare", "Chargemap"]);
    expect(out[0]).toMatchObject({ tool: null, official: false, utm: true });
  });

  it("rejects more than five links, http, unknown keys, partner ids and duplicates", () => {
    expect(() => validateChargingLinks("nl", Array.from({ length: 6 }, (_, i) => ({ ...ok, url: `https://e${i}.example/` })))).toThrow(/at most 5/);
    expect(() => validateChargingLinks("nl", [{ ...ok, url: "http://chargemap.com/" }])).toThrow(/https/);
    expect(() => validateChargingLinks("nl", [{ ...ok, logo: "x.png" }])).toThrow(/unknown key/);
    expect(() => validateChargingLinks("nl", [{ ...ok, affiliate_id: "x" }])).toThrow(/private config/);
    expect(() => validateChargingLinks("nl", [{ ...ok, url: "https://chargemap.com/?partner=1" }])).toThrow(/private config/);
    expect(() => validateChargingLinks("nl", [ok, ok])).toThrow(/duplicate/);
    expect(() => validateChargingLinks("nl", [{ ...ok, job: "Find Charger" }])).toThrow(/job/);
  });

  it("listings.mjs accepts the charging_links key in a country file", () => {
    expect(() => validateCountry("nl", { country: "nl", listings: [], charging_links: [ok] })).not.toThrow();
  });

  it("the committed JSON matches config/countries/*.yaml", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(serialize(loadChargingLinks()));
  });
});

describe("TRIP_FIT flag", () => {
  it("is on only for TRIP_FIT=1", () => {
    expect(tripFitEnabled({ TRIP_FIT: "1" })).toBe(true);
    expect(tripFitEnabled({ TRIP_FIT: "0" })).toBe(false);
    expect(tripFitEnabled({})).toBe(false);
  });
});
