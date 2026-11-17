import { describe, expect, it } from "vitest";
import de from "@/i18n/de.json";
import en from "@/i18n/en.json";
import es from "@/i18n/es.json";
import fr from "@/i18n/fr.json";
import it_ from "@/i18n/it.json";
import nl from "@/i18n/nl.json";
import { makeT, type Dict } from "@/i18n/t";
import { nerdValue, numberParts } from "./nerd-value";

const tEn = makeT(en as Dict);
const tNl = makeT({ ...en, ...nl } as Dict);
const num = (field: string, raw: number) => ({ field, raw });

describe("nerdValue (T-097)", () => {
  it("shows the car's own DC figure in km per 20 min, not the scaled km/h", () => {
    // road-tripper scores dc_km_per_20min × 3; the table must still read 387, not 1,161.
    expect(nerdValue(num("dc_km_per_20min", 387.2), tEn, "en")).toBe("387 km in 20 min");
    expect(nerdValue(num("dc_km_per_20min", 387.2), tNl, "nl")).toBe("387 km in 20 min");
  });

  it("uses the raw kWh/100 km, not ×10 Wh/km", () => {
    expect(nerdValue(num("consumption_kwh_100km", 16.4), tEn, "en")).toBe("16.4 kWh/100 km");
    expect(nerdValue(num("consumption_kwh_100km", 16.4), tNl, "nl")).toBe("16,4 kWh/100 km");
  });

  it("gives every numeric rule field a metric unit", () => {
    expect(nerdValue(num("real_range_km", 412), tEn, "en")).toBe("412 km");
    expect(nerdValue(num("boot_l", 470), tEn, "en")).toBe("470 L");
    expect(nerdValue(num("ac_kw", 11), tEn, "en")).toBe("11 kW");
    expect(nerdValue(num("length_mm", 4250), tNl, "nl")).toBe("4,25 m");
    // The release's derived estimates (T-114): winter range in km, real efficiency in Wh/km.
    expect(nerdValue(num("winter_range_km", 301.6), tEn, "en")).toBe("302 km in winter (est.)");
    expect(nerdValue(num("winter_range_km", 301.6), tNl, "nl")).toBe("302 km in de winter (schatting)");
    expect(nerdValue(num("real_wh_km", 187.4), tEn, "en")).toBe("187 Wh/km");
  });

  it("unknown stays 'not known yet' (NL: nog onbekend)", () => {
    expect(nerdValue({ field: "dc_km_per_20min", raw: null }, tNl, "nl")).toBe("nog onbekend");
  });

  it("labels words and yes/no instead of showing raw ids", () => {
    expect(nerdValue({ field: "heat_pump", raw: "option" }, tNl, "nl")).toBe("optie");
    expect(nerdValue({ field: "cooling_id", raw: "air" }, tEn, "en")).toBe("air");
    expect(nerdValue({ field: "fast_on_400v", raw: true }, tNl, "nl")).toBe("ja");
  });

  it("has the unit strings in all six languages, each with {v}", () => {
    for (const d of [en, nl, de, fr, es, it_] as Record<string, string>[]) {
      for (const k of Object.keys(en).filter((k) => k.startsWith("hero.nerd.unit."))) {
        expect(d[k], k).toContain("{v}");
      }
    }
  });
});

describe("numberParts (T-097 review: German table clipped 16 px on CI)", () => {
  it("keeps numbers whole and leaves words breakable", () => {
    expect(numberParts("387 km in 20 Min.")).toEqual([
      { text: "387", num: true }, { text: " km in ", num: false }, { text: "20", num: true }, { text: " Min.", num: false },
    ]);
    expect(numberParts("1.161,6 kWh")).toEqual([{ text: "1.161,6", num: true }, { text: " kWh", num: false }]);
    expect(numberParts("noch unbekannt")).toEqual([{ text: "noch unbekannt", num: false }]);
    expect(numberParts("4,25 m")[0]).toEqual({ text: "4,25", num: true });
  });
});
