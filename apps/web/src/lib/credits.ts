// Credits for the About page: one entry per source in the current release (its `sources` array),
// with the attribution each licence asks for. Order of preference for the main line:
//   1. a wording override (only RDW, pending Q-037),
//   2. the release's own `attribution`,
//   3. the registry's attribution (data/sources.yaml → src/config/sources.generated.json, build time),
//   4. the fallback wording below.
// Required wording from the registry or the fallback notices is always added when the main
// line does not already contain it, so a release can never drop a required credit.
// Server only (imports the generated registry); the page renders plain text and links.
import type { Source } from "@ev/schema";
import generated from "@/config/sources.generated.json";

export interface RegistryEntry {
  name: string;
  owner?: string;
  licence: string;
  status: string;
  url?: string;
  attribution?: string;
}

export type Registry = Record<string, RegistryEntry>;

export const registry: Registry = generated as Registry;

const OGL = "Contains public sector information licensed under the Open Government Licence v3.0.";

/**
 * Fallback wording, per source id: used only when the release and the registry don't already carry it.
 * `override` replaces the release's own line (RDW, Q-037: "do not state the data comes from RDW";
 * interim wording until Menno answers). `notice` is wording a licence requires.
 */
export const FALLBACK_WORDING: Record<string, { override?: string; notice?: string; fallback?: string }> = {
  "kilowatt-openev": { notice: "Open EV Data (https://github.com/KilowattApp/open-ev-data)" },
  openev: { fallback: "Contains data from Open EV Data (open-ev-data-dataset), CDLA-Permissive-2.0." },
  rdw: { override: "Dutch vehicle register (RDW open data, CC0)" },
  // APK defects (T-059 known issues): same RDW clause, same interim wording (Q-037).
  "rdw-defects": { override: "Dutch vehicle register (RDW open data, CC0)" },
  eea: { notice: "© European Union, EEA, CC BY 4.0" },
  kba: { notice: "© Kraftfahrt-Bundesamt, Flensburg" },
  "kba-fz10": { notice: "© Kraftfahrt-Bundesamt, Flensburg" },
  "dft-veh": { notice: OGL },
  "dft-veh0160": { notice: OGL },
  "dvsa-mot": { notice: OGL },
  ademe: { notice: "Source: ADEME (Car Labelling), Licence Ouverte / Open Licence 2.0 (Etalab)" },
  sdes: { notice: "Source: SDES, Licence Ouverte / Open Licence 2.0 (Etalab)" },
};

/** Licence id → readable name and official text. Per licence, not per source. */
const LICENCES: Record<string, { label: string; url?: string }> = {
  "CC-BY-4.0": { label: "CC BY 4.0", url: "https://creativecommons.org/licenses/by/4.0/" },
  "CC-BY-SA-4.0": { label: "CC BY-SA 4.0", url: "https://creativecommons.org/licenses/by-sa/4.0/" },
  "CC0-1.0": { label: "CC0 1.0", url: "https://creativecommons.org/publicdomain/zero/1.0/" },
  "CDLA-Permissive-2.0": { label: "CDLA-Permissive-2.0", url: "https://cdla.dev/permissive-2-0/" },
  "OGL-UK-3.0": { label: "Open Government Licence v3.0", url: "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" },
  "Licence-Ouverte-2.0": { label: "Licence Ouverte 2.0 (Etalab)", url: "https://www.etalab.gouv.fr/licence-ouverte-open-licence/" },
  "dl-de/by-2-0": { label: "Datenlizenz Deutschland – Namensnennung 2.0", url: "https://www.govdata.de/dl-de/by-2-0" },
  "MIT-with-attribution": { label: "MIT (attribution required)" },
  "US-Government-Public-Domain": { label: "US Government public domain" },
};

export interface Credit {
  id: string;
  name: string;
  licence: string;
  licenceLabel: string;
  licenceUrl?: string;
  url?: string;
  owner?: string;
  /** Attribution lines, in display order (at least one). */
  lines: string[];
}

const norm = (s: string) => s.toLowerCase().replace(/\s+/g, " ").trim();

export function creditFor(source: Source, reg: Registry = registry): Credit {
  const r = reg[source.id];
  const w = FALLBACK_WORDING[source.id] ?? {};
  const main = w.override || source.attribution?.trim() || r?.attribution || w.fallback;
  const lines: string[] = main ? [main] : [];
  for (const required of [r?.attribution, w.notice]) {
    if (required && !lines.some((l) => norm(l).includes(norm(required)))) lines.push(required);
  }
  const licence = source.licence || r?.licence || "";
  if (!lines.length) lines.push(`${source.name}, ${LICENCES[licence]?.label ?? licence}`);
  const lic = LICENCES[licence];
  return {
    id: source.id,
    name: source.name,
    licence,
    licenceLabel: lic?.label ?? licence,
    ...(lic?.url ? { licenceUrl: lic.url } : {}),
    ...(source.url ?? r?.url ? { url: source.url ?? r?.url } : {}),
    ...(r?.owner ? { owner: r.owner } : {}),
    lines,
  };
}

/** Credits for every source in the release, external sources first, then our own, by name. */
export function credits(sources: readonly Source[], reg: Registry = registry): Credit[] {
  const own = (c: Credit) => (reg[c.id]?.owner === "EV Finder" ? 1 : 0);
  return sources
    .map((s) => creditFor(s, reg))
    .sort((a, b) => own(a) - own(b) || a.name.localeCompare(b.name));
}

/** Splits text into plain parts and https URLs, so the page can link the URLs (still visible as text). */
export function linkParts(text: string): { text: string; href?: string }[] {
  const out: { text: string; href?: string }[] = [];
  let last = 0;
  for (const m of text.matchAll(/https:\/\/[^\s)]+/g)) {
    if (m.index > last) out.push({ text: text.slice(last, m.index) });
    out.push({ text: m[0], href: m[0] });
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push({ text: text.slice(last) });
  return out;
}
