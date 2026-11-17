import { describe, expect, it } from "vitest";
import matrix from "@/fixtures/consumption-matrix.sample.json";
import towns from "@/fixtures/towns.sample.json";
import { COUNTRY_SLUGS } from "@/config/countries";
import { conditionsFor, fitAll, fitCar, hasTowns, MATRIX, mixFactor, passesTrip, rangeNeeded, temperatureBand, TOWNS, townsFor, TRIP_RUNG, wltpConsumption, type TripRow } from "./trip-model";
import { defaultTripSettings, type TripSettings } from "./trip-settings";

const s = (patch: Partial<TripSettings>): TripSettings => ({ ...defaultTripSettings(), ...patch });
const car = (patch: Partial<TripRow>): TripRow => ({ variant_id: "x", body: "hatchback", battery_kwh_net: 58, wltp_range_km: 424, year_end: null, charge_100_daily: false, ...patch });

describe("fixture matrix and towns", () => {
  it("are clearly labelled provisional fixtures", () => {
    expect(matrix.status).toBe("PROVISIONAL");
    expect(matrix.label).toMatch(/FIXTURE/);
    expect(towns.status).toBe("PROVISIONAL");
    expect(TRIP_RUNG).toBe("fixture-matrix");
  });

  it("covers 3 road bands × 5 temperature bands for every body, cold > mild", () => {
    expect(MATRIX.temperature_bands).toHaveLength(5);
    for (const [body, table] of Object.entries(MATRIX.bodies)) {
      for (const band of ["town", "rural", "motorway"] as const) {
        const row = table[band];
        expect(Object.keys(row).sort(), `${body}.${band}`).toEqual(MATRIX.temperature_bands.map((b) => b.id).sort());
        expect(row.t1!, `${body}.${band}`).toBeGreaterThan(row.t5!);
      }
      expect(table.motorway.t5!).toBeGreaterThan(table.town.t5!); // speed costs energy in summer
    }
  });

  it("has towns for every country, with ids only (no coordinates)", () => {
    // ES and IT (T-119) wait for sourced towns + climate (WS1: GeoNames + Meteostat); the fixture's
    // values are hand-typed, so we don't add more by hand. There the trip check is off (hasTowns).
    const pending = ["es", "it"];
    for (const c of COUNTRY_SLUGS) expect(hasTowns(c), c).toBe(!pending.includes(c));
    for (const c of COUNTRY_SLUGS.filter((c) => !pending.includes(c))) expect(townsFor(c).length).toBeGreaterThan(0);
    for (const t of TOWNS) {
      expect(t.id).toMatch(/^[a-z]{2}-[a-z0-9-]+$/);
      expect(Object.keys(t).sort()).toEqual(["country", "id", "jan_c", "jul_c", "name"]);
    }
  });
});

describe("conditions", () => {
  it("returns null without a trip", () => {
    expect(conditionsFor(defaultTripSettings(), "nl")).toBeNull();
  });

  it("road shares sum to 1; motorway share defaults from the driving profile", () => {
    const c = conditionsFor(s({ roundTripKm: 100, driving: "motorway" }), "nl")!;
    expect(c.shares.town + c.shares.rural + c.shares.motorway).toBeCloseTo(1);
    expect(c.shares.motorway).toBeCloseTo(0.7);
    expect(c.changes).toContain("trip.change.motorwayDefault");
    const d = conditionsFor(s({ roundTripKm: 100, motorwayPct: 20 }), "nl")!;
    expect(d.shares.motorway).toBeCloseTo(0.2);
    expect(d.changes).not.toContain("trip.change.motorwayDefault");
  });

  it("uses the home town's January temperature; unknown town falls back to the country's first", () => {
    const munich = conditionsFor(s({ roundTripKm: 100, townId: "de-munich" }), "de")!;
    expect(munich.winterC).toBe(-0.5);
    expect(munich.winterBand).toBe("t2");
    const fallback = conditionsFor(s({ roundTripKm: 100, townId: "zz-nowhere" }), "fr")!;
    expect(fallback.town.country).toBe("fr");
    const snow = conditionsFor(s({ roundTripKm: 100, townId: "de-munich", extras: ["snow"] }), "de")!;
    expect(snow.winterC).toBe(-6.5);
    expect(snow.winterBand).toBe("t1");
  });

  it("temperature bands", () => {
    expect(temperatureBand(-10)).toBe("t1");
    expect(temperatureBand(-5)).toBe("t1");
    expect(temperatureBand(-1)).toBe("t2");
    expect(temperatureBand(3)).toBe("t3");
    expect(temperatureBand(10)).toBe("t4");
    expect(temperatureBand(25)).toBe("t5");
  });

  it("towing and roof box raise consumption", () => {
    const base = conditionsFor(s({ roundTripKm: 100 }), "nl")!;
    const tow = conditionsFor(s({ roundTripKm: 100, extras: ["tow", "roofbox"] }), "nl")!;
    expect(mixFactor(tow, "t3", "hatchback")).toBeGreaterThan(mixFactor(base, "t3", "hatchback") * 1.5);
  });
});

