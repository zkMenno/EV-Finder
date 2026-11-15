"use client";
// Explore: one table of new and used EVs. The server renders the first rows; this component
// hydrates them, then fetches the compact catalogue JSON from our own origin and filters
// and sorts the full list in the browser. All state lives in the URL (see lib/state.ts).
// Taxonomy-driven filters (voltage, chemistry, cooling) read their options from data.
import type { Country, Currency, FieldProvenance } from "@ev/schema";
import Link from "next/link";
import { useEffect, useId, useMemo, useRef, useState, type ReactNode } from "react";
import { generationHref, variantHref } from "@/app/[country]/ev/_lib/routes";
import type { CountrySlug, Lang } from "@/config/countries";
import { makeT, type Dict, type MsgKey, type T } from "@/i18n";
import { compareStore, COMPARE_MAX } from "@/lib/compare-store";
import { hasDcData } from "@/lib/dc";
import type { ClientCatalogue, ExploreRow } from "@/lib/explore-data";
import { favouriteStore } from "@/lib/favourites";
import { applyFilters, displayName, priceFor, sortRows } from "@/lib/filters";
import { formatMoney, formatYears, localeFor } from "@/lib/format";
import {
  activeFilterCount,
  BODIES,
  defaultFilters,
  ERAS,
  EXPLORE_PARAM_KEYS,
  LEVEL_KEY,
  LEVELS,
  nextSort,
  SEGMENTS,
  toSearchParams,
  VIEW_KEY,
  type ExploreFilters,
  type ExploreState,
  type Level,
  type NumericFilter,
  type SortKey,
  type View,
} from "@/lib/state";
import { readStorage, writeStorage } from "@/lib/storage";
import { voltageBounds, type UiTaxonomy } from "@/lib/taxonomy";
import { useListStore } from "@/lib/use-list-store";
import { Missing, Num } from "./Num";
import { numLabels, type NumLabels } from "./num-labels";
import { PriceBand } from "./PriceBand";
import { QualityBadge } from "./QualityBadge";
import { InfoTip, TermInfo, TermLabel, type TermText } from "./Term";
import { usePopover } from "./use-popover";

const PAGE = 50;

export interface ExploreProps {
  country: CountrySlug;
  code: Country;
  currency: Currency;
  lang: Lang;
  dict: Dict;
  initialState: ExploreState;
  viewFromUrl: boolean;
  levelFromUrl: boolean;
  initialRows: ExploreRow[];
  initialMatches: number;
  total: number;
  dataUrl: string;
  sources: Record<string, string>;
  taxonomy: UiTaxonomy;
  /** Release date (YYYY-MM-DD), shown with sources at nerd level. */
  asOf: string;
}

interface Ctx {
  t: T;
  locale: string;
  labels: NumLabels;
  sources: Record<string, string>;
  code: Country;
  currency: Currency;
  country: CountrySlug;
  tax: UiTaxonomy;
  names: { voltage: Map<string, string>; chem: Map<string, string>; cool: Map<string, string> };
  termText: TermText;
  level: Level;
  asOf: string;
  /**
   * Inside the table, numbers and secondary links are not Tab stops (one stop per row for the
   * name link, heart and compare; provenance via the variant page or the Nerd "sources" button).
   */
  inTable?: boolean;
}

