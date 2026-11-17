// T-125: property tests for the logic that turns release data into what a buyer sees. Each
// property runs on hundreds of generated inputs with a fixed seed (same cases on every machine and
// in CI). To explore further: FC_SEED=<n> FC_RUNS=<n> pnpm test properties. A failing case found
// this way is kept below as a plain regression test.
import fc from "fast-check";
import { describe, expect, it } from "vitest";
import type { Lang } from "@/config/countries";
import en from "@/i18n/en.json";
import de from "@/i18n/de.json";
import es from "@/i18n/es.json";
import fr from "@/i18n/fr.json";
import it_ from "@/i18n/it.json";
import nl from "@/i18n/nl.json";
import type { ExploreRow } from "./explore-data";
import { compactBands } from "./explore-data";
import { displayName, sortRows } from "./filters";
import { loanPayment } from "./finance";
import { DASH, formatMoney, formatNumber, localeFor } from "./format";
import { BUDGET_MAX, heroFromSearchParams, heroToSearchParams, mergeHeroIntoUrl, type HeroState } from "./hero-state";
import {
  AREAS,
  CHARGES,
  comboKey,
  CONDITIONS,
  isComplete,
  PRESET_FIELDS,
  rankHero,
  resolveProfile,
  ROLES,
  TRIPS,
  variantFit,
  type Answers,
  type ResolvedProfile,
} from "./shortlist";
import { SPEC_FIELDS } from "./spec-diff";
import {
  BODIES,
  defaultFilters,
  defaultState,
  deserializeState,
  ERAS,
  fromSearchParams,
  LEVELS,
  normalizeState,
  NUMERIC_FILTERS,
  SEGMENTS,
  serializeState,
  SORT_KEYS,
  toSearchParams,
  type ExploreFilters,
  type ExploreState,
} from "./state";
import { parseVariantUsedPrices } from "./variant-prices";
import { compareUrl, parseCompareIds } from "@/app/[country]/[lang]/compare/_lib/ids";
import { COMPARE_MAX, compareHref } from "./compare-store";

// `|| default`, not `?? default`: an empty FC_SEED must not quietly become seed 0.
fc.configureGlobal({ seed: Number(process.env.FC_SEED) || 20261117, numRuns: Number(process.env.FC_RUNS) || 200 });

// ── Generators ──────────────────────────────────────────────────────────────────────────────

const subsetInOrder = <T,>(all: readonly T[]) => fc.subarray([...all]);
const id = fc.stringMatching(/^[a-z0-9]{1,6}(-[a-z0-9]{1,4}){0,2}$/);
const idList = fc.uniqueArray(id, { maxLength: 4 }).map((a) => [...a].sort());
const filterNumber = fc.option(fc.oneof(fc.integer({ min: 0, max: 1_000_000 }), fc.double({ min: 0, max: 1e6, noNaN: true, noDefaultInfinity: true })), {
  nil: null,
});

const filtersArb: fc.Arbitrary<ExploreFilters> = fc
  .record({
    nums: fc.tuple(...NUMERIC_FILTERS.map(() => filterNumber)),
    eras: subsetInOrder(ERAS),
    segments: subsetInOrder(SEGMENTS),
    bodies: subsetInOrder(BODIES),
    makes: idList,
    excludeMakes: idList,
    voltageClasses: idList,
    chemistries: idList,
    coolings: idList,
    fast400: fc.boolean(),
    charge100: fc.boolean(),
    tripFit: fc.boolean(),
  })
  .map(({ nums, ...rest }) => {
    const f = { ...defaultFilters(), ...rest };
    NUMERIC_FILTERS.forEach((k, i) => (f[k] = nums[i]!));
    return f;
  });

// A direction only means something with a sort key; the URL carries it inside `sort=-key`.
const stateArb: fc.Arbitrary<ExploreState> = fc
  .record({
    filters: filtersArb,
    sort: fc.option(fc.constantFrom(...SORT_KEYS), { nil: null }),
    desc: fc.boolean(),
    view: fc.constantFrom("table" as const, "cards" as const),
    level: fc.constantFrom(...LEVELS),
    pay: fc.constantFrom("buy" as const, "loan" as const, "lease" as const),
  })
  .map(({ desc, ...s }) => ({ v: 1 as const, ...s, dir: s.sort && desc ? ("desc" as const) : ("asc" as const) }));

