// Display formatting. Values are metric internally and on screen (AGENTS.md data rule 6).
import type { Currency } from "@ev/schema";
import type { Lang } from "@/config/countries";

const LOCALE: Record<Lang, string> = {
  en: "en-GB",
  nl: "nl-NL",
  de: "de-DE",
  fr: "fr-FR",
  es: "es-ES",
  it: "it-IT",
};

export function localeFor(lang: Lang): string {
  return LOCALE[lang];
}

export const DASH = "—";

const cache = new Map<string, Intl.NumberFormat>();
function nf(locale: string, opts: Intl.NumberFormatOptions): Intl.NumberFormat {
  const key = locale + JSON.stringify(opts);
  let f = cache.get(key);
  if (!f) {
    f = new Intl.NumberFormat(locale, opts);
    cache.set(key, f);
  }
  return f;
}

export function formatNumber(value: number | null | undefined, locale: string, maxFractionDigits = 1): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return DASH;
  return nf(locale, { maximumFractionDigits: maxFractionDigits }).format(value);
}

export function formatMoney(amount: number | null | undefined, currency: Currency, locale: string): string {
  if (amount === null || amount === undefined || !Number.isFinite(amount)) return DASH;
  return nf(locale, { style: "currency", currency, maximumFractionDigits: 0 }).format(amount);
}

export function formatYears(start: number, end: number | null | undefined, nowLabel: string): string {
  if (end === start) return String(start);
  return `${start}–${end ?? nowLabel}`;
}
