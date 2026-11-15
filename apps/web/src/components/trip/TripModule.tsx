"use client";
// Trip fit quick check (T-036, Core 1). Explore loads this module with a dynamic import() only when
// TRIP_FIT=1 and the user opens the panel (or already saved a trip), so it never counts against
// the Explore first-load JS budget. Everything here runs in the browser (Decision 013); answers are
// stored in localStorage only (src/lib/trip-settings.ts), with a town id and never coordinates.
import type { FieldProvenance } from "@ev/schema";
import { useId, type ReactNode } from "react";
import { COUNTRIES, COUNTRY_SLUGS, type CountrySlug } from "@/config/countries";
import type { MsgKey, T } from "@/i18n/t";
import type { ExploreRow } from "@/lib/explore-data";
import type { Level } from "@/lib/state";
import { writeStorage } from "@/lib/storage";
import { TRIP_KEY } from "@/lib/state";
import { conditionsFor, fitAll, findTown, MATRIX, rangeNeeded, ROAD_BANDS, TOWNS, TRIP_RUNG, type CarFit } from "@/lib/trip-model";
import {
  CHARGING,
  DRIVING,
  EXTRAS,
  hasTrip,
  LONG_TRIPS,
  MAX_TRIP_KM,
  normalizeTripSettings,
  readTripSettings,
  ROLES,
  writeTripSettings,
  type TripSettings,
} from "@/lib/trip-settings";
import { Num } from "../Num";
import type { NumLabels } from "../num-labels";
import { TermInfo, type TermText } from "../Term";
import type { UiTerm } from "@/lib/taxonomy";

export type { CarFit, TripSettings };

/** Source id used in <Num> provenance for every trip estimate. */
export const TRIP_SOURCE_ID = "trip-fixture-matrix";

export function tripProvenance(t: T): FieldProvenance {
  return { source_ids: [TRIP_SOURCE_ID], confidence: "low", derived: true, estimate: true, note: t("trip.rung.note") };
}

export function tripSources(t: T): Record<string, string> {
  return { [TRIP_SOURCE_ID]: t("trip.rung.fixture") };
}

export const loadTripSettings = (): TripSettings | null => readTripSettings();
export const saveTripSettings = (s: TripSettings): boolean => writeTripSettings(s);
/** Forget the trip (empty value = nothing stored; the storage interface has no remove). */
export const clearTripSettings = (): boolean => writeStorage(TRIP_KEY, "");
export { hasTrip, normalizeTripSettings };

/** Verdicts for every row, or null when no trip is entered. */
export function computeFits(rows: readonly ExploreRow[], s: TripSettings | null, country: CountrySlug): Map<string, CarFit> | null {
  if (!hasTrip(s)) return null;
  const c = conditionsFor(s, country);
  return c ? fitAll(rows, c) : null;
}

export interface TripUi {
  t: T;
  level: Level;
  locale: string;
  labels: NumLabels;
  country: CountrySlug;
  /** Glossary ⓘ for the trip terms (glossary sweep item 10); none = plain labels. */
  gloss?: { base: string; terms: Record<string, UiTerm>; text: TermText };
}

/** The glossary ⓘ for one trip term, or nothing when the glossary (or `ui.gloss`) lacks it. */
function TripTerm({ ui, id }: { ui: TripUi; id: string }) {
  if (!ui.gloss) return null;
  return <TermInfo term={ui.gloss.terms[id]} base={ui.gloss.base} text={ui.gloss.text} />;
}

function TripNum({ value, ui, unit = "km", focusable = true }: { value: number | null; ui: TripUi; unit?: string; focusable?: boolean }) {
  return (
    <Num
      value={value === null ? null : Math.round(value)}
      unit={unit}
      digits={0}
      provenance={tripProvenance(ui.t)}
      sources={tripSources(ui.t)}
      locale={ui.locale}
      labels={ui.labels}
      level={ui.level === "nerd" ? "detailed" : ui.level}
      focusable={focusable}
    />
  );
}

