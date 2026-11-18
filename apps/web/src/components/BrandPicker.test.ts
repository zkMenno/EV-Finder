import { describe, expect, it } from "vitest";
import { matchBrands } from "./BrandPicker";

const makes = [
  { id: "citroen", name: "Citroën" },
  { id: "kia", name: "Kia" },
  { id: "skoda", name: "Škoda" },
  { id: "tesla", name: "Tesla" },
];

describe("matchBrands", () => {
  it("returns every brand for an empty or blank query", () => {
    expect(matchBrands(makes, "")).toEqual(makes);
    expect(matchBrands(makes, "   ")).toEqual(makes);
  });
  it("matches anywhere in the name, ignoring case", () => {
    expect(matchBrands(makes, "SL").map((m) => m.id)).toEqual(["tesla"]);
  });
  it("ignores accents both ways", () => {
    expect(matchBrands(makes, "citroen").map((m) => m.id)).toEqual(["citroen"]);
    expect(matchBrands(makes, "škod").map((m) => m.id)).toEqual(["skoda"]);
  });
  it("returns nothing when no brand matches", () => {
    expect(matchBrands(makes, "zzz")).toEqual([]);
  });
});
