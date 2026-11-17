import { test, expect } from "vitest";
import { readFileSync } from "node:fs";
import { getCatalogue } from "@/lib/catalogue";
import { toExploreRow } from "@/lib/explore-data";
import { showable } from "@/components/PriceBand";
import { rankHero, resolveProfile, comboKey, priceFit, presetsFor, presetCheck, siblingsOverBudget, PRESET_FIELDS, type UsedBands, type Answers } from "@/lib/shortlist";
import { defaultFilters } from "@/lib/state";

test("B3", () => {
  const raw = JSON.parse(readFileSync("/home/claude/rel2/2/shortlist_scores.json", "utf8")) as { variants: { variant_id: string; scores: Record<string, { score: number; band: string }> }[] };
  const rawBy = new Map(raw.variants.map((v) => [v.variant_id, v.scores]));
  const cat = getCatalogue();
  const all = cat.rows().map((r) => toExploreRow(r, cat.variantUsedPrices(), cat.shortlistScores()));
  const nowYear = Number(cat.generatedAt().slice(0, 4));
  const sets: [string, Answers, "NL" | "DE" | "FR", number | null, boolean][] = [
    ["road-tripper NL 15k", { role: "only", trips: "monthly", charge: "home", area: null, keep8: false }, "NL", 15000, false],
    ["road-tripper NL 35k", { role: "only", trips: "monthly", charge: "home", area: null, keep8: false }, "NL", 35000, false],
    ["daily-driver DE 25k rural", { role: "main", trips: "never", charge: "home", area: "countryside", keep8: false }, "DE", 25000, false],
    ["runabout FR none", { role: "second", trips: null, charge: "home", area: null, keep8: false }, "FR", null, false],
    ["kerbside NL 30k urban, presets off", { role: "only", trips: "often", charge: "public_only", area: "city", keep8: false }, "NL", 30000, true],
  ];
  for (const [name, a, cc, budget, off] of sets) {
    const usedBands: UsedBands = {};
    for (const b of cat.usedPrices()) { if (b.country !== cc || !showable(b, "EUR")) continue; (usedBands[b.generation_id] ??= []).push(b); }
    const rp = resolveProfile(a)!;
    const key = comboKey(rp);
    const q = { country: cc, cond: "any" as const, budget, filters: defaultFilters(), presetsOff: off ? [...PRESET_FIELDS] : [], usedBands, nowYear };
    const res = rankHero(all, rp, q, { hasScores: true });
    // Independent expectation straight from the JSON: same hard filters, then raw score, priced first.
    const presets = presetsFor(rp).filter((p) => !q.presetsOff.includes(p.field));
    const pf = (r: (typeof all)[number]) => priceFit(r, { ...q, yearMin: null, yearMax: null });
    const over = siblingsOverBudget(all, q, pf);
    const best = new Map<string, { id: string; s: number; priced: boolean; y: number; rr: number; name: string }>();
    for (const r of all) {
      if (presets.some((p) => presetCheck(r, p) === "fail")) continue;
      const { status, fit } = pf(r);
      if (status === "over" || (status === "unpriced" && over(r))) continue;
      const s = rawBy.get(r.variant_id)?.[key];
      if (!s || s.band === "ruled-out") continue;
      const c = { id: r.variant_id, s: s.score, priced: fit !== null, y: r.year_start, rr: r.real_range_km ?? 0, name: `${r.make_name} ${r.model_name}` };
      const cur = best.get(r.model_id);
      const better = !cur || Number(c.priced) - Number(cur.priced) > 0 || (c.priced === cur.priced && (c.s > cur.s || (c.s === cur.s && c.y > cur.y)));
      if (better) best.set(r.model_id, c);
    }
    const exp = [...best.values()].sort((x, y) => Number(y.priced) - Number(x.priced) || y.s - x.s || y.rr - x.rr || x.name.localeCompare(y.name)).slice(0, 10);
    const got = res.picks.map((p) => p.row.variant_id);
    const scoreOk = res.picks.every((p) => p.result.score === rawBy.get(p.row.variant_id)![key]!.score && p.result.band === rawBy.get(p.row.variant_id)![key]!.band);
    const sortedOk = res.picks.every((p, i) => i === 0 || res.picks[i - 1]!.price === null || p.price !== null ? i === 0 || Number(res.picks[i - 1]!.price !== null) > Number(p.price !== null) || res.picks[i - 1]!.result.score >= p.result.score : false);
    console.log(`${name} [${key}]: ${got.length} picks, priced ${res.priced}, shortlist ${res.shortlistN}; order==json ${JSON.stringify(got) === JSON.stringify(exp.map((e) => e.id))}; scores==json ${scoreOk}; sorted ${sortedOk}`);
    console.log("   " + res.picks.map((p) => `${p.rank ?? "-"}:${p.row.variant_id}=${p.result.score}${p.price ? "@" + p.price.amount : ""}`).join(" "));
    expect(got).toEqual(exp.map((e) => e.id));
    expect(scoreOk).toBe(true);
  }
});