const SYMBOL: Record<CarFit["verdict"], string> = { ok: "✓", tight: "⚠", fail: "✗", unknown: "?" };

/** The Explore "Your trips" cell: symbol + text (never colour alone), reason when a car fails. */
export function TripCell({ fit, ui, inTable = true }: { fit: CarFit | undefined; ui: TripUi; inTable?: boolean }) {
  const { t, level } = ui;
  if (!fit) return null;
  const tone = fit.verdict === "ok" ? "text-green-900" : fit.verdict === "tight" ? "text-amber-900" : fit.verdict === "fail" ? "text-red-900" : "text-slate-700";
  return (
    <span className="flex min-w-36 flex-col text-left" data-testid="trip-cell" data-verdict={fit.verdict}>
      <span className={`whitespace-nowrap font-semibold ${tone}`}>
        <span aria-hidden="true">{SYMBOL[fit.verdict]} </span>
        {t(`trip.verdict.${fit.verdict}` as MsgKey)}
      </span>
      {fit.verdict === "unknown" ? <span className="text-xs text-slate-700">{t("trip.reason.unknown")}</span> : null}
      {fit.verdict === "fail" && fit.shortKm !== null ? (
        <span className="text-xs text-slate-800" data-testid="trip-reason">
          {t("trip.reason.short", { km: Math.max(1, Math.round(fit.shortKm)) })}
        </span>
      ) : null}
      {level !== "simple" && fit.winterKm !== null ? (
        <span className="flex flex-wrap items-baseline gap-1 text-xs text-slate-800">
          {t("trip.cell.winter")} <TripNum value={fit.winterKm} ui={ui} focusable={!inTable} />
        </span>
      ) : null}
      {level === "nerd" && fit.margin !== null ? (
        <span className="text-[0.7rem] leading-4 text-slate-700">
          {t("trip.cell.margin", { pct: Math.round(fit.margin * 100) })} · {t("trip.cell.health", { pct: Math.round(fit.health * 100) })} ·{" "}
          {t("trip.cell.start", { pct: Math.round(fit.startCharge * 100) })} · {TRIP_RUNG}
        </span>
      ) : null}
    </span>
  );
}

/* ---------- panel: profile picker, inputs, result card ---------- */

