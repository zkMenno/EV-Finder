// Price modes and the loan calculator (Decision 017, T-043). Pure and client-safe: profiles come
// from src/lib/finance-profiles.ts (server) as props. Every amount here is an estimate from its
// inputs (price, deposit, term, APR), never an offer.
import type { Country } from "@ev/schema";
import { readStorage, writeStorage, type KeyValueStorage } from "@/lib/storage";

/** buy = outright price; loan = monthly instalment estimate; lease = link placeholder, no figures. */
export type PayMode = "buy" | "loan" | "lease";
export const PAY_MODES: readonly PayMode[] = ["buy", "loan", "lease"];

export function isPayMode(v: unknown): v is PayMode {
  return typeof v === "string" && (PAY_MODES as readonly string[]).includes(v);
}

/** One row of data/taxonomy/finance_profiles.yaml as the web app uses it (schema FinanceProfile). */
export interface FinanceProfileView {
  id: string;
  country: Country;
  product: string;
  /** Percent (8.91 = 8.91 %); null = no citable source, the calculator asks for a rate. */
  typical_apr: number | null;
  default_term_months: number | null;
  default_deposit_pct: number | null;
  source: { name: string; url: string; series_id: string | null; period: string | null } | null;
  retrieved_at: string | null;
  /** Entered by an agent, not yet checked by a person. */
  review: boolean;
}

/** Glossary ids the price-mode UI shows an ⓘ for (data/taxonomy/glossary_terms.yaml); missing ones render none. */
export const FINANCE_TERMS = [
  "loan",
  "lease",
  "private-lease",
  "balloon-pcp",
  "residual-value",
  "total-cost-over-term",
] as const;

/** The subset of localized glossary terms the price-mode UI needs (keeps the page payload small). */
export function financeTerms<T>(terms: Record<string, T>): Record<string, T> {
  return Object.fromEntries(FINANCE_TERMS.flatMap((id) => (terms[id] ? [[id, terms[id]]] : [])));
}

/** Spec §8 default when no source states a term: labelled "assumption, change it". */
export const DEFAULT_TERM_MONTHS = 48;
/** Default deposit when no source states one: labelled "assumption, change it". */
export const DEFAULT_DEPOSIT_PCT = 0;
export const TERM_CHOICES: readonly number[] = [12, 24, 36, 48, 60, 72, 84];

/** Monthly rate from an APR in percent: r = (1 + APR)^(1/12) − 1 (glossary `loan` nerd note). */
export function monthlyRate(aprPct: number): number {
  return Math.pow(1 + aprPct / 100, 1 / 12) - 1;
}

export interface LoanInputs {
  price: number;
  depositPct: number;
  termMonths: number;
  aprPct: number;
}

export interface LoanResult {
  deposit: number;
  principal: number;
  monthlyRate: number;
  monthly: number;
  /** Sum of all instalments (excludes the deposit). */
  totalRepaid: number;
  /** Deposit + all instalments: what the car costs you over the term. */
  totalOverTerm: number;
  /** totalRepaid − principal. */
  costOfCredit: number;
}

/** Annuity: payment = P × r / (1 − (1 + r)^−n); with r = 0, P / n. Null for impossible inputs. */
export function loanPayment(i: LoanInputs): LoanResult | null {
  const ok = (n: number) => Number.isFinite(n) && n >= 0;
  if (!ok(i.price) || !ok(i.depositPct) || i.depositPct > 100 || !ok(i.aprPct) || i.aprPct > 100)
    return null;
  if (!Number.isInteger(i.termMonths) || i.termMonths < 1 || i.termMonths > 120) return null;
  const deposit = (i.price * i.depositPct) / 100;
  const principal = i.price - deposit;
  const r = monthlyRate(i.aprPct);
  const n = i.termMonths;
  const monthly = r === 0 ? principal / n : (principal * r) / (1 - Math.pow(1 + r, -n));
  const totalRepaid = monthly * n;
  return {
    deposit,
    principal,
    monthlyRate: r,
    monthly,
    totalRepaid,
    totalOverTerm: deposit + totalRepaid,
    costOfCredit: totalRepaid - principal,
  };
}

