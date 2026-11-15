import { readFileSync } from "node:fs";
import type { Source } from "@ev/schema";
import { describe, expect, it } from "vitest";
import { attributionOf, buildRegistry, loadRegistry, OUT_FILE, serialize } from "../../scripts/sources.mjs";
import { creditFor, credits, linkParts, registry } from "./credits";

const KILOWATT = "Open EV Data (https://github.com/KilowattApp/open-ev-data)";

// Sources as a release lists them (release 1 plus the wave-5 additions).
const release: Source[] = [
  { id: "openev", name: "Open EV Data", licence: "CDLA-Permissive-2.0", url: "https://github.com/open-ev-data/open-ev-data-dataset", attribution: "Contains data from OpenEV Data (open-ev-data-dataset), CDLA-Permissive-2.0." },
  { id: "kilowatt-openev", name: "Open EV Data (KilowattApp)", licence: "MIT-with-attribution" },
  { id: "rdw", name: "RDW Open Data", licence: "CC0-1.0", attribution: "Bron: RDW Open Data (opendata.rdw.nl), CC0." },
  { id: "eea", name: "EEA CO2 monitoring", licence: "CC-BY-4.0", attribution: "Contains data from the European Environment Agency. CC BY 4.0." },
  { id: "kba-fz10", name: "KBA FZ10", licence: "dl-de/by-2-0" },
  { id: "dft-veh", name: "DfT vehicle licensing", licence: "OGL-UK-3.0" },
  { id: "ademe", name: "ADEME Car Labelling", licence: "Licence-Ouverte-2.0" },
  { id: "seed-manual", name: "EV Finder seed", licence: "CC-BY-4.0", attribution: "EV Finder contributors" },
];

const all = (id: string) => creditFor(release.find((s) => s.id === id)!).lines.join(" | ");

describe("registry (data/sources.yaml → sources.generated.json)", () => {
  it("the generated JSON matches the YAML (run `node scripts/sources.mjs` after editing)", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(serialize(loadRegistry()));
  });

  it("extracts required attribution from the registry's terms", () => {
    expect(registry["kilowatt-openev"]?.attribution).toBe(KILOWATT);
    expect(registry["kba-fz10"]?.attribution).toBe("© Kraftfahrt-Bundesamt, Flensburg");
    expect(registry["dft-veh"]?.attribution).toMatch(/^Contains public sector information licensed under the Open Government Licence v3\.0/);
    expect(attributionOf({ attribution: "Explicit" , terms: "attribution 'other' required" })).toBe("Explicit");
    expect(attributionOf({ terms: "No quoted text." })).toBeUndefined();
  });

  it("rejects malformed registries", () => {
    expect(() => buildRegistry({})).toThrow();
    expect(() => buildRegistry({ sources: [{ id: "a", name: "A", licence: "x" }, { id: "a", name: "B", licence: "y" }] })).toThrow(/duplicate/);
  });
});

describe("credits", () => {
  it("Open EV Data (KilowattApp) always carries its required visible attribution", () => {
    expect(all("kilowatt-openev")).toContain(KILOWATT);
    // Even if a release writes its own text without it, and the registry is empty.
    const c = creditFor({ id: "kilowatt-openev", name: "x", licence: "MIT-with-attribution", attribution: "Charge curves from KilowattApp." }, {});
    expect(c.lines.join(" ")).toContain(KILOWATT);
  });

  it("keeps the CDLA dataset's own attribution", () => {
    expect(all("openev")).toContain("CDLA-Permissive-2.0");
  });

  it("RDW uses the interim Q-037 wording, not the release's 'Bron: RDW'", () => {
    expect(all("rdw")).toBe("Dutch vehicle register (RDW open data, CC0)");
  });

  it("adds the required EEA, KBA, DfT and ADEME notices", () => {
    expect(all("eea")).toContain("© European Union, EEA, CC BY 4.0");
    expect(all("eea")).toContain("European Environment Agency");
    expect(all("kba-fz10")).toBe("© Kraftfahrt-Bundesamt, Flensburg");
    expect(all("dft-veh")).toContain("Open Government Licence v3.0");
    expect(all("ademe")).toContain("Licence Ouverte");
  });

  it("does not repeat a notice the release already includes", () => {
    const c = creditFor({ id: "kba-fz10", name: "KBA", licence: "dl-de/by-2-0", attribution: "© Kraftfahrt-Bundesamt, Flensburg (FZ10, 2026)" });
    expect(c.lines).toEqual(["© Kraftfahrt-Bundesamt, Flensburg (FZ10, 2026)"]);
  });

  it("unknown sources fall back to name and licence; licence labels and links are per licence", () => {
    const c = creditFor({ id: "new-src", name: "New source", licence: "CC-BY-4.0" }, {});
    expect(c.lines).toEqual(["New source, CC BY 4.0"]);
    expect(c.licenceUrl).toBe("https://creativecommons.org/licenses/by/4.0/");
  });

  it("lists every release source once, ours last", () => {
    const list = credits(release);
    expect(list.map((c) => c.id).sort()).toEqual(release.map((s) => s.id).sort());
    expect(list.at(-1)?.id).toBe("seed-manual");
  });

  it("linkParts keeps URLs visible as text", () => {
    expect(linkParts(KILOWATT)).toEqual([
      { text: "Open EV Data (" },
      { text: "https://github.com/KilowattApp/open-ev-data", href: "https://github.com/KilowattApp/open-ev-data" },
      { text: ")" },
    ]);
  });
});