function ChoiceGroup<V extends string>({
  legend,
  name,
  options,
  value,
  onChange,
  multi = false,
}: {
  legend: string;
  name: string;
  options: readonly { value: V; label: string }[];
  value: V[];
  onChange: (next: V[]) => void;
  multi?: boolean;
}) {
  return (
    <fieldset className="min-w-0">
      <legend className="mb-1 text-sm font-medium">{legend}</legend>
      <div className="flex flex-wrap gap-1.5">
        {options.map((o) => {
          const checked = value.includes(o.value);
          return (
            <label key={o.value} className="cursor-pointer">
              <input
                type={multi ? "checkbox" : "radio"}
                name={name}
                className="peer sr-only"
                checked={checked}
                onChange={(e) => onChange(multi ? (e.target.checked ? [...value, o.value] : value.filter((x) => x !== o.value)) : [o.value])}
              />
              <span className="inline-flex min-h-9 items-center gap-1 rounded-full border border-slate-500 bg-white px-3 text-sm text-slate-900 peer-checked:border-blue-800 peer-checked:bg-blue-800 peer-checked:text-white peer-focus-visible:outline peer-focus-visible:outline-3 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-blue-700">
                {checked ? <span aria-hidden="true">✓</span> : null}
                {o.label}
              </span>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}

export interface TripPanelProps {
  settings: TripSettings;
  onChange: (s: TripSettings) => void;
  onClose: () => void;
  onClear: () => void;
  fits: Map<string, CarFit> | null;
  ui: TripUi;
}

export function TripPanel({ settings: s, onChange, onClose, onClear, fits, ui }: TripPanelProps) {
  const { t, country } = ui;
  const ids = useId();
  const set = (patch: Partial<TripSettings>) => onChange(normalizeTripSettings({ ...s, ...patch }));
  const opts = <V extends string>(list: readonly V[], prefix: string) => list.map((v) => ({ value: v, label: t(`${prefix}.${v}` as MsgKey) }));
  const one = <V extends string>(v: V | null): V[] => (v ? [v] : []);
  const driving = s.driving ?? "mixed";
  const mwShown = s.motorwayPct ?? MATRIX.default_motorway_pct[driving];
  const town = findTown(s.townId, country);
  const others = COUNTRY_SLUGS.filter((c) => c !== country);

  return (
    <section aria-labelledby={`${ids}-h`} className="mb-4 rounded-lg border border-blue-800 bg-blue-50/40 p-4" data-testid="trip-panel">
      <div className="mb-3 flex items-start justify-between gap-2">
        <div>
          <h2 id={`${ids}-h`} className="text-lg font-semibold">
            {t("trip.title")}
          </h2>
          <p className="text-sm text-slate-800">{t("trip.intro")}</p>
        </div>
        <button type="button" onClick={onClose} className="min-h-9 rounded-md border border-slate-500 px-3 text-sm hover:bg-white">
          {t("trip.close")}
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="flex flex-col gap-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-700">{t("trip.step.profile")}</h3>
          <ChoiceGroup legend={t("trip.q.role")} name={`${ids}-role`} options={opts(ROLES, "trip.role")} value={one(s.role)} onChange={(v) => set({ role: v[0] ?? null })} />
          <ChoiceGroup legend={t("trip.q.long")} name={`${ids}-long`} options={opts(LONG_TRIPS, "trip.long")} value={one(s.longTrips)} onChange={(v) => set({ longTrips: v[0] ?? null })} />
          <ChoiceGroup legend={t("trip.q.charging")} name={`${ids}-chg`} options={opts(CHARGING, "trip.charging")} value={one(s.charging)} onChange={(v) => set({ charging: v[0] ?? null })} />
          <ChoiceGroup legend={t("trip.q.driving")} name={`${ids}-drv`} options={opts(DRIVING, "trip.driving")} value={one(s.driving)} onChange={(v) => set({ driving: v[0] ?? null })} />
          <ChoiceGroup legend={t("trip.q.extras")} name={`${ids}-ext`} options={opts(EXTRAS, "trip.extra")} value={s.extras} onChange={(v) => set({ extras: v })} multi />
        </div>

        <div className="flex flex-col gap-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-700">{t("trip.step.trip")}</h3>
          <div className="flex flex-col gap-1">
            <label htmlFor="trip-km" className="text-sm font-medium">
              {t("trip.km")}
            </label>
            <input
              id="trip-km"
              type="number"
              inputMode="numeric"
              min={1}
              max={MAX_TRIP_KM}
              step={10}
              value={s.roundTripKm ?? ""}
              aria-describedby="trip-km-help"
              onChange={(e) => set({ roundTripKm: e.target.value === "" ? null : Number(e.target.value) })}
              className="w-40 rounded-md border border-slate-400 bg-white px-2 py-1.5 text-sm tabular-nums"
            />
            <span id="trip-km-help" className="text-xs text-slate-700">
              {t("trip.km.help")}
            </span>
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="trip-mw" className="text-sm font-medium">
              {t("trip.motorway")}: <output htmlFor="trip-mw" className="tabular-nums">{mwShown}%</output>
              {s.motorwayPct === null ? <span className="ml-1 text-xs font-normal text-slate-700">({t("trip.motorway.default")})</span> : null}
            </label>
            <input id="trip-mw" type="range" min={0} max={100} step={5} value={mwShown} onChange={(e) => set({ motorwayPct: Number(e.target.value) })} className="max-w-72 accent-blue-800" />
          </div>
          <div className="flex flex-col gap-1">
            <span className="flex items-center gap-1">
              <label htmlFor="trip-town" className="text-sm font-medium">
                {t("trip.town")}
              </label>
              <TripTerm ui={ui} id="climate-normal" />
            </span>
            <select id="trip-town" value={town.id} onChange={(e) => set({ townId: e.target.value })} className="w-fit rounded-md border border-slate-400 bg-white px-2 py-1.5 text-sm">
              {[country, ...others].map((c) => (
                <optgroup key={c} label={COUNTRIES[c].name}>
                  {TOWNS.filter((x) => x.country === c).map((x) => (
                    <option key={x.id} value={x.id}>
                      {x.name}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
            <span className="text-xs text-slate-700">{t("trip.town.help")}</span>
          </div>
          <p className="text-xs text-slate-700">{t("trip.privacy")}</p>
          <div>
            <button type="button" onClick={onClear} className="text-sm text-blue-800 underline underline-offset-2">
              {t("trip.clear")}
            </button>
          </div>
        </div>
      </div>

      {hasTrip(s) ? <ResultCard settings={s} fits={fits} ui={ui} /> : <p className="mt-4 text-sm text-slate-800">{t("trip.enterKm")}</p>}
    </section>
  );
}

function ResultCard({ settings, fits, ui }: { settings: TripSettings; fits: Map<string, CarFit> | null; ui: TripUi }) {
  const { t, level, locale, country } = ui;
  const c = conditionsFor(settings, country);
  if (!c) return null;
  const need = rangeNeeded(c);
  const counts = { ok: 0, tight: 0, fail: 0, unknown: 0 };
  for (const f of fits?.values() ?? []) counts[f.verdict]++;
  const pct = (x: number) => Math.round(x * 100);
  const temp = (x: number) => new Intl.NumberFormat(locale, { maximumFractionDigits: 1 }).format(x);
  const row = (label: string, value: ReactNode, testId?: string) => (
    <div className="flex flex-col" data-testid={testId}>
      <dt className="text-xs text-slate-700">{label}</dt>
      <dd className="font-semibold">{value}</dd>
    </div>
  );
  const json = {
    rung: TRIP_RUNG,
    matrix: MATRIX.status,
    trip_km: c.km,
    road_shares: c.shares,
    town: c.town.id,
    winter_c: c.winterC,
    summer_c: c.summerC,
    temperature_bands: { winter: c.winterBand, summer: c.summerBand },
    need_km: { winter: Math.round(need.winterKm), summer: Math.round(need.summerKm), winter_p10: Math.round(need.winterLow), winter_p90: Math.round(need.winterHigh) },
    wltp_equivalent_km: { winter: Math.round(need.winterWltpKm), summer: Math.round(need.summerWltpKm) },
    wh_per_km_reference: need.whPerKm,
  };

  return (
    <div className="mt-4 rounded-md border border-slate-300 bg-white p-4" data-testid="trip-result" aria-live="polite">
      <h3 className="flex items-center gap-1 font-semibold">
        {t("trip.result.title")}
        <TripTerm ui={ui} id="range-you-need" />
      </h3>
      <p className="mt-1 flex flex-wrap items-baseline gap-1">
        {t("trip.result.need")} <TripNum value={need.winterKm} ui={ui} /> <span>{t("trip.result.winterMix")}</span>
        <span className="text-slate-700">
          (≈ <TripNum value={need.winterWltpKm} ui={ui} /> {t("trip.result.wltp")})
        </span>
        <TripTerm ui={ui} id="wltp-equivalent" />
      </p>
      <p className="mt-1 text-xs text-slate-700" data-testid="trip-estimate-label">
        {t("trip.result.estimate", { rung: t("trip.rung.fixture") })}
      </p>
      <p className="mt-2 text-sm" data-testid="trip-counts">
        {t("trip.result.counts", { ok: counts.ok, tight: counts.tight, fail: counts.fail })}
        {counts.unknown ? ` ${t("trip.result.unknown", { n: counts.unknown })}` : ""}
      </p>

      {level !== "simple" ? (
        <>
          <dl className="mt-3 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
            {row(t("trip.result.winter"), <TripNum value={need.winterKm} ui={ui} />, "trip-winter-km")}
            {row(t("trip.result.summer"), <TripNum value={need.summerKm} ui={ui} />, "trip-summer-km")}
            {row(t("trip.result.wltpWinter"), <TripNum value={need.winterWltpKm} ui={ui} />, "trip-wltp-km")}
            {row(t("trip.result.wltpSummer"), <TripNum value={need.summerWltpKm} ui={ui} />)}
          </dl>
          <p className="mt-3 flex items-center gap-1 text-sm">
            <span>{t("trip.result.temps", { town: c.town.name, winter: temp(c.winterC), summer: temp(c.summerC) })}</span>
            <TripTerm ui={ui} id="climate-normal" />
          </p>
          <div className="mt-2" aria-hidden="true">
            <div className="flex h-3 w-full overflow-hidden rounded border border-slate-400">
              {ROAD_BANDS.map((b, i) => (
                <span key={b} style={{ width: `${pct(c.shares[b])}%` }} className={["bg-slate-300", "bg-slate-500", "bg-slate-800"][i]} />
              ))}
            </div>
          </div>
          <p className="mt-1 flex items-center gap-1 text-xs text-slate-800">
            <span>{ROAD_BANDS.map((b) => `${t(`trip.band.${b}` as MsgKey)} ${pct(c.shares[b])}% (${Math.round(c.km * c.shares[b])} km)`).join(" · ")}</span>
            <TripTerm ui={ui} id="road-band" />
          </p>
          <p className="mt-2 flex flex-wrap items-center gap-1 text-xs text-slate-800">
            <span>{t("trip.result.assumes")}</span>
            <TripTerm ui={ui} id="start-charge" />
            <TripTerm ui={ui} id="trip-margin" />
            <TripTerm ui={ui} id="soh" />
          </p>
          {c.changes.length ? (
            <div className="mt-2 text-xs text-slate-800">
              <span className="font-semibold">{t("trip.result.changed")}</span>
              <ul className="list-disc pl-5">
                {c.changes.map((k) => (
                  <li key={k}>{t(k as MsgKey)}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </>
      ) : null}

      {level === "nerd" ? (
        <div className="mt-3 text-xs" data-testid="trip-nerd">
          <table className="border-collapse">
            <caption className="text-left font-semibold">{t("trip.nerd.whkm")}</caption>
            <thead>
              <tr>
                <th scope="col" className="pr-3 text-left">{t("trip.nerd.band")}</th>
                <th scope="col" className="pr-3 text-right">{t("trip.result.winter")}</th>
                <th scope="col" className="text-right">{t("trip.result.summer")}</th>
              </tr>
            </thead>
            <tbody>
              {ROAD_BANDS.map((b) => (
                <tr key={b}>
                  <th scope="row" className="pr-3 text-left font-normal">{t(`trip.band.${b}` as MsgKey)}</th>
                  <td className="pr-3 text-right tabular-nums"><TripNum value={need.whPerKm[b].winter} unit="Wh/km" ui={ui} /></td>
                  <td className="text-right tabular-nums"><TripNum value={need.whPerKm[b].summer} unit="Wh/km" ui={ui} /></td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-2 flex flex-wrap items-center gap-1">
            <span>{t("trip.nerd.band10", { low: Math.round(need.winterLow), high: Math.round(need.winterHigh) })}</span>
            <TripTerm ui={ui} id="uncertainty-band" />
            <span>
              · {t("trip.nerd.rung")}: {TRIP_RUNG} ({MATRIX.status})
            </span>
            <TripTerm ui={ui} id="real-range-rung" />
            <span>· {t("trip.nerd.factor", { winter: need.winterFactor.toFixed(2), summer: need.summerFactor.toFixed(2) })}</span>
          </p>
          <details className="mt-2">
            <summary className="cursor-pointer">{t("trip.nerd.json")}</summary>
            <pre className="mt-1 max-w-full overflow-auto rounded bg-slate-100 p-2">{JSON.stringify(json, null, 2)}</pre>
          </details>
        </div>
      ) : null}
    </div>
  );
}