describe("range you truly need", () => {
  it("winter needs more than summer, both on your mix and as WLTP", () => {
    const n = rangeNeeded(conditionsFor(s({ roundTripKm: 150, townId: "nl-amsterdam" }), "nl")!);
    // 150 km between an 80% daily charge and a 10% buffer → at least 150 / 0.7 ≈ 214 km.
    expect(n.summerKm).toBeGreaterThanOrEqual(150 / 0.7 - 0.01);
    expect(n.winterKm).toBeGreaterThan(n.summerKm);
    expect(n.winterWltpKm).toBeGreaterThan(n.winterKm);
    expect(n.winterWltpKm).toBeGreaterThan(n.summerWltpKm);
    expect(n.winterLow).toBeLessThan(n.winterKm);
    expect(n.winterHigh).toBeGreaterThan(n.winterKm);
    expect(n.whPerKm.motorway.winter).toBeGreaterThan(n.whPerKm.town.summer);
  });
});

describe("verdict per car", () => {
  const c = (km: number, extra: Partial<TripSettings> = {}) => conditionsFor(s({ roundTripKm: km, townId: "nl-amsterdam", ...extra }), "nl")!;

  it("WLTP battery consumption: usable / WLTP km, else the published figure, else unknown", () => {
    expect(wltpConsumption(car({ battery_kwh_net: 50, wltp_range_km: 400 }))).toBeCloseTo(12.5);
    expect(wltpConsumption(car({ wltp_range_km: null, consumption_kwh_100km: 16 }))).toBe(16);
    expect(wltpConsumption(car({ wltp_range_km: null, consumption_kwh_100km: null }))).toBeNull();
  });

  it("short trip ✓, long trip ✗ with the km it is short by, in between ⚠", () => {
    expect(fitCar(car({}), c(60)).verdict).toBe("ok");
    const long = fitCar(car({}), c(400));
    expect(long.verdict).toBe("fail");
    expect(long.shortKm!).toBeGreaterThan(0);
    // Find a distance that lands in the tight band.
    const verdicts = new Set<string>();
    for (let km = 50; km <= 400; km += 5) verdicts.add(fitCar(car({}), c(km)).verdict);
    expect(verdicts).toEqual(new Set(["ok", "tight", "fail"]));
  });

  it("verdict thresholds follow the spec: ✓ needs a 15% margin and the band above the need", () => {
    for (let km = 20; km <= 400; km += 10) {
      const f = fitCar(car({}), c(km));
      if (f.verdict === "ok") expect(f.margin!).toBeGreaterThanOrEqual(0.15);
      if (f.verdict === "fail") expect(f.margin!).toBeLessThan(0);
      if (f.verdict === "tight") expect(f.margin!).toBeGreaterThanOrEqual(0);
    }
  });

  it("no battery or no consumption → unknown, never a guess", () => {
    expect(fitCar(car({ battery_kwh_net: null }), c(50)).verdict).toBe("unknown");
    expect(fitCar(car({ wltp_range_km: null, consumption_kwh_100km: null }), c(50)).verdict).toBe("unknown");
    expect(passesTrip(fitCar(car({ battery_kwh_net: null }), c(50)))).toBe(false);
  });

  it("charge-to-100% batteries start full; used cars assume 90% health; keep 8+ years 85%", () => {
    const nmc = fitCar(car({}), c(100));
    const lfp = fitCar(car({ charge_100_daily: true }), c(100));
    expect(lfp.haveKwh!).toBeGreaterThan(nmc.haveKwh!);
    expect(fitCar(car({ year_end: 2020 }), c(100), MATRIX, 2026).health).toBe(0.9);
    expect(fitCar(car({ year_end: null }), c(100), MATRIX, 2026).health).toBe(1);
    expect(fitCar(car({}), c(100, { extras: ["keep8"] })).health).toBe(0.85);
  });

  it("winter range is below summer range; SUVs use more on the motorway", () => {
    const f = fitCar(car({}), c(100));
    expect(f.winterKm!).toBeLessThan(f.summerKm!);
    const mw = c(100, { motorwayPct: 90 });
    expect(fitCar(car({ body: "suv" }), mw).winterKm!).toBeLessThan(fitCar(car({ body: "sedan" }), mw).winterKm!);
  });

  it("fitAll keys every row; the filter keeps ✓ and ⚠ only", () => {
    const rows = [car({ variant_id: "a" }), car({ variant_id: "b", battery_kwh_net: 20, wltp_range_km: 150 })];
    const m = fitAll(rows, c(200));
    expect([...m.keys()]).toEqual(["a", "b"]);
    expect(passesTrip(m.get("b"))).toBe(false);
    expect(passesTrip({ ...m.get("a")!, verdict: "tight" })).toBe(true);
  });
});