const answersArb: fc.Arbitrary<Answers> = fc
  .record({
    role: fc.option(fc.constantFrom(...ROLES), { nil: null }),
    trips: fc.option(fc.constantFrom(...TRIPS), { nil: null }),
    charge: fc.option(fc.constantFrom(...CHARGES), { nil: null }),
    area: fc.option(fc.constantFrom(...AREAS), { nil: null }),
    keep8: fc.boolean(),
  })
  // A second car never asks about long trips, so the URL never carries them.
  .map((a) => (a.role === "second" ? { ...a, trips: null } : a));

const heroArb: fc.Arbitrary<HeroState> = fc.record({
  answers: answersArb,
  budget: fc.option(fc.integer({ min: 1, max: BUDGET_MAX }), { nil: null }),
  cond: fc.constantFrom(...CONDITIONS),
  presetsOff: subsetInOrder(PRESET_FIELDS).map((a) => [...a].sort()),
  filters: filtersArb.map((f) => ({ ...f, tripFit: false })), // trip fit is parked (Decision 051)
});

/** Every complete picker answer set → its profile. */
const PROFILES: ResolvedProfile[] = [];
for (const role of ROLES)
  for (const trips of [null, ...TRIPS])
    for (const charge of CHARGES)
      for (const area of [null, ...AREAS])
        for (const keep8 of [false, true]) {
          const a: Answers = { role, trips, charge, area, keep8 };
          if (isComplete(a)) PROFILES.push(resolveProfile(a)!);
        }

function baseRow(i: number): ExploreRow {
  return {
    variant_id: `v${i}`,
    variant_name: `v${i}`,
    generation_id: `g${i}`,
    generation_name: "gen",
    model_id: `m${i}`,
    model_name: `Model ${i}`,
    make_id: "make",
    make_name: "Make",
    year_start: 2022,
    era: "2021-22",
    body: "hatchback",
    quality_tier: "sourced",
    provenance: {},
  } as ExploreRow;
}

/** The fields the shortlist rules read (factors, gates, presets, penalties). */
const knownValues = fc.record(
  {
    dc_km_per_20min: fc.integer({ min: 0, max: 600 }),
    real_range_km: fc.integer({ min: 50, max: 800 }),
    boot_l: fc.integer({ min: 0, max: 900 }),
    consumption_kwh_100km: fc.double({ min: 10, max: 35, noNaN: true }),
    ac_kw: fc.double({ min: 2, max: 22, noNaN: true }),
    length_mm: fc.integer({ min: 2500, max: 5500 }),
    seats: fc.integer({ min: 2, max: 9 }),
    towing_kg: fc.integer({ min: 0, max: 3500 }),
    kerb_mass_kg: fc.integer({ min: 800, max: 3200 }),
    heat_pump: fc.constantFrom("standard", "option", "none"),
    cooling_id: fc.constantFrom("liquid", "refrigerant", "air", "passive"),
    fast_on_400v: fc.boolean(),
    charge_100_daily: fc.boolean(),
    voltage_class_id: fc.constantFrom("400v", "800v"),
  },
  { requiredKeys: [] },
);
const FIELD_KEYS = ["dc_km_per_20min", "real_range_km", "boot_l", "consumption_kwh_100km", "ac_kw", "length_mm", "seats", "towing_kg", "kerb_mass_kg", "heat_pump", "cooling_id", "fast_on_400v", "charge_100_daily", "voltage_class_id"] as const;

const heroQuery = { country: "NL" as const, cond: "any" as const, budget: null, filters: defaultFilters(), presetsOff: [], nowYear: 2026 };
/** Scores come from the release (Decision 065): give the row a release score for this profile. */
const withScore = (row: ExploreRow, rp: ResolvedProfile, score = 50): ExploreRow => ({ ...row, shortlist: { s: { [comboKey(rp)]: [score, "consider"] } } });
const qualifies = (row: ExploreRow, rp: ResolvedProfile) => rankHero([withScore(row, rp)], rp, heroQuery, { hasScores: true }).qualifying === 1;