export function Explore(props: ExploreProps) {
  const t = useMemo(() => makeT(props.dict), [props.dict]);
  const locale = localeFor(props.lang);

  const [state, setState] = useState<ExploreState>(props.initialState);
  const [all, setAll] = useState<ExploreRow[] | null>(null);
  const [sources, setSources] = useState(props.sources);
  const [limit, setLimit] = useState(PAGE);
  // True once the user changed anything: from then on counts come from the (partial or full) client list.
  const [dirty, setDirty] = useState(false);
  const lastUrl = useRef(toSearchParams(props.initialState).toString());

  const ctx: Ctx = useMemo(
    () => ({
      t,
      locale,
      labels: numLabels(t),
      sources,
      code: props.code,
      currency: props.currency,
      country: props.country,
      tax: props.taxonomy,
      names: {
        voltage: new Map(props.taxonomy.voltageClasses.map((v) => [v.id, v.label])),
        chem: new Map(props.taxonomy.chemistries.map((v) => [v.id, v.label])),
        cool: new Map(props.taxonomy.coolings.map((v) => [v.id, v.label])),
      },
      termText: { about: t("term.about"), learnMore: t("term.learnMore") },
      level: state.level,
      asOf: props.asOf,
    }),
    [t, locale, sources, props.code, props.currency, props.country, props.taxonomy, state.level, props.asOf],
  );

  // Full list, fetched from our own origin after first paint.
  useEffect(() => {
    let live = true;
    fetch(props.dataUrl)
      .then((r) => (r.ok ? (r.json() as Promise<ClientCatalogue>) : null))
      .then((c) => {
        if (live && c) {
          setAll(c.rows);
          setSources(c.sources);
        }
      })
      .catch(() => {
        /* keep the server-rendered rows */
      });
    return () => {
      live = false;
    };
  }, [props.dataUrl]);

  // Remembered table/cards and level preferences, unless the URL says otherwise.
  useEffect(() => {
    const patch: Partial<ExploreState> = {};
    if (!props.viewFromUrl) {
      const stored = readStorage(VIEW_KEY);
      let view: View | null = stored === "cards" || stored === "table" ? stored : null;
      if (!view && window.matchMedia?.("(max-width: 639px)").matches) view = "cards";
      if (view && view !== props.initialState.view) patch.view = view;
    }
    if (!props.levelFromUrl) {
      const stored = readStorage(LEVEL_KEY);
      if ((LEVELS as readonly string[]).includes(stored ?? "") && stored !== props.initialState.level) patch.level = stored as Level;
    }
    // One-off read of browser-only preferences after hydration (reading them during render would
    // mismatch the server HTML), so a setState here is intended.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (Object.keys(patch).length) setState((s) => ({ ...s, ...patch }));
  }, [props.viewFromUrl, props.levelFromUrl, props.initialState.view, props.initialState.level]);

  // State → URL (replaceState: no server round trip, links stay shareable).
  useEffect(() => {
    const qs = toSearchParams(state).toString();
    if (qs === lastUrl.current) return;
    lastUrl.current = qs;
    const url = new URL(window.location.href);
    for (const k of EXPLORE_PARAM_KEYS) url.searchParams.delete(k);
    new URLSearchParams(qs).forEach((v, k) => url.searchParams.set(k, v));
    window.history.replaceState(null, "", url.pathname + url.search + url.hash);
  }, [state]);

  const update = (next: ExploreState) => {
    setDirty(true);
    setLimit(PAGE);
    setState(next);
  };
  const setFilter = (patch: Partial<ExploreFilters>) => update({ ...state, filters: { ...state.filters, ...patch } });
  const setView = (view: View) => {
    writeStorage(VIEW_KEY, view);
    setState({ ...state, view });
  };
  const setLevel = (level: Level) => {
    writeStorage(LEVEL_KEY, level);
    setState({ ...state, level });
  };

  const matches = useMemo(() => {
    if (!all && !dirty) return props.initialRows;
    const base = all ?? props.initialRows;
    return sortRows(applyFilters(base, state.filters, props.code), state.sort, state.dir, props.code);
  }, [all, dirty, state.filters, state.sort, state.dir, props.code, props.initialRows]);

  const matchCount = all || dirty ? matches.length : props.initialMatches;
  const rows = matches.slice(0, limit);

  return (
    <div className="grid gap-6 lg:grid-cols-[18rem_minmax(0,1fr)]">
      <FiltersPanel filters={state.filters} onChange={setFilter} onReset={() => update({ ...state, filters: defaultFilters() })} ctx={ctx} />
      <section aria-labelledby="results-heading" className="min-w-0">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h2 id="results-heading" className="sr-only">
            {t("explore.results")}
          </h2>
          <p aria-live="polite" className="text-sm text-slate-800" data-testid="result-count">
            {t("explore.count", { shown: matchCount, total: all?.length ?? props.total })}
            {!all ? <span className="ml-2 text-slate-600">{t("explore.loading")}</span> : null}
          </p>
          <div className="flex flex-wrap gap-2">
            <Toggle
              label={t("level")}
              options={LEVELS.map((l) => ({ value: l, label: t(`level.${l}`) }))}
              value={state.level}
              onChange={setLevel}
              testId="level-switch"
            />
            <Toggle
              label={t("explore.view")}
              options={(["table", "cards"] as const).map((v) => ({ value: v, label: t(`explore.view.${v}`) }))}
              value={state.view}
              onChange={setView}
            />
          </div>
        </div>

        {rows.length === 0 ? (
          <p className="rounded-md border border-dashed border-slate-400 p-6 text-center text-slate-800">{t("explore.noResults")}</p>
        ) : state.view === "table" ? (
          <ExploreTable rows={rows} state={state} onSort={(k) => update(nextSort(state, k))} ctx={ctx} />
        ) : (
          <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3" data-testid="explore-cards">
            {rows.map((r) => (
              <Card key={r.variant_id} row={r} ctx={ctx} />
            ))}
          </ul>
        )}

        {matches.length > rows.length ? (
          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={() => setLimit((l) => l + PAGE * 2)}
              className="rounded-md border border-slate-500 px-4 py-2 text-sm font-medium hover:bg-slate-100"
              data-testid="show-more"
            >
              {t("explore.showMore", { n: Math.min(PAGE * 2, matches.length - rows.length) })}
            </button>
          </div>
        ) : null}
      </section>
    </div>
  );
}

