// Reviewer test (T-012, 2026-11-15): AGENTS.md says NL covers the whole public UI and only
// staff pages are EN-only. The existing test checks a few prefixes; this one checks every key.
import { describe, expect, it } from "vitest";
import en from "./en.json";
import nl from "./nl.json";

describe("NL dictionary coverage", () => {
  it("translates every public (non-staff) key", () => {
    const missing = Object.keys(en).filter((k) => !k.startsWith("staff.") && !(k in nl));
    expect(missing).toEqual([]);
  });

  it("has no empty NL strings", () => {
    const empty = Object.entries(nl as Record<string, string>).filter(([, v]) => !v.trim()).map(([k]) => k);
    expect(empty).toEqual([]);
  });
});