// ── 1. URL state round-trips (design principle 3: state never gets lost) ───────────────────

describe("Explore state", () => {
  it("URL encode → decode gives the same state", () => {
    fc.assert(
      fc.property(stateArb, (s) => {
        expect(fromSearchParams(toSearchParams(s))).toEqual(s);
      }),
    );
  });

  it("storage encode → decode gives the same state", () => {
    fc.assert(
      fc.property(stateArb, (s) => {
        expect(deserializeState(serializeState(s))).toEqual(s);
      }),
    );
  });

  it("parsing any URL never throws, and the result round-trips", () => {
    const keys = fc.constantFrom("price", "range", "era", "seg", "body", "sort", "view", "level", "pay", "make", "volt", "trip", "c100", "x");
    fc.assert(
      fc.property(fc.dictionary(keys, fc.string()), (q) => {
        const s = fromSearchParams(q);
        expect(fromSearchParams(toSearchParams(s))).toEqual(s);
      }),
    );
  });

  it("normalising any stored junk never throws and is idempotent", () => {
    fc.assert(
      fc.property(fc.anything(), (x) => {
        const s = normalizeState(x);
        expect(normalizeState(s)).toEqual(s);
      }),
    );
  });
});

describe("hero state", () => {
  it("URL encode → decode gives the same hero state", () => {
    fc.assert(
      fc.property(heroArb, (h) => {
        expect(heroFromSearchParams(heroToSearchParams(h))).toEqual(h);
      }),
    );
  });

  it("merging the hero into a URL keeps Explore's own sort, view, level and price mode", () => {
    fc.assert(
      fc.property(heroArb, stateArb, (h, s) => {
        const own = new URLSearchParams();
        for (const k of ["sort", "view", "level", "pay"]) {
          const v = toSearchParams(s).get(k);
          if (v) own.set(k, v);
        }
        const merged = new URL("https://x.test" + mergeHeroIntoUrl(`https://x.test/nl/en?${own}`, h));
        for (const k of ["sort", "view", "level", "pay"]) expect(merged.searchParams.get(k)).toBe(own.get(k));
        expect(heroFromSearchParams(merged.searchParams)).toEqual(h);
      }),
    );
  });
});

describe("compare URL", () => {
  const variantId = fc.stringMatching(/^[a-z0-9][a-z0-9-]{0,20}$/);
  const ids = fc.uniqueArray(variantId, { maxLength: COMPARE_MAX });

  it("compare link → ids gives the same cars in the same order (tray link and page links)", () => {
    fc.assert(
      fc.property(ids, fc.boolean(), fc.constantFrom(null, "buy", "loan", "lease"), (list, diff, pay) => {
        const tray = new URL("https://x.test" + compareHref("/nl/en", list.map((id) => ({ id, label: id }))));
        expect(parseCompareIds(tray.searchParams.get("ids"))).toEqual(list);
        const page = new URL("https://x.test" + compareUrl("/nl/en", list, diff, pay));
        expect(parseCompareIds(page.searchParams.get("ids"))).toEqual(list);
        expect(page.searchParams.get("diff")).toBe(diff ? "1" : null);
        expect(page.searchParams.get("pay")).toBe(pay === "loan" || pay === "lease" ? pay : null);
      }),
    );
  });

  it("parsing any ids parameter never throws and keeps at most the compare maximum", () => {
    fc.assert(
      fc.property(fc.oneof(fc.string(), fc.array(fc.string())), (raw) => {
        const out = parseCompareIds(raw);
        expect(out.length).toBeLessThanOrEqual(COMPARE_MAX);
        expect(new Set(out).size).toBe(out.length);
        expect(parseCompareIds(out.join(","))).toEqual(out);
      }),
    );
  });
});

// ── 2. The hero never drops a car for missing data (Decision 055) ──────────────────────────

