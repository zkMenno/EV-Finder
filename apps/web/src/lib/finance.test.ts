import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { loadFinance, OUT_FILE, serialize, validateFinance } from "../../scripts/finance.mjs";
import {
  DEFAULT_DEPOSIT_PCT,
  DEFAULT_TERM_MONTHS,
  effectiveLoan,
  financeLinksAllowed,
  loanPayment,
  monthlyFor,
  monthlyRate,
  parseLoanSettings,
  readLoanSettings,
  writeLoanSettings,
  type FinanceProfileView,
} from "./finance";
import { financeProfile } from "./finance-profiles";
import { memoryStorage } from "./storage";

const de: FinanceProfileView = {
  id: "de-used-car-loan",
  country: "DE",
  product: "used-car-loan",
  typical_apr: 8.91,
  default_term_months: null,
  default_deposit_pct: null,
  source: { name: "ECB MIR", url: "https://data.ecb.europa.eu/x", series_id: "MIR.M.DE", period: "2026-09" },
  retrieved_at: "2026-11-15",
  review: true,
};
const nl: FinanceProfileView = { ...de, id: "nl-used-car-loan", country: "NL", typical_apr: null, source: null, retrieved_at: null };

describe("loan maths (annuity, Decision 017)", () => {
  it("monthly rate from APR: (1 + APR)^(1/12) − 1", () => {
    expect(monthlyRate(12.682503)).toBeCloseTo(0.01, 6);
    expect(monthlyRate(0)).toBe(0);
  });
  it("annuity payment, totals and cost of credit", () => {
    // 20,000 over 48 months at 1 % a month: 526.68 (standard annuity table).
    const r = loanPayment({ price: 20000, depositPct: 0, termMonths: 48, aprPct: 12.682503 })!;
    expect(r.monthly).toBeCloseTo(526.68, 1);
    expect(r.totalRepaid).toBeCloseTo(526.68 * 48, -1);
    expect(r.costOfCredit).toBeCloseTo(r.totalRepaid - 20000, 6);
    // Deposit lowers the principal and is part of the total over the term.
    const d = loanPayment({ price: 20000, depositPct: 25, termMonths: 48, aprPct: 12.682503 })!;
    expect(d.principal).toBe(15000);
    expect(d.totalOverTerm).toBeCloseTo(5000 + d.monthly * 48, 6);
    // 0 % = straight division.
    expect(loanPayment({ price: 12000, depositPct: 0, termMonths: 24, aprPct: 0 })!.monthly).toBe(500);
  });
  it("rejects impossible inputs", () => {
    expect(loanPayment({ price: -1, depositPct: 0, termMonths: 48, aprPct: 5 })).toBeNull();
    expect(loanPayment({ price: 1, depositPct: 101, termMonths: 48, aprPct: 5 })).toBeNull();
    expect(loanPayment({ price: 1, depositPct: 0, termMonths: 0, aprPct: 5 })).toBeNull();
    expect(loanPayment({ price: 1, depositPct: 0, termMonths: 12.5, aprPct: 5 })).toBeNull();
  });
});

describe("inputs: user → sourced profile → labelled default; no made-up APR", () => {
  const none = { aprPct: null, termMonths: null, depositPct: null };
  it("uses the sourced APR and the labelled term/deposit assumptions", () => {
    const e = effectiveLoan(de, none);
    expect(e).toMatchObject({ aprPct: 8.91, termMonths: DEFAULT_TERM_MONTHS, depositPct: DEFAULT_DEPOSIT_PCT });
    expect(e.origin).toEqual({ apr: "profile", term: "assumption", deposit: "assumption" });
  });
  it("NL (typical_apr null): no rate until the user enters one", () => {
    const e = effectiveLoan(nl, none);
    expect(e.aprPct).toBeNull();
    expect(e.origin.apr).toBe("missing");
    expect(monthlyFor(25000, e)).toBeNull();
    const mine = effectiveLoan(nl, { ...none, aprPct: 7 });
    expect(mine.origin.apr).toBe("user");
    expect(monthlyFor(25000, mine)!.monthly).toBeGreaterThan(0);
  });
  it("no price → no monthly figure", () => {
    expect(monthlyFor(null, effectiveLoan(de, none))).toBeNull();
  });
  it("settings survive storage, and garbage is ignored", () => {
    const st = memoryStorage();
    writeLoanSettings({ aprPct: 6.5, termMonths: 60, depositPct: 10 }, st);
    expect(readLoanSettings(st)).toEqual({ aprPct: 6.5, termMonths: 60, depositPct: 10 });
    expect(parseLoanSettings("{bad")).toEqual(none);
    expect(parseLoanSettings(JSON.stringify({ aprPct: -3, termMonths: 500, depositPct: "x" }))).toEqual(none);
  });
  it("no finance or lease links for the UK", () => {
    expect(financeLinksAllowed("UK")).toBe(false);
    expect(financeLinksAllowed("NL")).toBe(true);
  });
});

describe("finance_profiles.yaml (scripts/finance.mjs)", () => {
  it("the committed JSON matches data/taxonomy/finance_profiles.yaml", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(serialize(loadFinance()));
  });
  it("a rate always has a source and a date; NL has no rate", () => {
    for (const c of ["NL", "DE", "FR", "BE", "UK"] as const) {
      const p = financeProfile(c);
      if (p?.typical_apr != null) {
        expect(p.source?.url).toMatch(/^https:\/\//);
        expect(p.retrieved_at).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      }
    }
    expect(financeProfile("NL")?.typical_apr ?? null).toBeNull();
  });
  it("rejects an APR without a source", () => {
    const row = { id: "x", country: "DE", product: "used-car-loan", typical_apr: 5, default_term_months: null, default_deposit_pct: null, source: null, retrieved_at: null, review: true };
    expect(() => validateFinance({ finance_profiles: [row] })).toThrow(/source/);
    expect(() => validateFinance({ finance_profiles: [{ ...row, typical_apr: 500 }] })).toThrow(/percentage/);
  });
});
