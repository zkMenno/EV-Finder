// "Find a charger / plan a trip" link-out block (T-026; spec tab "Charging buildout", Link rules).
// Pure links from config/countries/<country>.yaml `charging_links`, validated at build time by
// scripts/charging-links.mjs into src/config/charging-links.generated.json. No API calls, no
// logos, no affiliate tags: plain URLs plus our UTM tag, new tab, rel="noopener" (+ nofollow for
// third-party sites). Server only.
import { readFileSync } from "node:fs";
import type { CountrySlug, Lang } from "@/config/countries";
import generated from "@/config/charging-links.generated.json";

export interface ChargingLinkConfig {
  /** What the tool is for, official-map | local-app | map | route-planner | price-compare (schema CountryChargingLink.job). */
  job: string;
  /**
   * Link text per language (text only, no logos): schema LocalizedText, EN required. Older
   * generated files and test fixtures may still hold a plain string; both are accepted.
   */
  label: Partial<Record<Lang, string>> & { en: string } | string;
  url: string;
  order: number;
  tool: string | null;
  /** Government / official source: no nofollow. */
  official: boolean;
  /** false: link without our UTM tag (config can opt out per link). */
  utm: boolean;
  /** true only after someone opened the link by hand (absent = false). */
  verified?: boolean;
}

/** The label in `lang`, falling back to EN (LocalizedText), or the plain string form. */
export function linkLabel(label: ChargingLinkConfig["label"], lang: Lang = "en"): string {
  if (typeof label === "string") return label;
  return label[lang] ?? label.en;
}

export interface ChargingLink {
  id: string;
  job: string;
  label: string;
  url: string;
  rel: string;
  target: "_blank";
}

export const UTM = { utm_source: "evfinder", utm_medium: "referral", utm_campaign: "charging_links" } as const;
export const MAX_CHARGING_LINKS = 5;
/** Plain ABRP link for model pages (car pre-selection waits for abrp_typecode, T-029). */
export const ABRP_URL = "https://abetterrouteplanner.com/";
const ABRP_HOST = "abetterrouteplanner.com";

type Config = Record<CountrySlug, readonly ChargingLinkConfig[]>;

let override: { file: string; config: Config } | null = null;

/**
 * The validated config. `CHARGING_LINKS_FILE` (a JSON file in the generated shape) replaces it at
 * runtime; the e2e test uses it with a fixture until T-024 fills the country YAML.
 */
export function chargingConfig(env: Record<string, string | undefined> = process.env): Config {
  const file = env.CHARGING_LINKS_FILE;
  if (file) {
    if (override?.file !== file) override = { file, config: JSON.parse(readFileSync(file, "utf8")) as Config };
    return override.config;
  }
  // Validated by the script (a test keeps it in step with the YAML); widen via unknown.
  return generated as unknown as Config;
}

/** Adds our UTM tag unless the URL already carries one. */
export function withUtm(url: string): string {
  const u = new URL(url);
  if ([...u.searchParams.keys()].some((k) => k.startsWith("utm_"))) return u.href;
  for (const [k, v] of Object.entries(UTM)) u.searchParams.set(k, v);
  return u.href;
}

export function linkRel(official: boolean): string {
  return official ? "noopener" : "nofollow noopener";
}

function isAbrp(url: string): boolean {
  try {
    const h = new URL(url).hostname;
    return h === ABRP_HOST || h.endsWith(`.${ABRP_HOST}`);
  } catch {
    return false;
  }
}

/** The block's links for one country, in config order, at most five. */
export function chargingLinks(country: CountrySlug, opts: { withoutAbrp?: boolean; config?: Config; lang?: Lang } = {}): ChargingLink[] {
  const list = (opts.config ?? chargingConfig())[country] ?? [];
  return [...list]
    .sort((a, b) => a.order - b.order)
    .filter((l) => !(opts.withoutAbrp && isAbrp(l.url)))
    .slice(0, MAX_CHARGING_LINKS)
    .map((l, i) => ({
      id: l.tool ?? `${l.job}-${i}`,
      job: l.job,
      label: linkLabel(l.label, opts.lang),
      url: l.utm ? withUtm(l.url) : l.url,
      rel: linkRel(l.official),
      target: "_blank" as const,
    }));
}

/** Model-page footer: a plain ABRP link, no car pre-selected. */
export function abrpLink(): ChargingLink {
  return { id: "abrp", job: "route-planner", label: "A Better Routeplanner (ABRP)", url: withUtm(ABRP_URL), rel: linkRel(false), target: "_blank" };
}