function Toggle<V extends string>({
  label,
  options,
  value,
  onChange,
  testId,
}: {
  label: string;
  options: { value: V; label: string }[];
  value: V;
  onChange: (v: V) => void;
  testId?: string;
}) {
  return (
    <div role="group" aria-label={label} className="inline-flex rounded-md border border-slate-400 p-0.5" data-testid={testId}>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          aria-pressed={value === o.value}
          onClick={() => onChange(o.value)}
          className={`rounded px-3 py-1 text-sm ${value === o.value ? "bg-slate-900 text-white" : "text-slate-900 hover:bg-slate-100"}`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

/* ---------- filters ---------- */

function FilterLabel({ htmlFor, termId, fallback, ctx }: { htmlFor?: string; termId: string; fallback: string; ctx: Ctx }) {
  const term = ctx.tax.terms[termId];
  const Tag = htmlFor ? "label" : "span";
  return (
    <span className="flex items-start justify-between gap-1">
      <Tag {...(htmlFor ? { htmlFor } : {})} className="text-sm font-medium">
        <TermLabel term={term ? { ...term, label: fallback } : undefined} fallback={fallback} showTechnical={ctx.level !== "simple"} />
      </Tag>
      <TermInfo term={term} country={ctx.country} text={ctx.termText} />
    </span>
  );
}

function NumberFilter({
  id,
  termId,
  label,
  value,
  onChange,
  step = 1,
  ctx,
}: {
  id: NumericFilter;
  termId: string;
  label: string;
  value: number | null;
  onChange: (v: number | null) => void;
  step?: number;
  ctx: Ctx;
}) {
  return (
    <div className="flex flex-col gap-1">
      <FilterLabel htmlFor={`f-${id}`} termId={termId} fallback={label} ctx={ctx} />
      <input
        id={`f-${id}`}
        name={id}
        type="number"
        inputMode="numeric"
        min={0}
        step={step}
        value={value ?? ""}
        onChange={(e) => {
          const raw = e.target.value;
          const n = raw === "" ? null : Number(raw);
          onChange(n !== null && Number.isFinite(n) && n >= 0 ? n : null);
        }}
        className="w-full rounded-md border border-slate-400 bg-white px-2 py-1.5 text-sm tabular-nums"
      />
    </div>
  );
}

function Chips<V extends string>({
  legend,
  termId,
  options,
  selected,
  onChange,
  ctx,
  info,
}: {
  legend: string;
  termId: string;
  options: readonly { value: V; label: string }[];
  selected: V[];
  onChange: (next: V[]) => void;
  ctx: Ctx;
  info?: (v: V) => ReactNode;
}) {
  const term = ctx.tax.terms[termId];
  return (
    <fieldset>
      <legend className="mb-1 flex w-full items-start justify-between gap-1 text-sm font-medium">
        <span>{legend}</span>
        <TermInfo term={term} country={ctx.country} text={ctx.termText} />
      </legend>
      <div className="flex flex-wrap gap-1.5">
        {options.map((o) => (
          <span key={o.value} className="inline-flex items-center">
            <label className="cursor-pointer">
              <input
                type="checkbox"
                className="peer sr-only"
                checked={selected.includes(o.value)}
                onChange={(e) => onChange(e.target.checked ? [...selected, o.value] : selected.filter((x) => x !== o.value))}
              />
              <span className="inline-flex items-center gap-1 rounded-full border border-slate-500 bg-white px-2.5 py-0.5 text-sm text-slate-900 peer-checked:border-blue-800 peer-checked:bg-blue-800 peer-checked:text-white peer-focus-visible:outline peer-focus-visible:outline-3 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-blue-700">
                {selected.includes(o.value) ? <span aria-hidden="true">✓</span> : null}
                {o.label}
              </span>
            </label>
            {info?.(o.value)}
          </span>
        ))}
      </div>
    </fieldset>
  );
}

function Flag({ id, termId, label, checked, onChange, ctx }: { id: string; termId: string; label: string; checked: boolean; onChange: (v: boolean) => void; ctx: Ctx }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <label htmlFor={id} className="flex items-start gap-2 text-sm font-medium">
        <input id={id} type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} className="mt-0.5 h-4 w-4 accent-blue-800" />
        {label}
      </label>
      <TermInfo term={ctx.tax.terms[termId]} country={ctx.country} text={ctx.termText} />
    </div>
  );
}

function VoltageSlider({ f, onChange, ctx }: { f: ExploreFilters; onChange: (p: Partial<ExploreFilters>) => void; ctx: Ctx }) {
  const { t } = ctx;
  const [lo, hi] = voltageBounds(ctx.tax);
  const vmin = f.voltageMin ?? lo;
  const vmax = f.voltageMax ?? hi;
  return (
    <details className="rounded-md border border-slate-300 bg-white p-2" open={ctx.level === "nerd" || f.voltageMin !== null || f.voltageMax !== null}>
      <summary className="cursor-pointer text-sm font-medium">{t("filters.advanced")}</summary>
      <div className="mt-2 flex flex-col gap-2">
        <FilterLabel termId="nominal-voltage" fallback={ctx.tax.terms["nominal-voltage"]?.label ?? t("filters.vmin")} ctx={ctx} />
        <label htmlFor="f-vmin" className="text-xs">
          {t("filters.vmin")}: <span className="tabular-nums">{vmin}</span>
        </label>
        <input id="f-vmin" type="range" min={lo} max={hi} step={10} value={vmin} onChange={(e) => {
          const v = Number(e.target.value);
          onChange({ voltageMin: v <= lo ? null : Math.min(v, vmax) });
        }} className="accent-blue-800" />
        <label htmlFor="f-vmax" className="text-xs">
          {t("filters.vmax")}: <span className="tabular-nums">{vmax}</span>
        </label>
        <input id="f-vmax" type="range" min={lo} max={hi} step={10} value={vmax} onChange={(e) => {
          const v = Number(e.target.value);
          onChange({ voltageMax: v >= hi ? null : Math.max(v, vmin) });
        }} className="accent-blue-800" />
      </div>
    </details>
  );
}

function ChemistryInfo({ id, ctx }: { id: string; ctx: Ctx }) {
  const c = ctx.tax.chemistries.find((x) => x.id === id);
  if (!c) return null;
  const { t } = ctx;
  const list = (title: string, items: string[]) =>
    items.length ? (
      <span className="mt-1 block">
        <span className="font-semibold">{title}</span>
        {items.map((i) => (
          <span key={i} className="block">
            · {i}
          </span>
        ))}
      </span>
    ) : null;
  return (
    <InfoTip label={c.label} href={`/${ctx.country}/learn/chemistry`} text={ctx.termText}>
      {c.explainer ? <span className="block">{c.explainer}</span> : null}
      {list(t("chem.pros"), c.pros)}
      {list(t("chem.cons"), c.cons)}
      {list(t("chem.care"), c.care)}
      {c.charge100 !== null ? (
        <span className="mt-1 block">
          {t("chem.charge100")}: {c.charge100 ? t("yes") : t("no")}
        </span>
      ) : null}
    </InfoTip>
  );
}

function FiltersPanel({
  filters: f,
  onChange,
  onReset,
  ctx,
}: {
  filters: ExploreFilters;
  onChange: (p: Partial<ExploreFilters>) => void;
  onReset: () => void;
  ctx: Ctx;
}) {
  const { t, level, tax } = ctx;
  const n = activeFilterCount(f);
  const more = level !== "simple";
  // Narrow screens: filters collapse behind a button so results stay above the fold. Always open on lg+.
  const [shown, setShown] = useState(false);
  return (
    <aside aria-labelledby="filters-heading" className="lg:sticky lg:top-4 lg:max-h-[calc(100vh-2rem)] lg:self-start lg:overflow-y-auto">
      <button
        type="button"
        aria-expanded={shown}
        aria-controls="filters-form"
        onClick={() => setShown((v) => !v)}
        className="w-full rounded-md border border-slate-500 px-4 py-2 text-left text-sm font-medium lg:hidden"
      >
        {t("filters.title")} {n ? `(${t("filters.active", { n })})` : ""} <span aria-hidden="true">{shown ? "▲" : "▼"}</span>
      </button>
      <form
        id="filters-form"
        role="search"
        aria-labelledby="filters-heading"
        onSubmit={(e) => e.preventDefault()}
        className={`${shown ? "flex" : "hidden"} mt-2 flex-col gap-4 rounded-lg border border-slate-300 bg-slate-50 p-4 lg:mt-0 lg:flex`}
      >
        <div className="flex items-baseline justify-between">
          <h2 id="filters-heading" className="font-semibold">
            {t("filters.title")} {n ? <span className="text-sm font-normal text-slate-700">({t("filters.active", { n })})</span> : null}
          </h2>
          {n ? (
            <button type="button" onClick={onReset} className="text-sm text-blue-800 underline underline-offset-2">
              {t("filters.reset")}
            </button>
          ) : null}
        </div>
        <NumberFilter id="priceMax" termId="new-price" label={`${t("filters.price")} (${ctx.currency})`} value={f.priceMax} step={1000} onChange={(v) => onChange({ priceMax: v })} ctx={ctx} />
        <Chips legend={t("filters.era")} termId="era" options={ERAS.map((e) => ({ value: e, label: e }))} selected={f.eras} onChange={(eras) => onChange({ eras })} ctx={ctx} />
        <Chips legend={t("filters.body")} termId="body-type" options={BODIES.map((b) => ({ value: b, label: t(`body.${b}` as MsgKey) }))} selected={f.bodies} onChange={(bodies) => onChange({ bodies })} ctx={ctx} />
        <NumberFilter id="rangeMin" termId="real-range" label={t("filters.range")} value={f.rangeMin} step={10} onChange={(v) => onChange({ rangeMin: v })} ctx={ctx} />
        <Flag id="f-fast400" termId="400v-charger-behaviour" label={t("filters.fast400")} checked={f.fast400} onChange={(fast400) => onChange({ fast400 })} ctx={ctx} />
        <Flag id="f-c100" termId="charge-to-100" label={t("filters.charge100")} checked={f.charge100} onChange={(charge100) => onChange({ charge100 })} ctx={ctx} />
        {more ? (
          <>
            <Chips legend={t("filters.segment")} termId="segment" options={SEGMENTS.map((s) => ({ value: s, label: t(`segment.${s}` as MsgKey) }))} selected={f.segments} onChange={(segments) => onChange({ segments })} ctx={ctx} />
            <Chips legend={t("filters.voltage")} termId="voltage-class" options={tax.voltageClasses.map((v) => ({ value: v.id, label: v.label }))} selected={f.voltageClasses} onChange={(voltageClasses) => onChange({ voltageClasses })} ctx={ctx} />
            <Chips
              legend={t("filters.chemistry")}
              termId="chemistry"
              options={tax.chemistries.map((c) => ({ value: c.id, label: c.label }))}
              selected={f.chemistries}
              onChange={(chemistries) => onChange({ chemistries })}
              ctx={ctx}
              info={(id) => <ChemistryInfo id={id} ctx={ctx} />}
            />
            <Chips legend={t("filters.cooling")} termId="cooling" options={tax.coolings.map((c) => ({ value: c.id, label: c.label }))} selected={f.coolings} onChange={(coolings) => onChange({ coolings })} ctx={ctx} />
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-1">
              <NumberFilter id="batteryMin" termId="usable-vs-gross" label={t("filters.battery")} value={f.batteryMin} onChange={(v) => onChange({ batteryMin: v })} ctx={ctx} />
              <NumberFilter id="dcMin" termId="dc-km-20min" label={t("filters.dc")} value={f.dcMin} step={5} onChange={(v) => onChange({ dcMin: v })} ctx={ctx} />
              <NumberFilter id="bootMin" termId="boot-volume" label={t("filters.boot")} value={f.bootMin} step={10} onChange={(v) => onChange({ bootMin: v })} ctx={ctx} />
              <NumberFilter id="lengthMax" termId="vehicle-length" label={t("filters.length")} value={f.lengthMax} step={50} onChange={(v) => onChange({ lengthMax: v })} ctx={ctx} />
              <NumberFilter id="towingMin" termId="towing-capacity" label={t("filters.towing")} value={f.towingMin} step={100} onChange={(v) => onChange({ towingMin: v })} ctx={ctx} />
            </div>
            <VoltageSlider f={f} onChange={onChange} ctx={ctx} />
          </>
        ) : null}
        <p className="text-xs text-slate-700">{t("filters.hint")}</p>
      </form>
    </aside>
  );
}

/* ---------- columns ---------- */

interface Col {
  id: string;
  key: SortKey | null;
  label: MsgKey;
  term?: string;
  num?: boolean;
  levels: readonly Level[];
  cell: (r: ExploreRow, c: Ctx) => ReactNode;
}

const ALL: readonly Level[] = LEVELS;
const DN: readonly Level[] = ["detailed", "nerd"];
const N: readonly Level[] = ["nerd"];

function num(r: ExploreRow, c: Ctx, v: number | null | undefined, field: string, unit?: string, digits = 1, note?: string, claim = false) {
  return (
    <Num
      value={v}
      unit={unit}
      provenance={r.provenance[field]}
      sources={c.sources}
      locale={c.locale}
      labels={c.labels}
      digits={digits}
      note={note}
      claim={claim}
      level={c.level}
      asOf={c.asOf}
      focusable={!c.inTable}
    />
  );
}

function rangeNote(r: ExploreRow, c: Ctx): string | undefined {
  if (!r.real_range_rung) return undefined;
  const label = c.t(`rung.${r.real_range_rung}` as MsgKey);
  return c.level === "nerd" ? `${label} [${r.real_range_rung}]` : label;
}

const NO_NAMES = new Map<string, string>();

function named(map: Map<string, string>, id: string | null | undefined, c: Ctx): string {
  if (!id) return "—";
  if (id === "not-disclosed") return c.t("notDisclosed");
  return map.get(id) ?? id;
}

function priceCell(r: ExploreRow, c: Ctx) {
  const amount = priceFor(r, c.code);
  const currency = r.price_new?.[c.code]?.currency ?? c.currency;
  return (
    <Num
      value={amount}
      text={amount !== null ? formatMoney(amount, currency, c.locale) : undefined}
      provenance={r.provenance[`price_new.${c.code}`] ?? r.provenance.price_new}
      sources={c.sources}
      locale={c.locale}
      labels={c.labels}
      level={c.level}
      asOf={c.asOf}
      focusable={!c.inTable}
    />
  );
}

function charger400(r: ExploreRow, c: Ctx) {
  // No DC figure means "no DC data": never imply the car fast-charges (shared rule, src/lib/dc.ts).
  if (!hasDcData(r)) return <Missing label={c.t("num.noDc")} />;
  if (!r.charger_400v_mode) return <Missing label={c.t("num.noData")} />;
  return (
    <span className="flex flex-col">
      <span>
        {c.t(`c400.${r.charger_400v_mode}` as MsgKey)}
        {r.fast_on_400v != null ? ` · ${r.fast_on_400v ? c.t("yes") : c.t("no")}` : ""}
      </span>
      {r.charger_400v_kw != null ? num(r, c, r.charger_400v_kw, "charger_400v_kw", "kW", 0) : null}
    </span>
  );
}

const COLS: Col[] = [
  { id: "car", key: "name", label: "col.car", levels: ALL, cell: () => null },
  { id: "gen", key: null, label: "col.generation", term: "generation", levels: DN, cell: (r, c) => (
      <Link href={generationHref(c.country, r)} tabIndex={c.inTable ? -1 : undefined} className="underline decoration-slate-400 underline-offset-2 hover:text-blue-900">
        {r.generation_name}
      </Link>
    ) },
  { id: "variant", key: null, label: "col.variant", term: "variant", levels: DN, cell: (r) => r.variant_name },
  { id: "years", key: "years", label: "col.years", term: "model-years", levels: ALL, cell: (r, c) => formatYears(r.year_start, r.year_end, c.t("years.now")) },
  { id: "era", key: "era", label: "col.era", term: "era", levels: DN, cell: (r) => r.era },
  { id: "range", key: "range", label: "col.range", term: "real-range", num: true, levels: ALL, cell: (r, c) => num(r, c, r.real_range_km, "real_range_km", "km", 0, rangeNote(r, c)) },
  { id: "battery", key: "battery", label: "col.battery", term: "usable-vs-gross", num: true, levels: DN, cell: (r, c) => num(r, c, r.battery_kwh_net, "battery_kwh_net", "kWh") },
  { id: "dc", key: "dc", label: "col.dc", term: "dc-km-20min", num: true, levels: ALL, cell: (r, c) => num(r, c, r.dc_km_per_20min, "dc_km_per_20min", "km", 0) },
  { id: "ac", key: "ac", label: "col.ac", term: "ac-charging", num: true, levels: DN, cell: (r, c) => num(r, c, r.ac_km_per_h, "ac_km_per_h", "km/h", 0) },
  { id: "price", key: "price", label: "col.price", term: "new-price", num: true, levels: ALL, cell: priceCell },
  { id: "rdw", key: "rdw", label: "col.rdw", term: "registrations-nl", num: true, levels: DN, cell: (r, c) => num(r, c, r.registered_count_nl, "registered_count_nl", undefined, 0) },
  { id: "voltage", key: null, label: "col.voltage", term: "voltage-class", levels: DN, cell: (r, c) => named(c.names.voltage, r.voltage_class_id, c) },
  { id: "nominal", key: null, label: "col.voltage", term: "nominal-voltage", num: true, levels: N, cell: (r, c) => num(r, c, r.voltage_nominal_v, "voltage_nominal_v", "V", 0) },
  { id: "charger400", key: null, label: "col.charger400", term: "400v-charger-behaviour", levels: N, cell: charger400 },
  { id: "chem", key: null, label: "col.chemistry", term: "chemistry", levels: DN, cell: (r, c) => named(c.names.chem, r.chemistry_id, c) + (c.level === "nerd" && r.cell_format ? ` · ${named(NO_NAMES, r.cell_format, c)}` : "") },
  { id: "cool", key: null, label: "col.cooling", term: "cooling", levels: N, cell: (r, c) => named(c.names.cool, r.cooling_id, c) },
  { id: "platform", key: null, label: "col.platform", levels: N, cell: (r) => r.platform_name ?? "—" },
  { id: "pack", key: null, label: "col.pack", levels: N, cell: (r, c) => named(NO_NAMES, r.battery_pack_id, c) },
  { id: "quality", key: "quality", label: "col.quality", term: "quality-tier", levels: ALL, cell: (r, c) => <QualityBadge tier={r.quality_tier} label={c.t(`tier.${r.quality_tier}`)} help={c.t(`tier.${r.quality_tier}.help`)} /> },
];

/** Columns shown at a level. Exported for tests. */
export function columnsFor(level: Level): string[] {
  return COLS.filter((c) => c.levels.includes(level)).map((c) => c.id);
}

/* ---------- table ---------- */

function ExploreTable({ rows, state, onSort, ctx: outer }: { rows: ExploreRow[]; state: ExploreState; onSort: (k: SortKey) => void; ctx: Ctx }) {
  const ctx = useMemo(() => ({ ...outer, inTable: true }), [outer]);
  const { t, level } = ctx;
  const cols = COLS.filter((c) => c.levels.includes(level));
  return (
    <div className="max-h-[75vh] overflow-auto rounded-lg border border-slate-300" tabIndex={0} aria-labelledby="results-heading">
      <table className="w-max min-w-full border-collapse text-sm" data-testid="explore-table">
        <thead>
          <tr>
            {cols.map((col, i) => {
              const sorted = col.key && state.sort === col.key;
              const ariaSort = sorted ? (state.dir === "asc" ? "ascending" : "descending") : col.key ? "none" : undefined;
              const term = col.term ? ctx.tax.terms[col.term] : undefined;
              const label = <TermLabel term={term} fallback={t(col.label)} showTechnical={level !== "simple"} />;
              return (
                <th
                  key={col.id}
                  scope="col"
                  aria-sort={ariaSort}
                  className={`sticky top-0 min-w-24 max-w-44 border-b border-slate-300 bg-slate-100 px-3 py-2 text-left align-bottom font-semibold ${i === 0 ? "left-0 z-30" : "z-20"}`}
                >
                  <span className={`flex items-end gap-1 ${col.num ? "justify-end" : ""}`}>
                    {col.key ? (
                      <button
                        type="button"
                        onClick={() => onSort(col.key!)}
                        aria-label={t("sort.by", { col: term?.label ?? t(col.label) })}
                        className="inline-flex items-end gap-1 rounded-sm text-left hover:underline"
                      >
                        {label}
                        <span aria-hidden="true" className="text-xs text-slate-600">
                          {sorted ? (state.dir === "asc" ? "▲" : "▼") : "↕"}
                        </span>
                      </button>
                    ) : (
                      label
                    )}
                    <TermInfo term={term} country={ctx.country} text={ctx.termText} />
                  </span>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.variant_id} className="border-b border-slate-200 last:border-0 hover:bg-slate-50" data-testid="explore-row">
              <th scope="row" className="sticky left-0 z-10 bg-white px-3 py-2 text-left font-medium">
                <div className="flex items-center gap-2">
                  <RowActions row={r} t={t} />
                  <span className="flex flex-col">
                    <Link href={variantHref(ctx.country, r)} className="whitespace-nowrap text-blue-800 underline underline-offset-2 hover:text-blue-950">
                      {r.make_name} {r.model_name}
                      {level !== "simple" ? <span className="sr-only"> {r.generation_name} {r.variant_name}</span> : null}
                    </Link>
                    {level === "nerd" ? <RowSources row={r} ctx={ctx} /> : null}
                    {level === "simple" ? (
                      <span className="whitespace-nowrap text-xs font-normal text-slate-700">
                        {r.generation_name} · {r.variant_name}
                      </span>
                    ) : null}
                  </span>
                </div>
              </th>
              {cols.slice(1).map((col) => (
                <td key={col.id} className={`px-3 py-2 ${col.num ? "text-right" : "whitespace-nowrap"}`}>
                  {col.cell(r, ctx)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ---------- per-row sources (Nerd level, keyboard access to provenance) ---------- */

/** Provenance key → column label, in display order. Price uses `price_new.<CC>`. */
const PROV_LABELS: readonly [string, MsgKey][] = [
  ["real_range_km", "col.range"],
  ["battery_kwh_net", "col.battery"],
  ["dc_km_per_20min", "col.dc"],
  ["dc_km_per_10min", "col.dc"],
  ["dc_peak_kw", "col.dcPeak"],
  ["ac_km_per_h", "col.ac"],
  ["price_new", "col.price"],
  ["registered_count_nl", "col.rdw"],
  ["voltage_nominal_v", "col.voltage"],
  ["charger_400v_kw", "col.charger400"],
  ["boot_l", "filters.boot"],
  ["length_mm", "filters.length"],
  ["towing_kg", "filters.towing"],
];

/** Rows of the per-row sources list: label, source names, confidence. Exported for tests. */
export function rowSources(r: ExploreRow, code: Country, sources: Record<string, string>) {
  const out: { key: string; label: MsgKey; names: string; confidence: FieldProvenance["confidence"]; estimate: boolean }[] = [];
  const dc = hasDcData(r);
  for (const [key, label] of PROV_LABELS) {
    if (key === "charger_400v_kw" && !dc) continue;
    const p = key === "price_new" ? (r.provenance[`price_new.${code}`] ?? r.provenance.price_new) : r.provenance[key];
    const value = key === "price_new" ? priceFor(r, code) : (r as unknown as Record<string, unknown>)[key];
    if (!p || value === null || value === undefined) continue;
    out.push({ key, label, names: p.source_ids.map((s) => sources[s] ?? s).join(", "), confidence: p.confidence, estimate: !!p.estimate });
  }
  return out;
}

function RowSources({ row, ctx }: { row: ExploreRow; ctx: Ctx }) {
  const { buttonProps, popoverProps } = usePopover();
  const list = rowSources(row, ctx.code, ctx.sources);
  if (!list.length) return null;
  const { t } = ctx;
  return (
    <span className="inline-flex">
      <button
        {...buttonProps}
        aria-label={t("explore.rowSources", { name: displayName(row) })}
        className="w-fit whitespace-nowrap rounded-sm text-left text-xs font-normal text-blue-800 underline decoration-dotted underline-offset-2"
        data-testid="row-sources"
      >
        {t("explore.sources")}
      </button>
      <span {...popoverProps}>
        <span className="mb-1 block font-semibold">{displayName(row)}</span>
        {list.map((x) => (
          <span key={x.key} className="block">
            <span className="font-semibold">{t(x.label)}:</span> {x.names} · {ctx.labels.conf[x.confidence]}
            {x.estimate ? ` · ${ctx.labels.estimate}` : ""}
          </span>
        ))}
        <span className="mt-1 block text-slate-700">{ctx.asOf}</span>
      </span>
    </span>
  );
}

/* ---------- cards ---------- */

function Card({ row: r, ctx: c }: { row: ExploreRow; ctx: Ctx }) {
  const { t, level } = c;
  const item = (label: string, value: ReactNode) => (
    <div className="flex flex-col">
      <dt className="text-xs text-slate-700">{label}</dt>
      <dd>{value}</dd>
    </div>
  );
  const term = (id: string, fallback: MsgKey) => c.tax.terms[id]?.label ?? t(fallback);
  const more = level !== "simple";
  return (
    <li className="flex flex-col gap-3 rounded-lg border border-slate-300 bg-white p-4" data-testid="explore-card">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-semibold">
            <Link href={variantHref(c.country, r)} className="text-blue-800 underline underline-offset-2 hover:text-blue-950">
              {r.make_name} {r.model_name}
            </Link>
          </h3>
          <p className="text-sm text-slate-700">
            {r.generation_name} · {r.variant_name} · {formatYears(r.year_start, r.year_end, t("years.now"))}
          </p>
        </div>
        <QualityBadge tier={r.quality_tier} label={t(`tier.${r.quality_tier}`)} help={t(`tier.${r.quality_tier}.help`)} />
      </div>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        {item(term("real-range", "col.range"), num(r, c, r.real_range_km, "real_range_km", "km", 0, rangeNote(r, c)))}
        {item(`${term("dc-km-20min", "col.dc")} (${t("col.dc20.unit")})`, num(r, c, r.dc_km_per_20min, "dc_km_per_20min", "km", 0))}
        {item(term("new-price", "col.price"), priceCell(r, c))}
        {item(t("price.used"), <PriceBand currency={c.currency} locale={c.locale} notEnoughLabel={t("price.notEnough")} samplesLabel={t("price.samples")} />)}
        {more ? (
          <>
            {item(term("usable-vs-gross", "col.battery"), num(r, c, r.battery_kwh_net, "battery_kwh_net", "kWh"))}
            {item(`${t("col.dc")} (${t("col.dc.unit")})`, num(r, c, r.dc_km_per_10min, "dc_km_per_10min", "km", 0))}
            {item(term("peak-kw", "col.dcPeak"), num(r, c, r.dc_peak_kw, "dc_peak_kw", "kW", 0, undefined, r.dc_peak_kw_is_claim === true))}
            {item(term("ac-charging", "col.ac"), num(r, c, r.ac_km_per_h, "ac_km_per_h", "km/h", 0))}
            {item(term("voltage-class", "col.voltage"), named(c.names.voltage, r.voltage_class_id, c))}
            {item(term("chemistry", "col.chemistry"), named(c.names.chem, r.chemistry_id, c))}
            {r.registered_count_nl != null ? item(term("registrations-nl", "col.rdw"), num(r, c, r.registered_count_nl, "registered_count_nl", undefined, 0)) : null}
            {item(term("era", "col.era"), r.era)}
          </>
        ) : null}
        {level === "nerd" ? (
          <>
            {item(term("cooling", "col.cooling"), named(c.names.cool, r.cooling_id, c))}
            {item(term("400v-charger-behaviour", "col.charger400"), charger400(r, c))}
            {item(term("nominal-voltage", "col.voltage"), num(r, c, r.voltage_nominal_v, "voltage_nominal_v", "V", 0))}
            {item(t("col.platform"), r.platform_name ?? "—")}
            {item(t("col.pack"), named(NO_NAMES, r.battery_pack_id, c))}
          </>
        ) : null}
      </dl>
      <div className="mt-auto">
        <RowActions row={r} t={t} withText />
      </div>
    </li>
  );
}

/* ---------- favourite + compare ---------- */

function RowActions({ row, t, withText = false }: { row: ExploreRow; t: T; withText?: boolean }) {
  const favs = useListStore(favouriteStore);
  const cmp = useListStore(compareStore);
  const fullId = useId();
  const name = displayName(row);
  const fav = favs.includes(row.variant_id);
  const inCmp = cmp.some((c) => c.id === row.variant_id);
  const full = !inCmp && cmp.length >= COMPARE_MAX;
  return (
    <div className="flex items-center gap-1">
      <button
        type="button"
        aria-pressed={fav}
        aria-label={t(fav ? "fav.remove" : "fav.add", { name })}
        onClick={() => favouriteStore.toggle(row.variant_id)}
        className="grid h-8 w-8 place-items-center rounded-full hover:bg-slate-100"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true" className={`h-5 w-5 ${fav ? "fill-red-700 stroke-red-700" : "fill-none stroke-slate-700"}`} strokeWidth="2">
          <path d="M12 21s-7.5-4.6-9.5-9.2C1 8.2 3.4 4.5 7 4.5c2 0 3.6 1.1 5 3 1.4-1.9 3-3 5-3 3.6 0 6 3.7 4.5 7.3C19.5 16.4 12 21 12 21z" />
        </svg>
      </button>
      {/* Full tray: aria-disabled (not disabled) so keyboard and screen-reader users still reach it and hear why. */}
      <button
        type="button"
        aria-pressed={inCmp}
        aria-label={inCmp ? t("compare.removeLabel", { name }) : t("compare.addLabel", { name })}
        aria-disabled={full || undefined}
        aria-describedby={full ? fullId : undefined}
        title={full ? t("compare.full", { max: COMPARE_MAX }) : undefined}
        data-testid="compare-toggle"
        onClick={() => {
          if (inCmp) compareStore.remove(row.variant_id);
          else if (!full) compareStore.add({ id: row.variant_id, label: name });
        }}
        className={`flex h-8 items-center gap-1 rounded-full border px-2 text-xs font-medium aria-disabled:cursor-not-allowed aria-disabled:opacity-50 ${inCmp ? "border-blue-800 bg-blue-800 text-white" : "border-slate-500 text-slate-900 hover:bg-slate-100"}`}
      >
        <span aria-hidden="true">{inCmp ? "✓" : "+"}</span>
        <span className={withText ? "" : "sr-only"}>{t("compare.add")}</span>
      </button>
      {full ? (
        <span id={fullId} className="sr-only">
          {t("compare.full", { max: COMPARE_MAX })}
        </span>
      ) : null}
    </div>
  );
}