describe("hero ranking", () => {
  it(`a scored car we know nothing else about qualifies for every profile (${PROFILES.length} answer sets)`, () => {
    for (const rp of PROFILES) expect(qualifies(baseRow(0), rp), rp.base.id).toBe(true);
  });

  it("removing any data from a car that qualifies never rules it out", () => {
    fc.assert(
      fc.property(knownValues, fc.subarray([...FIELD_KEYS], { minLength: 1 }), fc.constantFrom(...PROFILES), (vals, drop, rp) => {
        const full = { ...baseRow(1), ...vals } as ExploreRow;
        fc.pre(qualifies(full, rp));
        const less = { ...full } as Record<string, unknown>;
        for (const k of drop) delete less[k];
        expect(qualifies(less as ExploreRow, rp)).toBe(true);
      }),
    );
  });

  it("ranks are 1..n, at most 10, one card per model, best score first", () => {
    fc.assert(
      fc.property(fc.array(fc.tuple(knownValues, fc.integer({ min: 0, max: 1000 })), { minLength: 1, maxLength: 25 }), fc.constantFrom(...PROFILES), (vals, rp) => {
        const rows = vals.map(([v, sc], i) => withScore({ ...baseRow(i % 7), variant_id: `v${i}`, ...v } as ExploreRow, rp, sc / 10));
        const { picks, qualifying } = rankHero(rows, rp, heroQuery, { hasScores: true });
        expect(picks.length).toBe(Math.min(10, qualifying));
        expect(picks.map((p) => p.rank)).toEqual(picks.map((_, i) => i + 1));
        expect(new Set(picks.map((p) => p.row.model_id)).size).toBe(picks.length);
        for (let i = 1; i < picks.length; i++) expect(picks[i - 1]!.result.score).toBeGreaterThanOrEqual(picks[i]!.result.score);
      }),
    );
  });
});

// ── 3. Sorting is stable and total ─────────────────────────────────────────────────────────

describe("Explore sort", () => {
  const sortable = fc.record(
    {
      real_range_km: fc.integer({ min: 100, max: 110 }), // narrow range → many ties
      battery_kwh_net: fc.integer({ min: 40, max: 42 }),
      dc_km_per_20min: fc.integer({ min: 200, max: 203 }),
      year_start: fc.integer({ min: 2018, max: 2020 }),
      model_name: fc.constantFrom("ID.3", "Ioniq 5", "e-208", "Zoë", "Model 3"),
    },
    { requiredKeys: ["year_start", "model_name"] },
  );
  const keys = ["name", "years", "range", "battery", "dc"] as const;

  it("returns the same cars, missing values last, sorted, ties in catalogue order", () => {
    fc.assert(
      fc.property(fc.array(sortable, { maxLength: 30 }), fc.constantFrom(...keys), fc.constantFrom("asc" as const, "desc" as const), (vals, key, dir) => {
        const rows = vals.map((v, i) => ({ ...baseRow(i), ...v }) as ExploreRow);
        const out = sortRows(rows, key, dir, "NL");
        expect([...out].sort((a, b) => a.variant_id.localeCompare(b.variant_id))).toEqual([...rows].sort((a, b) => a.variant_id.localeCompare(b.variant_id)));
        const idx = (r: ExploreRow) => rows.indexOf(r);
        const val = (r: ExploreRow): number | string | null =>
          key === "name" ? displayName(r).toLowerCase() : key === "years" ? r.year_start : key === "range" ? (r.real_range_km ?? null) : key === "battery" ? (r.battery_kwh_net ?? null) : (r.dc_km_per_20min ?? null);
        let seenMissing = false;
        for (let i = 0; i < out.length; i++) {
          if (val(out[i]!) === null) seenMissing = true;
          else expect(seenMissing, "a known value after a missing one").toBe(false);
          if (i === 0) continue;
          const a = val(out[i - 1]!);
          const b = val(out[i]!);
          if (a === null || b === null) continue;
          const c = typeof a === "string" ? a.localeCompare(b as string) : a - (b as number);
          expect(dir === "asc" ? c <= 0 : c >= 0).toBe(true);
          if (c === 0) expect(idx(out[i - 1]!)).toBeLessThan(idx(out[i]!));
        }
        // Total: sorting again changes nothing.
        expect(sortRows(out, key, dir, "NL")).toEqual(out);
      }),
    );
  });
});

// ── 4. The loan estimate moves the right way ───────────────────────────────────────────────

