// Plain-string labels for <Num>, so server components can pass them across the client boundary.
import type { Confidence } from "@ev/schema";
import type { T } from "@/i18n";

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
  conf: Record<Confidence, string>;
}

export function numLabels(t: T): NumLabels {
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
    conf: { high: t("conf.high"), medium: t("conf.medium"), low: t("conf.low") },
  };
}