/** The user's own loan settings (browser only). null fields fall back to the profile / defaults. */
export interface LoanSettings {
  aprPct: number | null;
  termMonths: number | null;
  depositPct: number | null;
}

export const LOAN_KEY = "ev-finder:loan:v1";
export const PAY_KEY = "ev-finder:pay:v1";

function pct(v: unknown): number | null {
  return typeof v === "number" && Number.isFinite(v) && v >= 0 && v <= 100 ? v : null;
}

export function parseLoanSettings(raw: string | null): LoanSettings {
  const empty: LoanSettings = { aprPct: null, termMonths: null, depositPct: null };
  if (!raw) return empty;
  try {
    const o = JSON.parse(raw) as Record<string, unknown>;
    const term =
      typeof o.termMonths === "number" &&
      Number.isInteger(o.termMonths) &&
      o.termMonths >= 1 &&
      o.termMonths <= 120
        ? o.termMonths
        : null;
    return { aprPct: pct(o.aprPct), termMonths: term, depositPct: pct(o.depositPct) };
  } catch {
    return empty;
  }
}

export function readLoanSettings(storage?: KeyValueStorage | null): LoanSettings {
  return parseLoanSettings(
    storage === undefined ? readStorage(LOAN_KEY) : readStorage(LOAN_KEY, storage),
  );
}

export function writeLoanSettings(s: LoanSettings, storage?: KeyValueStorage | null): void {
  const v = JSON.stringify(s);
  if (storage === undefined) writeStorage(LOAN_KEY, v);
  else writeStorage(LOAN_KEY, v, storage);
}

/** Where each input comes from, so the UI can label it ("you", "source", "assumption"). */
export type InputOrigin = "user" | "profile" | "assumption" | "missing";

export interface EffectiveLoan {
  aprPct: number | null;
  termMonths: number;
  depositPct: number;
  origin: { apr: InputOrigin; term: InputOrigin; deposit: InputOrigin };
}

/** User value → sourced profile value → labelled default. APR never gets a made-up default. */
export function effectiveLoan(profile: FinanceProfileView | null, s: LoanSettings): EffectiveLoan {
  const apr = s.aprPct ?? profile?.typical_apr ?? null;
  const term = s.termMonths ?? profile?.default_term_months ?? DEFAULT_TERM_MONTHS;
  const deposit = s.depositPct ?? profile?.default_deposit_pct ?? DEFAULT_DEPOSIT_PCT;
  return {
    aprPct: apr,
    termMonths: term,
    depositPct: deposit,
    origin: {
      apr: s.aprPct !== null ? "user" : profile?.typical_apr != null ? "profile" : "missing",
      term:
        s.termMonths !== null
          ? "user"
          : profile?.default_term_months != null
            ? "profile"
            : "assumption",
      deposit:
        s.depositPct !== null
          ? "user"
          : profile?.default_deposit_pct != null
            ? "profile"
            : "assumption",
    },
  };
}

/** Monthly estimate for one price with the effective settings; null without a price or a rate. */
export function monthlyFor(price: number | null | undefined, e: EffectiveLoan): LoanResult | null {
  if (typeof price !== "number" || e.aprPct === null) return null;
  return loanPayment({
    price,
    depositPct: e.depositPct,
    termMonths: e.termMonths,
    aprPct: e.aprPct,
  });
}

/**
 * Finance and lease link-outs per country. UK: none until the FCA credit-broking question is
 * answered (Decision 017); the calculator itself is allowed everywhere.
 */
export function financeLinksAllowed(country: Country): boolean {
  return country !== "UK";
}

/** Remembered price mode (localStorage), used when the URL has no ?pay=. */
export function readPayMode(): PayMode | null {
  const v = readStorage(PAY_KEY);
  return isPayMode(v) ? v : null;
}
export function writePayMode(m: PayMode): void {
  writeStorage(PAY_KEY, m);
}