describe("loan estimate", () => {
  const price = fc.integer({ min: 0, max: 200_000 });
  const apr = fc.double({ min: 0, max: 30, noNaN: true });
  const term = fc.constantFrom(12, 24, 36, 48, 60, 72, 84);
  const deposit = fc.integer({ min: 0, max: 100 });
  const eps = 1e-6;

  it("a dearer car never costs less a month", () => {
    fc.assert(
      fc.property(price, price, apr, term, deposit, (p1, p2, aprPct, termMonths, depositPct) => {
        const [lo, hi] = p1 <= p2 ? [p1, p2] : [p2, p1];
        const a = loanPayment({ price: lo, aprPct, termMonths, depositPct })!;
        const b = loanPayment({ price: hi, aprPct, termMonths, depositPct })!;
        expect(a.monthly).toBeLessThanOrEqual(b.monthly + eps);
      }),
    );
  });

  it("a higher rate never costs less a month, and credit never costs less than nothing", () => {
    fc.assert(
      fc.property(price, apr, apr, term, deposit, (p, r1, r2, termMonths, depositPct) => {
        const [lo, hi] = r1 <= r2 ? [r1, r2] : [r2, r1];
        const a = loanPayment({ price: p, aprPct: lo, termMonths, depositPct })!;
        const b = loanPayment({ price: p, aprPct: hi, termMonths, depositPct })!;
        expect(a.monthly).toBeLessThanOrEqual(b.monthly + eps);
        expect(a.costOfCredit).toBeGreaterThanOrEqual(-eps * termMonths);
        expect(a.deposit + a.principal).toBeCloseTo(p, 6);
        expect(Number.isFinite(b.monthly)).toBe(true);
      }),
    );
  });
});

// ── 5. Used price bands: P25 ≤ median ≤ P75 everywhere the buyer sees them ─────────────────

describe("used price bands", () => {
  const rawBand = fc.record({
    build_year: fc.integer({ min: 2012, max: 2026 }),
    p25: fc.option(fc.integer({ min: -1000, max: 80_000 }), { nil: null }),
    median: fc.integer({ min: -1000, max: 80_000 }),
    p75: fc.option(fc.integer({ min: -1000, max: 80_000 }), { nil: null }),
    currency: fc.constantFrom("EUR", "GBP"),
    samples: fc.integer({ min: 0, max: 400 }),
    method: fc.constantFrom("listings", "model"),
    confidence: fc.constantFrom("high", "medium", "low"),
  });
  const doc = fc.array(fc.record({ variant_id: id, bands: fc.dictionary(fc.constantFrom("NL", "DE", "FR", "UK"), fc.array(rawBand, { maxLength: 6 })) }), { maxLength: 5 }).map((variants) => ({ variants }));

  it("parsed bands are ordered: P25 ≤ median ≤ P75, oldest build year first, median > 0", () => {
    fc.assert(
      fc.property(doc, (d) => {
        for (const per of parseVariantUsedPrices(d).values())
          for (const list of Object.values(per)) {
            for (const b of list) {
              expect(b.median).toBeGreaterThan(0);
              if (b.p25 !== null) expect(b.p25).toBeLessThanOrEqual(b.median);
              if (b.p75 !== null) expect(b.p75).toBeGreaterThanOrEqual(b.median);
            }
            expect(list.map((b) => b.build_year)).toEqual([...list.map((b) => b.build_year)].sort((a, b) => a - b));
          }
      }),
    );
  });

  it("the price the hero shows sits inside its own band", () => {
    fc.assert(
      fc.property(doc, fc.option(fc.integer({ min: 1, max: 80_000 }), { nil: null }), (d, budget) => {
        for (const [vid, per] of parseVariantUsedPrices(d)) {
          const row = { ...baseRow(0), variant_id: vid, year_start: 2012, year_end: 2026, used_bands: compactBands(per) } as ExploreRow;
          for (const cc of Object.keys(per)) {
            const fit = variantFit(row, cc as "NL", budget);
            if (!fit) continue;
            if (budget !== null) expect(fit.amount).toBeLessThanOrEqual(budget);
            if (fit.low !== null) expect(fit.low).toBeLessThanOrEqual(fit.amount);
            if (fit.high !== null) expect(fit.high).toBeGreaterThanOrEqual(fit.amount);
          }
        }
      }),
    );
  });

  // Regression (found by the property above): a band with P25 above its median was passed through
  // as is, so a card could read "€20,000 (€25,000–€22,000)".
  it("drops a quartile on the wrong side of the median instead of showing it", () => {
    const parsed = parseVariantUsedPrices({ variants: [{ variant_id: "a", bands: { NL: [{ build_year: 2020, p25: 25_000, median: 20_000, p75: 19_000 }] } }] });
    expect(parsed.get("a")!.NL![0]).toMatchObject({ p25: null, median: 20_000, p75: null });
  });
});

