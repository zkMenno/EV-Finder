"use client";
// Explore: one table of new and used EVs. The server renders the first rows; this component
// hydrates them, then fetches the compact catalogue JSON from our own origin and filters
// and sorts the full list in the browser. All state lives in the URL (see lib/state.ts).
// Taxonomy-driven filters (voltage, chemistry, cooling) read their options from data.
import { loadClientCatalogue } from "@/lib/client-catalogue";
import { onAnswers, onFilters, publishFilters } from "@/lib/filter-bus";
import { resolveProfile, suggestedScore, type Answers } from "@/lib/shortlist";
import { profileName, SuggestedSort } from "./SuggestedSort";
import type { Country, Currency, FieldProvenance } from "@ev/schema";
import Link from "next/link";
import { useCallback, useEffect, useId, useMemo, useRef, useState, type ReactNode } from "react";
import { generationHref, variantHref } from "@/app/[country]/[lang]/ev/_lib/routes";
import type { CountrySlug, Lang } from "@/config/countries";
import { makeT, type Dict, type MsgKey, type T } from "@/i18n/t";
import { compareStore, COMPARE_MAX } from "@/lib/compare-store";
import { hasDcData } from "@/lib/dc";
import type { ExploreRow } from "@/lib/explore-data";
import { favouriteStore } from "@/lib/favourites";
import { applyFilters, displayName, mostRestrictive, priceFor, sortRows, withoutGroup, type FilterGroup } from "@/lib/filters";
import { formatMoney, formatYears, localeFor } from "@/lib/format";
import { effectiveLoan, monthlyFor, readPayMode, writePayMode, type EffectiveLoan, type FinanceProfileView, type PayMode } from "@/lib/finance";
import { LeaseNotice, LoanBox, PayModeToggle, useLoanSettings, type FinanceUi } from "@/components/PriceMode";
import { siteBase } from "@/lib/site-paths";
import {
  activeFilterCount,
  BODIES,
  defaultFilters,
  ERAS,
  EXPLORE_PARAM_KEYS,
  LEVEL_KEY,
  LEVELS,
  MENU_SORTS,
  nextSort,
  sortBy,
  SEGMENTS,
  toSearchParams,
  VIEW_KEY,
  type ExploreFilters,
  type ExploreState,
  type Level,
  type NumericFilter,
  type SortKey,
  TRIP_KEY,
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
// Type only: the trip module itself is loaded with import() on demand (T-036, JS budget).
import type * as TripModuleNs from "./trip/TripModule";

type TripModule = typeof TripModuleNs;
type CarFit = TripModuleNs.CarFit;
type TripSettings = TripModuleNs.TripSettings;

const loadTripModule = (): Promise<TripModule> => import("./trip/TripModule");

const PAGE = 50;

export interface ExploreProps {
  country: CountrySlug;
  code: Country;
  currency: Currency;
  lang: Lang;
  dict: Dict;
  initialState: ExploreState;
  /** The hero's picker answers from the URL (T-067 Suggested sort). */
  initialAnswers?: Answers;
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
  /** TRIP_FIT=1 (server env): shows the trip fit quick check. Off → no trip UI at all. */
  tripFit?: boolean;
  /** This country's finance profile (data/taxonomy/finance_profiles.yaml), Decision 017. */
  finance: FinanceProfileView | null;
  /** The URL sets ?pay= (else the remembered price mode wins). */
  payFromUrl: boolean;
  /** The release has shortlist_scores.json (Decision 065); without it "Suggested" can't order. */
  hasScores?: boolean;
  /** The page's default view, left out of the URL (T-130: cards on /cars). */
  defaultView?: View;
  /** Link to the "How we rank" explanation of the Most popular order (T-130). */
  howWeRankHref?: string;
}

interface Ctx {
  t: T;
  locale: string;
  labels: NumLabels;
  sources: Record<string, string>;
  code: Country;
  currency: Currency;
  country: CountrySlug;
  /** "/{country}/{lang}": prefix for every link (Decision 015). */
  base: string;
  tax: UiTaxonomy;
  names: { voltage: Map<string, string>; chem: Map<string, string>; cool: Map<string, string> };
  termText: TermText;
  level: Level;
  asOf: string;
  /** Price mode and the effective loan inputs (Decision 017). */
  pay: PayMode;
  loan: EffectiveLoan;
  /**
   * Inside the table, numbers and secondary links are not Tab stops (one stop per row for the
   * name link, heart and compare; provenance via the variant page or the Nerd "sources" button).
   */
  inTable?: boolean;
  /** Trip fit verdicts (T-036) once the user entered a trip; drives the "Your trips" column. */
  trip?: { mod: TripModule; fits: Map<string, CarFit>; ui: TripModuleNs.TripUi };
}

export function Explore(props: ExploreProps) {
  const t = useMemo(() => makeT(props.dict), [props.dict]);
  const locale = localeFor(props.lang);

  const [state, setState] = useState<ExploreState>(props.initialState);
  const [answers, setAnswers] = useState<Answers | null>(props.initialAnswers ?? null);
  useEffect(() => onAnswers(setAnswers), []);
  const rp = useMemo(() => (answers ? resolveProfile(answers) : null), [answers]);
  const [all, setAll] = useState<ExploreRow[] | null>(null);
  const [sources, setSources] = useState(props.sources);
  const [limit, setLimit] = useState(PAGE);
  // True once the user changed anything: from then on counts come from the (partial or full) client list.
  const [dirty, setDirty] = useState(false);
  const lastUrl = useRef(toSearchParams(props.initialState, props.defaultView).toString());
  // Trip fit (T-036): module loaded on demand, answers from localStorage only.
  const [tripMod, setTripMod] = useState<TripModule | null>(null);
  const [tripSettings, setTripSettings] = useState<TripSettings | null>(null);
  const [tripOpen, setTripOpen] = useState(false);
  const tripFit = props.tripFit === true;
  const [loanSettings, setLoanSettings] = useLoanSettings();
  const loan = useMemo(() => effectiveLoan(props.finance, loanSettings), [props.finance, loanSettings]);

  const tripRows = all ?? props.initialRows;
  const fits = useMemo(
    () => (tripMod && tripFit ? tripMod.computeFits(tripRows, tripSettings, props.country) : null),
    [tripMod, tripFit, tripRows, tripSettings, props.country],
  );

  const ctx: Ctx = useMemo(
    () => ({
      t,
      locale,
      labels: numLabels(t, { base: siteBase(props.country, props.lang), terms: props.taxonomy.terms }),
      sources,
      code: props.code,
      currency: props.currency,
      country: props.country,
      base: siteBase(props.country, props.lang),
      tax: props.taxonomy,
      names: {
        voltage: new Map(props.taxonomy.voltageClasses.map((v) => [v.id, v.label])),
        chem: new Map(props.taxonomy.chemistries.map((v) => [v.id, v.label])),
        cool: new Map(props.taxonomy.coolings.map((v) => [v.id, v.label])),
      },
      termText: { about: t("term.about"), learnMore: t("term.learnMore") },
      level: state.level,
      asOf: props.asOf,
      pay: state.pay,
      loan,
      trip: tripMod && fits ? { mod: tripMod, fits, ui: {
              t,
              level: state.level,
              locale,
              labels: numLabels(t, { base: siteBase(props.country, props.lang), terms: props.taxonomy.terms }),
              country: props.country,
              gloss: { base: siteBase(props.country, props.lang), terms: props.taxonomy.terms, text: { about: t("term.about"), learnMore: t("term.learnMore") } },
            } } : undefined,
    }),
    [t, locale, sources, props.code, props.currency, props.country, props.lang, props.taxonomy, state.level, props.asOf, state.pay, loan, tripMod, fits],
  );

  const openTrip = () => {
    setTripOpen(true);
    if (tripMod) return;
    loadTripModule()
      .then((m) => {
        setTripMod(m);
        setTripSettings(m.loadTripSettings() ?? m.normalizeTripSettings(null));
      })
      .catch(() => setTripOpen(false));
  };

  // A trip saved earlier: load the module after first paint so the column comes back.
  useEffect(() => {
    if (!tripFit || !readStorage(TRIP_KEY)) return;
    let live = true;
    loadTripModule()
      .then((m) => {
        if (!live) return;
        setTripMod(m);
        setTripSettings(m.loadTripSettings());
      })
      .catch(() => {
        /* no trip column; Explore works as before */
      });
    return () => {
      live = false;
    };
  }, [tripFit]);

  const changeTrip = (next: TripSettings) => {
    setTripSettings(next);
    tripMod?.saveTripSettings(next);
  };
  const clearTrip = () => {
    tripMod?.clearTripSettings();
    setTripSettings(tripMod ? tripMod.normalizeTripSettings(null) : null);
    if (state.filters.tripFit) update({ ...state, filters: { ...state.filters, tripFit: false } });
  };

  // Full list, fetched from our own origin after first paint (shared with the hero, T-080).
  useEffect(() => {
    let live = true;
    void loadClientCatalogue(props.dataUrl).then((c) => {
      if (live && c) {
        setAll(c.rows);
        setSources(c.sources);
      }
    });
    return () => {
      live = false;
    };
  }, [props.dataUrl]);

  // The hero's refine filters are Explore's filters (same URL params, T-080).
  useEffect(
    () =>
      onFilters("explore", (filters) => {
        setDirty(true);
        setLimit(PAGE);
        setState((s) => ({ ...s, filters: { ...filters, tripFit: s.filters.tripFit } }));
      }),
    [],
  );

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
    if (!props.payFromUrl) {
      const stored = readPayMode();
      if (stored && stored !== props.initialState.pay) patch.pay = stored;
    }
    // One-off read of browser-only preferences after hydration (reading them during render would
    // mismatch the server HTML), so a setState here is intended.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (Object.keys(patch).length) setState((s) => ({ ...s, ...patch }));
  }, [props.viewFromUrl, props.levelFromUrl, props.payFromUrl, props.initialState.view, props.initialState.level, props.initialState.pay]);

  // State → URL (replaceState: no server round trip, links stay shareable).
  useEffect(() => {
    const qs = toSearchParams(state, props.defaultView).toString();
    if (qs === lastUrl.current) return;
    lastUrl.current = qs;
    const url = new URL(window.location.href);
    for (const k of EXPLORE_PARAM_KEYS) url.searchParams.delete(k);
    new URLSearchParams(qs).forEach((v, k) => url.searchParams.set(k, v));
    window.history.replaceState(null, "", url.pathname + url.search + url.hash);
  }, [state, props.defaultView]);

  const update = (next: ExploreState) => {
    setDirty(true);
    setLimit(PAGE);
    setState(next);
    if (next.filters !== state.filters) publishFilters({ filters: next.filters, from: "explore" });
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
  const setPay = (pay: PayMode) => {
    writePayMode(pay);
    setState({ ...state, pay });
  };
  const financeUi: FinanceUi = {
    t,
    locale,
    currency: props.currency,
    code: props.code,
    level: state.level,
    base: ctx.base,
    terms: props.taxonomy.terms,
    termText: ctx.termText,
  };

  // The filter pipeline Explore shows: filters + (with a trip entered) the winter trip fit.
  const runFilters = useCallback(
    (f: ExploreFilters) => {
      let out = applyFilters(all ?? props.initialRows, f, props.code);
      // "Does my trips in winter": keeps ✓ and ⚠; only with a trip entered (the URL flag alone does nothing).
      if (f.tripFit && fits) out = out.filter((r) => {
        const v = fits.get(r.variant_id)?.verdict;
        return v === "ok" || v === "tight";
      });
      return out;
    },
    [all, props.initialRows, props.code, fits],
  );
  // "Suggested" sort (T-067): the release's score for the hero's profile (Decision 065); a car the
  // release rules out, or doesn't score, goes last.
  const scorer = useMemo(() => (rp ? (r: ExploreRow) => suggestedScore(r, rp) : undefined), [rp]);
  const matches = useMemo(() => {
    if (!all && !dirty && !(state.sort === "suggested" && answers !== props.initialAnswers)) return props.initialRows;
    return sortRows(runFilters(state.filters), state.sort, state.dir, props.code, scorer);
  }, [all, dirty, runFilters, state.filters, state.sort, state.dir, props.code, props.initialRows, scorer, answers, props.initialAnswers]);
  // Empty state with a reason: the one filter whose removal brings back the most cars.
  const relax = useMemo(
    () => (matches.length === 0 && (all || dirty) ? mostRestrictive(state.filters, (f) => runFilters(f).length) : null),
    [matches.length, all, dirty, state.filters, runFilters],
  );

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
            <span className="inline-flex items-center">
              <Toggle
                label={t("level")}
                options={LEVELS.map((l) => ({ value: l, label: t(`level.${l}`) }))}
                value={state.level}
                onChange={setLevel}
                testId="level-switch"
              />
              <TermInfo term={props.taxonomy.terms["detail-level"]} base={ctx.base} text={ctx.termText} />
            </span>
            <Toggle
              label={t("explore.view")}
              options={(["table", "cards"] as const).map((v) => ({ value: v, label: t(`explore.view.${v}`) }))}
              value={state.view}
              onChange={setView}
            />
          </div>
        </div>

        <SuggestedSort
          rp={rp}
          active={state.sort === "suggested"}
          onToggle={() => update({ ...state, sort: state.sort === "suggested" ? null : "suggested", dir: "desc" })}
          t={t}
          termText={ctx.termText}
          profileName={rp ? profileName(rp, t) : ""}
          hasScores={props.hasScores !== false}
        />
        <SortMenu state={state} onChange={(k) => update(sortBy(state, k))} t={t} />
        {state.sort === "popular" ? (
          <p className="mb-3 text-sm text-slate-700" data-testid="popular-why">
            {t("sort.popular.why")}{" "}
            {props.howWeRankHref ? (
              <a href={props.howWeRankHref} className="font-medium text-blue-800 underline underline-offset-2">
                {t("sort.popular.how")}
              </a>
            ) : null}
          </p>
        ) : null}
        <div className="mb-3 flex flex-col gap-2">
          <PayModeToggle value={state.pay} onChange={setPay} ui={financeUi} />
          {state.pay === "loan" ? <LoanBox profile={props.finance} settings={loanSettings} onChange={setLoanSettings} ui={financeUi} /> : null}
          {state.pay === "lease" ? <LeaseNotice ui={financeUi} /> : null}
        </div>

        {tripFit ? (
          <TripBar
            ctx={ctx}
            open={tripOpen}
            settings={tripSettings}
            mod={tripMod}
            filterOn={state.filters.tripFit}
            onOpen={openTrip}
            onFilter={(on) => setFilter({ tripFit: on })}
          />
        ) : null}
        {tripFit && tripOpen ? (
          tripMod && tripSettings ? (
            <tripMod.TripPanel
              settings={tripSettings}
              onChange={changeTrip}
              onClose={() => setTripOpen(false)}
              onClear={clearTrip}
              fits={fits}
              ui={{ t, level: state.level, locale, labels: ctx.labels, country: props.country, gloss: { base: ctx.base, terms: ctx.tax.terms, text: ctx.termText } }}
            />
          ) : (
            <p className="mb-4 text-sm text-slate-700">{t("trip.loading")}</p>
          )
        ) : null}

        {rows.length === 0 ? (
          <EmptyState
            ctx={ctx}
            filters={state.filters}
            relax={relax}
            onRemove={(g) => update({ ...state, filters: withoutGroup(state.filters, g) })}
            onReset={() => update({ ...state, filters: defaultFilters() })}
          />
        ) : state.view === "table" ? (
          <ExploreTable rows={rows} state={state} onSort={(k) => update(nextSort(state, k))} ctx={ctx} />
        ) : (
          <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3" data-testid="explore-cards">
            {firstOfGeneration(rows).map(([r, first]) => (
              // "#n popular" once per generation: on its first variant in the current order (T-130).
              <Card key={r.variant_id} row={r} ctx={ctx} popTag={first} />
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

/* ---------- trip fit entry point (T-036) ---------- */

/** Label of one filter group as the filters panel shows it, with chosen values where it has them. */
function groupLabel(g: FilterGroup, f: ExploreFilters, c: Ctx): string {
  const { t } = c;
  const list = (label: string, values: string[]) => (values.length ? `${label}: ${values.join(", ")}` : label);
  switch (g) {
    case "priceMax": return t("filters.price");
    case "eras": return list(t("filters.era"), f.eras);
    case "segments": return list(t("filters.segment"), f.segments.map((v) => t(`segment.${v}` as MsgKey)));
    case "bodies": return list(t("filters.body"), f.bodies.map((v) => t(`body.${v}` as MsgKey)));
    case "rangeMin": return t("filters.range");
    case "batteryMin": return t("filters.battery");
    case "dcMin": return t("filters.dc");
    case "bootMin": return t("filters.boot");
    case "lengthMax": return t("filters.length");
    case "towingMin": return t("filters.towing");
    case "seatsMin": return t("filters.seats");
    case "acMin": return t("filters.ac");
    case "yearMin": return t("filters.years");
    case "makes": return list(t("filters.makes"), f.makes);
    case "excludeMakes": return list(t("filters.excludeMakes"), f.excludeMakes);
    case "voltageClasses": return list(t("filters.voltage"), f.voltageClasses.map((v) => named(c.names.voltage, v, c)));
    case "voltageMin": return t("filters.vrange");
    case "fast400": return t("filters.fast400");
    case "chemistries": return list(t("filters.chemistry"), f.chemistries.map((v) => named(c.names.chem, v, c)));
    case "coolings": return list(t("filters.cooling"), f.coolings.map((v) => named(c.names.cool, v, c)));
    case "charge100": return t("filters.charge100");
    case "tripFit": return t("trip.filter");
  }
}

/** "No cars match": names the most restrictive filter and offers to remove it (or reset all). */
function EmptyState({
  ctx,
  filters,
  relax,
  onRemove,
  onReset,
}: {
  ctx: Ctx;
  filters: ExploreFilters;
  relax: { group: FilterGroup; count: number } | null;
  onRemove: (g: FilterGroup) => void;
  onReset: () => void;
}) {
  const { t } = ctx;
  const name = relax ? groupLabel(relax.group, filters, ctx) : "";
  return (
    <div className="flex flex-col items-center gap-3 rounded-md border border-dashed border-slate-400 p-6 text-center text-slate-800" data-testid="explore-empty" role="status">
      <p>{relax ? t("explore.noResults.reason", { filter: name, n: relax.count }) : t("explore.noResults")}</p>
      <div className="flex flex-wrap justify-center gap-3">
        {relax ? (
          <button
            type="button"
            onClick={() => onRemove(relax.group)}
            className="min-h-9 rounded-md border border-blue-800 bg-blue-800 px-3 text-sm font-semibold text-white hover:bg-blue-900"
            data-testid="explore-empty-remove"
            data-group={relax.group}
          >
            {t("explore.noResults.remove", { filter: name })}
          </button>
        ) : null}
        <button type="button" onClick={onReset} className="min-h-9 rounded-md border border-slate-400 px-3 text-sm text-blue-800 underline underline-offset-2">
          {t("filters.reset")}
        </button>
      </div>
    </div>
  );
}

function TripBar({
  ctx,
  open,
  settings,
  mod,
  filterOn,
  onOpen,
  onFilter,
}: {
  ctx: Ctx;
  open: boolean;
  settings: TripSettings | null;
  mod: TripModule | null;
  filterOn: boolean;
  onOpen: () => void;
  onFilter: (on: boolean) => void;
}) {
  const { t } = ctx;
  const has = !!mod && mod.hasTrip(settings);
  return (
    <div className="mb-3 flex flex-wrap items-center gap-3" data-testid="trip-bar">
      {has ? (
        <>
          <button
            type="button"
            onClick={onOpen}
            aria-expanded={open}
            className="inline-flex min-h-9 items-center gap-1 rounded-full border border-blue-800 bg-blue-50 px-3 text-sm font-medium text-blue-900 hover:bg-blue-100"
            data-testid="trip-chip"
          >
            {t("trip.chip", { km: settings!.roundTripKm! })} <span className="underline underline-offset-2">{t("trip.edit")}</span>
          </button>
          <span className="flex items-center gap-1">
            <label htmlFor="f-trip" className="flex items-center gap-2 text-sm font-medium">
              <input id="f-trip" type="checkbox" checked={filterOn} onChange={(e) => onFilter(e.target.checked)} className="h-4 w-4 accent-blue-800" />
              {t("trip.filter")}
            </label>
            <TermInfo term={ctx.tax.terms["trip-fit"]} base={ctx.base} text={ctx.termText} />
          </span>
        </>
      ) : (
        <button
          type="button"
          onClick={onOpen}
          aria-expanded={open}
          className="min-h-9 rounded-md border border-blue-800 px-3 text-sm font-semibold text-blue-900 hover:bg-blue-50"
          data-testid="trip-open"
        >
          {t("trip.open")}
        </button>
      )}
      {has ? null : <TermInfo term={ctx.tax.terms["trip-fit"]} base={ctx.base} text={ctx.termText} />}
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
      <TermInfo term={term} base={ctx.base} text={ctx.termText} />
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
        <TermInfo term={term} base={ctx.base} text={ctx.termText} />
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
      <TermInfo term={ctx.tax.terms[termId]} base={ctx.base} text={ctx.termText} />
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
    <InfoTip label={c.label} href={`${ctx.base}/learn/chemistry`} text={ctx.termText}>
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
              <NumberFilter id="seatsMin" termId="seats" label={t("filters.seats")} value={f.seatsMin} onChange={(v) => onChange({ seatsMin: v })} ctx={ctx} />
              <NumberFilter id="acMin" termId="ac-charging" label={t("filters.ac")} value={f.acMin} onChange={(v) => onChange({ acMin: v })} ctx={ctx} />
              <NumberFilter id="yearMin" termId="model-years" label={`${t("filters.years")}: ${t("hero.refine.yearFrom")}`} value={f.yearMin} onChange={(v) => onChange({ yearMin: v })} ctx={ctx} />
              <NumberFilter id="yearMax" termId="model-years" label={`${t("filters.years")}: ${t("hero.refine.yearTo")}`} value={f.yearMax} onChange={(v) => onChange({ yearMax: v })} ctx={ctx} />
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
      noteTerm={field === "real_range_km" && note ? "rung" : undefined}
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
  if (c.pay === "lease") return <Missing label={c.t("pay.lease.none")} />;
  // Loan: the monthly estimate from this price + the shown loan inputs; hover = the price's source.
  const monthly = c.pay === "loan" ? monthlyFor(amount, c.loan) : null;
  if (c.pay === "loan" && !monthly) return <Missing label={amount === null ? c.t("num.noData") : c.t("pay.needRate")} />;
  return (
    <Num
      value={amount}
      text={
        monthly
          ? `≈ ${c.t("pay.perMonth", { amount: formatMoney(monthly.monthly, currency, c.locale) })}`
          : amount !== null
            ? formatMoney(amount, currency, c.locale)
            : undefined
      }
      note={monthly ? c.t("pay.estimate") : undefined}
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
      <Link href={generationHref(c.base, r)} tabIndex={c.inTable ? -1 : undefined} className="underline decoration-slate-400 underline-offset-2 hover:text-blue-900">
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
  { id: "platform", key: null, label: "col.platform", term: "platform", levels: N, cell: (r) => r.platform_name ?? "—" },
  { id: "pack", key: null, label: "col.pack", term: "battery-pack", levels: N, cell: (r, c) => named(NO_NAMES, r.battery_pack_id, c) },
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
  const trip = ctx.trip;
  // "Sort by {col}" split around the column name, so the words work in any language's order.
  const [sortBefore = "", sortAfter = ""] = t("sort.by", { col: "\u0000" }).split("\u0000");
  return (
    <div className="relative max-h-[75vh] overflow-auto rounded-lg border border-slate-300" tabIndex={0} aria-labelledby="results-heading" data-testid="explore-scroll">
      <table className="w-max min-w-full border-collapse text-sm" data-testid="explore-table">
        <thead>
          <tr>
            {cols.map((col, i) => {
              const sorted = col.key && state.sort === col.key;
              const ariaSort = sorted ? (state.dir === "asc" ? "ascending" : "descending") : col.key ? "none" : undefined;
              // Price column follows the price mode (Decision 017).
              const payCol = col.id === "price" && ctx.pay !== "buy" ? ctx.pay : null;
              const term = payCol ? ctx.tax.terms[payCol] : col.term ? ctx.tax.terms[col.term] : undefined;
              const label = <TermLabel term={term} fallback={payCol ? t(`pay.col.${payCol}`) : t(col.label)} showTechnical={level !== "simple"} />;
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
                        // No aria-label: the accessible name must contain the visible label (WCAG 2.5.3,
                        // axe label-content-name-mismatch), so "Sort by" is sr-only text around it.
                        className="inline-flex min-h-6 items-end gap-1 rounded-sm text-left hover:underline"
                      >
                        {sortBefore.trim() ? <span className="sr-only">{sortBefore}</span> : null}
                        {label}
                        {sortAfter.trim() ? <span className="sr-only">{sortAfter}</span> : null}
                        <span aria-hidden="true" className="text-xs text-slate-600">
                          {sorted ? (state.dir === "asc" ? "▲" : "▼") : "↕"}
                        </span>
                      </button>
                    ) : (
                      label
                    )}
                    <TermInfo term={term} base={ctx.base} text={ctx.termText} />
                  </span>
                </th>
              );
            })}
            {trip ? (
              <th scope="col" className="sticky top-0 z-20 min-w-36 border-b border-slate-300 bg-slate-100 px-3 py-2 text-left align-bottom font-semibold" data-testid="trip-col">
                <span className="inline-flex items-end gap-1">
                  {t("trip.col")}
                  <TermInfo term={ctx.tax.terms["trip-fit"]} base={ctx.base} text={ctx.termText} />
                </span>
              </th>
            ) : null}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => {
            const fit = trip?.fits.get(r.variant_id);
            const grey = fit?.verdict === "fail";
            return (
            <tr
              key={r.variant_id}
              className={`border-b border-slate-200 last:border-0 hover:bg-slate-50 ${grey ? "text-slate-600 [&>td]:opacity-70" : ""}`}
              data-testid="explore-row"
              data-trip={fit?.verdict}
            >
              <th scope="row" className="sticky left-0 z-10 bg-white px-3 py-2 text-left font-medium">
                <div className="flex items-center gap-2">
                  <RowActions row={r} t={t} />
                  <span className="flex flex-col">
                    <Link href={variantHref(ctx.base, r)} className="inline-block min-h-6 whitespace-nowrap py-0.5 text-blue-800 underline underline-offset-2 hover:text-blue-950">
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
              {trip ? (
                <td className="px-3 py-2">
                  <trip.mod.TripCell fit={fit} ui={trip.ui} />
                </td>
              ) : null}
            </tr>
            );
          })}
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
        className="min-h-6 w-fit whitespace-nowrap rounded-sm text-left text-xs font-normal text-blue-800 underline decoration-dotted underline-offset-2"
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

/** Each row with whether it is the first of its generation in this order. */
function firstOfGeneration(rows: ExploreRow[]): [ExploreRow, boolean][] {
  const seen = new Set<string>();
  return rows.map((r) => {
    const first = !seen.has(r.generation_id);
    seen.add(r.generation_id);
    return [r, first];
  });
}

/** Sort menu (T-130): a native select, so it works with keyboard and screen readers on every phone. */
function SortMenu({ state, onChange, t }: { state: ExploreState; onChange: (k: SortKey) => void; t: T }) {
  const inMenu = (MENU_SORTS as readonly string[]).includes(state.sort ?? "");
  return (
    <div className="mb-3 flex items-center gap-2">
      <label htmlFor="sort-menu" className="text-sm text-slate-800">
        {t("sort.label")}
      </label>
      <select
        id="sort-menu"
        value={inMenu ? (state.sort as string) : ""}
        onChange={(e) => {
          const k = e.target.value;
          if ((MENU_SORTS as readonly string[]).includes(k)) onChange(k as SortKey);
        }}
        className="min-h-11 rounded-md border border-slate-500 bg-white px-3 py-2 text-sm font-semibold"
        data-testid="sort-menu"
      >
        {!inMenu ? <option value="">{t("sort.other")}</option> : null}
        {MENU_SORTS.map((k) => (
          <option key={k} value={k}>
            {t(`sort.${k}` as MsgKey)}
          </option>
        ))}
      </select>
    </div>
  );
}

function Card({ row: r, ctx: c, popTag = true }: { row: ExploreRow; ctx: Ctx; popTag?: boolean }) {
  const { t, level } = c;
  const item = (label: ReactNode, value: ReactNode) => (
    <div className="flex min-w-0 flex-col [overflow-wrap:anywhere]">
      <dt className="text-xs text-slate-700">{label}</dt>
      <dd>{value}</dd>
    </div>
  );
  // Label + glossary ⓘ (glossary sweep item 4); a missing term renders the plain label.
  const term = (id: string, fallback: MsgKey, suffix = "") => (
    <span className="inline-flex items-center gap-0.5">
      {(c.tax.terms[id]?.label ?? t(fallback)) + suffix}
      <TermInfo term={c.tax.terms[id]} base={c.base} text={c.termText} />
    </span>
  );
  const more = level !== "simple";
  return (
    <li
      className={`flex flex-col gap-3 rounded-lg border border-slate-300 bg-white p-4 ${c.trip?.fits.get(r.variant_id)?.verdict === "fail" ? "opacity-70" : ""}`}
      data-testid="explore-card"
      data-trip={c.trip?.fits.get(r.variant_id)?.verdict}
    >
      {popTag && r.pop_rank ? (
        <p className="w-fit rounded-full border border-slate-500 px-2 py-0.5 text-xs font-semibold" data-testid="popular-tag">
          {t("card.popular", { n: r.pop_rank })}
        </p>
      ) : null}
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-semibold">
            <Link href={variantHref(c.base, r)} className="text-blue-800 underline underline-offset-2 hover:text-blue-950">
              {r.make_name} {r.model_name}
            </Link>
          </h3>
          <p className="text-sm text-slate-700">
            {r.generation_name} · {r.variant_name} · {formatYears(r.year_start, r.year_end, t("years.now"))}
          </p>
        </div>
        <span className="inline-flex items-center gap-1">
          <QualityBadge tier={r.quality_tier} label={t(`tier.${r.quality_tier}`)} help={t(`tier.${r.quality_tier}.help`)} />
          <TermInfo term={c.tax.terms["quality-tier"]} base={c.base} text={c.termText} />
        </span>
      </div>
      {c.trip ? (
        <div className="text-sm">
          <span className="inline-flex items-center gap-0.5 text-xs text-slate-700">
            {t("trip.col")}
            <TermInfo term={c.tax.terms["trip-fit"]} base={c.base} text={c.termText} />
          </span>
          <c.trip.mod.TripCell fit={c.trip.fits.get(r.variant_id)} ui={c.trip.ui} inTable={false} />
        </div>
      ) : null}
      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        {item(term("real-range", "col.range"), num(r, c, r.real_range_km, "real_range_km", "km", 0, rangeNote(r, c)))}
        {item(term("dc-km-20min", "col.dc", ` (${t("col.dc20.unit")})`), num(r, c, r.dc_km_per_20min, "dc_km_per_20min", "km", 0))}
        {item(c.pay === "buy" ? term("new-price", "col.price") : term(c.pay, `pay.col.${c.pay}`), priceCell(r, c))}
        {item(term("used-price", "price.used"), <PriceBand currency={c.currency} locale={c.locale} notEnoughLabel={t("price.notEnough")} samplesLabel={t("price.samples")} />)}
        {more ? (
          <>
            {item(term("usable-vs-gross", "col.battery"), num(r, c, r.battery_kwh_net, "battery_kwh_net", "kWh"))}
            {item(term("dc-km-10min", "col.dc", ` (${t("col.dc.unit")})`), num(r, c, r.dc_km_per_10min, "dc_km_per_10min", "km", 0))}
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
            {item(term("platform", "col.platform"), r.platform_name ?? "—")}
            {item(term("battery-pack", "col.pack"), named(NO_NAMES, r.battery_pack_id, c))}
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
        {/* Name = the visible word + the car (WCAG 2.5.3 Label in Name; T-096). */}
        <span className="sr-only">: {name}</span>
      </button>
      {full ? (
        <span id={fullId} className="sr-only">
          {t("compare.full", { max: COMPARE_MAX })}
        </span>
      ) : null}
    </div>
  );
}
