// Plain-string labels for <Num>, so server components can pass them across the client boundary.
import type { Confidence } from "@ev/schema";
import type { T } from "@/i18n/t";

/**
 * Glossary ids behind the words in a <Num> popover (glossary sweep item 7). Each word links to
 * its /learn page when the glossary has the term; a missing term just stays plain text.
 */
export const NUM_TERMS = {
  agree: "sources-agree",
  oneSource: "quality-tier",
  estimate: "estimate",
  claim: "claim",
  derived: "derived",
  confidence: "confidence",
  release: "data-release",
  rung: "real-range-rung",
  notDisclosed: "not-disclosed",
} as const;
export type NumTermKey = keyof typeof NUM_TERMS;

export interface NumLabels {
  source: string;
  confidence: string;
  derived: string;
  details: string;
  noSource: string;
  /** Screen-reader text for a missing value ("—"). */
  noData: string;
  /** Screen-reader text for a DC-behaviour value hidden because the car has no DC data. */
  noDc: string;
  /** "{n} sources agree" */
  agree: string;
  oneSource: string;
  estimate: string;
  claim: string;
  claimHelp: string;
  /** "Data release" (popover line with the release date). */
  release: string;
  conf: Record<Confidence, string>;
  /** Glossary hrefs ("/{country}/{lang}/learn/<id>") for the popover words; only terms that exist. */
  glossary?: Partial<Record<NumTermKey, string>>;
}

export interface NumGlossary {
  /** "/{country}/{lang}" */
  base: string;
  /** Glossary term ids that exist (e.g. `Object.keys(tax.terms)` or the terms record). */
  terms: Record<string, unknown> | readonly string[];
}

/** Hrefs for the NUM_TERMS that exist in the glossary. Exported for tests. */
export function numGlossary({ base, terms }: NumGlossary): Partial<Record<NumTermKey, string>> {
  const has = Array.isArray(terms) ? new Set(terms) : new Set(Object.keys(terms));
  const out: Partial<Record<NumTermKey, string>> = {};
  for (const [k, id] of Object.entries(NUM_TERMS) as [NumTermKey, string][]) {
    if (has.has(id)) out[k] = `${base}/learn/${id}`;
  }
  return out;
}

export function numLabels(t: T, glossary?: NumGlossary): NumLabels {
  return {
    source: t("num.source"),
    confidence: t("num.confidence"),
    derived: t("num.derived"),
    details: t("num.details"),
    noSource: t("num.noSource"),
    noData: t("num.noData"),
    noDc: t("num.noDc"),
    agree: t("num.agree"),
    oneSource: t("num.oneSource"),
    estimate: t("num.estimate"),
    claim: t("num.claim"),
    claimHelp: t("num.claimHelp"),
    release: t("num.release"),
    conf: { high: t("conf.high"), medium: t("conf.medium"), low: t("conf.low") },
    ...(glossary ? { glossary: numGlossary(glossary) } : {}),
  };
}