// ── 6. Formatters: no NaN/undefined on screen, locale-correct in all 6 languages, metric ──

const LANGS: Lang[] = ["en", "nl", "de", "fr", "es", "it"];

/** Reads a formatted number back using the locale's own separators. */
function readBack(s: string, locale: string): number {
  const parts = new Intl.NumberFormat(locale).formatToParts(-12345.6);
  const group = parts.find((p) => p.type === "group")!.value;
  const dec = parts.find((p) => p.type === "decimal")!.value;
  const minus = parts.find((p) => p.type === "minusSign")!.value;
  return Number(s.split(group).join("").replace(dec, ".").replace(minus, "-"));
}

describe("formatters", () => {
  it("show every finite number in the language's own format, rounded, never NaN or undefined", () => {
    fc.assert(
      fc.property(fc.double({ min: -1e9, max: 1e9, noNaN: true }), fc.constantFrom(...LANGS), fc.integer({ min: 0, max: 2 }), (v, lang, digits) => {
        const locale = localeFor(lang);
        const s = formatNumber(v, locale, digits);
        expect(s).not.toMatch(/NaN|undefined|Infinity|null/);
        const round = Math.round(v * 10 ** digits) / 10 ** digits;
        expect(readBack(s, locale)).toBeCloseTo(Object.is(round, -0) ? 0 : round, digits);
      }),
    );
  });

  it("show a dash, never 0 or NaN, for missing values", () => {
    for (const v of [null, undefined, NaN, Infinity, -Infinity])
      for (const lang of LANGS) {
        expect(formatNumber(v, localeFor(lang))).toBe(DASH);
        expect(formatMoney(v, "EUR", localeFor(lang))).toBe(DASH);
      }
  });

  it("money: whole amounts with the right currency symbol in every language", () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 5_000_000 }), fc.constantFrom(...LANGS), fc.constantFrom("EUR" as const, "GBP" as const), (v, lang, cur) => {
        const s = formatMoney(v, cur, localeFor(lang));
        // The symbol, or the ISO code where that is the language's own style (es-ES writes "0 GBP").
        expect(s).toMatch(cur === "EUR" ? /€|EUR/ : /£|GBP/);
        expect(s).not.toMatch(/NaN|undefined/);
        const digits = s.replace(/[^\d]/g, "");
        expect(Number(digits)).toBe(v);
      }),
    );
  });

  it("every unit on spec pages is metric", () => {
    const METRIC = new Set(["km", "kWh", "kW", "V", "kg", "km/h", "l", "min", "mm", "s", "kWh/100 km", "Wh/km", "°C", "€"]);
    for (const f of SPEC_FIELDS) if ("unit" in f && f.unit) expect(METRIC, `${f.key}: ${f.unit}`).toContain(f.unit);
  });

  it("no dictionary in any language shows imperial units", () => {
    const dicts: Record<string, Record<string, string>> = { en, nl, de, fr, es, it: it_ };
    const IMPERIAL = /\b(mph|miles?|mi\/kWh|lbs?|pounds? of|gallons?|inch(es)?|feet|°F)\b/i;
    for (const [lang, d] of Object.entries(dicts))
      for (const [k, v] of Object.entries(d)) expect(IMPERIAL.test(v), `${lang} ${k}: ${v}`).toBe(false);
  });
});

// Keep the default state honest: it must encode to an empty query (clean shareable URL).
it("the default state is the empty URL", () => {
  expect(toSearchParams(defaultState()).toString()).toBe("");
});
