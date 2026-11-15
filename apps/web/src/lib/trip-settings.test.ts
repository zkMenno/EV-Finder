import { describe, expect, it } from "vitest";
import { memoryStorage, type KeyValueStorage } from "./storage";
import { TRIP_KEY } from "./state";
import { defaultTripSettings, hasTrip, normalizeTripSettings, readTripSettings, writeTripSettings } from "./trip-settings";

describe("trip settings (browser only)", () => {
  it("normalises junk to defaults and keeps valid answers", () => {
    expect(normalizeTripSettings(null)).toEqual(defaultTripSettings());
    const s = normalizeTripSettings({ role: "main", longTrips: "bogus", extras: ["tow", "x", "snow"], roundTripKm: "150", motorwayPct: 140, townId: "nl-groningen" });
    expect(s.role).toBe("main");
    expect(s.longTrips).toBeNull();
    expect(s.extras).toEqual(["tow", "snow"]);
    expect(s.roundTripKm).toBe(150);
    expect(s.motorwayPct).toBe(100);
    expect(s.townId).toBe("nl-groningen");
    expect(normalizeTripSettings({ roundTripKm: 99999 }).roundTripKm).toBe(2000);
    expect(normalizeTripSettings({ roundTripKm: 0 }).roundTripKm).toBeNull();
  });

  it("never keeps coordinates, addresses or unknown keys", () => {
    const s = normalizeTripSettings({ townId: "52.37,4.89", lat: 52.37, lon: 4.89, address: "Damrak 1", roundTripKm: 80 });
    expect(s.townId).toBeNull();
    const json = JSON.stringify(s);
    expect(json).not.toMatch(/52\.37|4\.89|Damrak|"lat"|"lon"|address/);
    expect(Object.keys(s).sort()).toEqual(["charging", "driving", "extras", "longTrips", "motorwayPct", "role", "roundTripKm", "townId", "v"]);
  });

  it("round-trips through storage; corrupt, empty and throwing storage are safe", () => {
    const mem = memoryStorage();
    expect(readTripSettings(mem)).toBeNull();
    writeTripSettings({ ...defaultTripSettings(), roundTripKm: 120, townId: "de-berlin" }, mem);
    expect(readTripSettings(mem)?.roundTripKm).toBe(120);
    mem.setItem(TRIP_KEY, "{not json");
    expect(readTripSettings(mem)).toBeNull();
    mem.setItem(TRIP_KEY, "");
    expect(readTripSettings(mem)).toBeNull();
    const broken: KeyValueStorage = {
      getItem: () => {
        throw new Error("denied");
      },
      setItem: () => {
        throw new Error("quota");
      },
    };
    expect(readTripSettings(broken)).toBeNull();
    expect(writeTripSettings(defaultTripSettings(), broken)).toBe(false);
    expect(readTripSettings(null)).toBeNull();
  });

  it("hasTrip needs a round trip", () => {
    expect(hasTrip(null)).toBe(false);
    expect(hasTrip(defaultTripSettings())).toBe(false);
    expect(hasTrip({ ...defaultTripSettings(), roundTripKm: 10 })).toBe(true);
  });
});
