"use client";
// The landing-page hero (T-080, Decision 051): country → 4-tap profile picker → budget with a rough
// monthly estimate → optional refine → top 10, the first five marked "Your shortlist".
// The server renders the first result from the URL; the browser re-ranks on every change with the
// same pure functions (src/lib/shortlist.ts) once the compact catalogue has loaded. Scores come from
// the release's shortlist_scores.json (Decision 065); without it the hero says so and ranks nothing. All state is in
// the URL; the refine filters are Explore's filters, kept in step through src/lib/filter-bus.ts.
import { useEffect, useId, useMemo, useRef, useState, type ReactNode } from "react";
import type { Body, Country, Currency } from "@ev/schema";
import { COUNTRIES, COUNTRY_SLUGS, isServed, type CountrySlug, type Lang } from "@/config/countries";
import { makeT, type Dict, type MsgKey, type T } from "@/i18n/t";
import { loadClientCatalogue } from "@/lib/client-catalogue";
import { compareStore, COMPARE_MAX } from "@/lib/compare-store";
import type { ExploreRow } from "@/lib/explore-data";
import { onFilters, publishAnswers, publishFilters } from "@/lib/filter-bus";
import { effectiveLoan, monthlyFor, type FinanceProfileView } from "@/lib/finance";
import { formatMoney, formatNumber, formatYears, localeFor } from "@/lib/format";
import { nerdValue, numberParts } from "@/lib/nerd-value";
import { priceHowText } from "@/lib/price-how";
import { heroToSearchParams, mergeHeroIntoUrl, type HeroState } from "@/lib/hero-state";
import { buildListingUrl, type ListingSite } from "@/lib/listing-url";
import {
  AREAS,
  asksTrips,
  CHARGES,
  presetsFor,
  rankHero,
  SHORTLIST_N,
  reasons,
  resolveProfile,
  ROLES,
  TRIPS,
  type ActivePreset,
  type Answers,
  type Condition,
  type HeroPick,
  type HeroResult,
  type PresetField,
  type ResolvedProfile,
  type UsedBands,
} from "@/lib/shortlist";
import { BODIES, defaultFilters, type ExploreFilters } from "@/lib/state";
import type { UiTerm } from "@/lib/taxonomy";
import { useLevel } from "@/lib/use-level";
import { useListStore } from "@/lib/use-list-store";
import { generationHref } from "@/app/[country]/[lang]/ev/_lib/routes";
import { LoanBox, LoanWarning, useLoanSettings, type FinanceUi } from "./PriceMode";
import { profileName } from "./SuggestedSort";
import { TermInfo, type TermText } from "./Term";
import { ParallaxScene } from "@/components/parallax/ParallaxScene";
import { city as cityScene, village as villageScene } from "@/components/parallax/scenes.generated";

export interface HeroProps {
  country: CountrySlug;
  code: Country;
  currency: Currency;
  lang: Lang;
  dict: Dict;
  base: string;
  initial: HeroState;
  /** Ranked on the server from the URL; null when the picker isn't answered yet. */
  initialResult: HeroResult | null;
  /** The release has shortlist_scores.json (Decision 065). */
  hasScores: boolean;
  /** Release number (Nerd mode names where the scores come from). */
  release: number;
  /** Source id → name (Nerd mode: where a price comes from). */
  sources: Record<string, string>;
  dataUrl: string;
  total: number;
  finance: FinanceProfileView | null;
  usedBands: UsedBands;
  nowYear: number;
  makes: { id: string; name: string }[];
  /** This country's "See listings" sites, best first. */
  listingSites: ListingSite[];
  terms: Record<string, UiTerm | undefined>;
  /** Launch /learn guides that exist (winter range, charging in 2026, batteries). */
  learnLinks?: { slug: string; title: string; href: string }[];
}

const QUICK_BUDGETS: Record<Currency, number[]> = {
  EUR: [15000, 20000, 30000, 40000, 60000],
  GBP: [12000, 17000, 25000, 35000, 50000],
};

/** Preset field → the factor label that names it ("not known yet" lists). */
const PRESET_FACTOR: Partial<Record<PresetField, string>> = {
  dc_km_per_20min: "dc-speed",
  real_range_km: "winter-range",
  boot_l: "space",
  length_mm: "size",
  ac_kw: "ac-speed",
};

/** Score factors for parked features (bidirectional charging is parked, launch-scope.md): they still
 *  count in the release score, but the card never names them in its "not known yet" line (A-36). */
const PARKED_FACTORS: ReadonlySet<string> = new Set(["v2l", "home-power"]);

const chipCls =
  "inline-flex min-h-11 cursor-pointer items-center rounded-md border border-slate-400 bg-white px-3 py-2 text-sm " +
  "has-[:checked]:border-blue-800 has-[:checked]:bg-blue-100 has-[:checked]:font-semibold " +
  "has-[:focus-visible]:outline has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-[var(--focus)]";
const toggleCls =
  "inline-flex min-h-11 items-center rounded-md border border-slate-400 bg-white px-3 py-2 text-sm aria-pressed:border-blue-800 aria-pressed:bg-blue-100 aria-pressed:font-semibold";
const inputCls = "w-32 rounded-md border border-slate-400 bg-white px-3 py-2 text-base tabular-nums";

function cap(s: string): string {
  return s ? s[0]!.toUpperCase() + s.slice(1) : s;
}

function presetLabel(p: ActivePreset, t: T, locale: string): string {
  if (p.field === "length_mm" && p.max !== undefined) {
    return t("hero.preset.length_mm.max", { n: formatNumber(p.max / 1000, locale, 1) });
  }
  const n = formatNumber(p.min ?? p.max ?? 0, locale, 0);
  return t(`hero.preset.${p.field}.${p.min !== undefined ? "min" : "max"}` as MsgKey, { n });
}

// ── Home-hero scene (UX design v6): village, or city for city answers; day and night, layered ──

function Scene({ city }: { city: boolean }) {
  // Depth + parallax (Menno 2026-11-17): flat SVG first, drifting layers on top when motion is allowed.
  return (
    <div className="mx-auto w-full max-w-[14rem] md:max-w-[22rem]">
      <ParallaxScene scene={city ? cityScene : villageScene} testId="hero-scene" />
    </div>
  );
}

// ── Small building blocks ───────────────────────────────────────────────────────────────────

function Step({ n, title, children, t }: { n: number; title: string; children: ReactNode; t: T }) {
  const id = useId();
  return (
    <section aria-labelledby={id} className="border-t border-slate-200 pt-4">
      <h2 id={id} className="text-lg font-semibold">
        <span className="mr-2 text-sm font-normal text-slate-700">{t("hero.stepN", { n })}</span>
        {title}
      </h2>
      <div className="mt-3">{children}</div>
    </section>
  );
}

function Choice<V extends string>({
  name,
  legend,
  values,
  value,
  label,
  onChange,
  info,
}: {
  name: string;
  legend: string;
  /** ⓘ tooltip next to the question (glossary term). */
  info?: ReactNode;
  values: readonly V[];
  value: V | null;
  label: (v: V) => string;
  onChange: (v: V) => void;
}) {
  return (
    <fieldset className="mt-3">
      <legend className="text-sm font-semibold">
        {legend}
        {info ? <> {info}</> : null}
      </legend>
      <div className="mt-2 flex flex-wrap gap-2">
        {values.map((v) => (
          <label key={v} className={chipCls}>
            <input
              type="radio"
              name={name}
              value={v}
              checked={value === v}
              onChange={() => onChange(v)}
              className="sr-only"
              data-testid={`hero-${name}-${v}`}
            />
            {label(v)}
          </label>
        ))}
      </div>
    </fieldset>
  );
}

function NumberSelect({
  label,
  value,
  options,
  onChange,
  t,
  testid,
}: {
  label: string;
  value: number | null;
  options: number[];
  onChange: (v: number | null) => void;
  t: T;
  testid: string;
}) {
  const id = useId();
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-semibold">
        {label}
      </label>
      <select
        id={id}
        value={value === null ? "" : String(value)}
        onChange={(e) => onChange(e.target.value === "" ? null : Number(e.target.value))}
        className="mt-1 rounded-md border border-slate-400 bg-white px-3 py-2 text-base"
        data-testid={testid}
      >
        <option value="">{t("hero.refine.any")}</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </div>
  );
}

// ── The hero ────────────────────────────────────────────────────────────────────────────────

export function Hero(props: HeroProps) {
  const t = useMemo(() => makeT(props.dict), [props.dict]);
  const locale = localeFor(props.lang);
  const level = useLevel();
  const [hero, setHero] = useState<HeroState>(props.initial);
  const [rows, setRows] = useState<ExploreRow[] | null>(null);
  const [copied, setCopied] = useState(false);
  // The loan settings box renders only when opened (one LoanBox per page until then).
  const [loanOpen, setLoanOpen] = useState(false);
  const [dirty, setDirty] = useState(false);
  const lastUrl = useRef(heroToSearchParams(props.initial).toString());
  const [loanSettings, setLoanSettings] = useLoanSettings();
  const loan = useMemo(() => effectiveLoan(props.finance, loanSettings), [props.finance, loanSettings]);
  const money = (n: number) => formatMoney(n, props.currency, locale);
  const termText: TermText = { about: t("term.about"), learnMore: t("term.learnMore") };
  // ⓘ for a glossary id; renders nothing until the release has the term (T-100 ids).
  const tip = (id: string) => <TermInfo term={props.terms[id]} base={props.base} text={termText} />;

  useEffect(() => {
    let live = true;
    void loadClientCatalogue(props.dataUrl).then((c) => {
      if (live && c) setRows(c.rows);
    });
    return () => {
      live = false;
    };
  }, [props.dataUrl]);

  // Explore below changed a filter: take it over (same params, one URL).
  useEffect(() => onFilters("hero", (filters) => setHero((h) => ({ ...h, filters: { ...filters, tripFit: false } }))), []);

  // State → URL (replaceState: no round trip; the link stays shareable).
  useEffect(() => {
    const qs = heroToSearchParams(hero).toString();
    if (qs === lastUrl.current) return;
    lastUrl.current = qs;
    window.history.replaceState(null, "", mergeHeroIntoUrl(window.location.href, hero));
  }, [hero]);

  const update = (patch: Partial<HeroState>) => {
    setDirty(true);
    setCopied(false);
    setHero((h) => ({ ...h, ...patch }));
  };
  const setAnswers = (patch: Partial<Answers>) => {
    const answers = { ...hero.answers, ...patch };
    update({ answers, presetsOff: [] });
    publishAnswers(answers);
  };
  const setFilters = (filters: ExploreFilters) => {
    update({ filters });
    publishFilters({ filters, from: "hero" });
  };

  const rp = useMemo(() => resolveProfile(hero.answers), [hero.answers]);
  const presets = useMemo(() => (rp ? presetsFor(rp) : []), [rp]);
  const result: HeroResult | null = useMemo(() => {
    if (!rp) return null;
    if (!rows) return dirty ? null : props.initialResult;
    return rankHero(rows, rp, {
      country: props.code,
      cond: hero.cond,
      budget: hero.budget,
      filters: hero.filters,
      presetsOff: hero.presetsOff,
      usedBands: props.usedBands,
      nowYear: props.nowYear,
    }, { hasScores: props.hasScores });
  }, [rp, rows, dirty, hero, props.code, props.usedBands, props.nowYear, props.initialResult, props.hasScores]);

  const monthly = hero.budget !== null ? monthlyFor(hero.budget, loan) : null;
  const ui: FinanceUi = {
    t,
    locale,
    currency: props.currency,
    code: props.code,
    level,
    base: props.base,
    terms: props.terms,
    termText,
  };

  const countryHref = (slug: CountrySlug) => {
    const lang = isServed(slug, props.lang) ? props.lang : COUNTRIES[slug].defaultLang;
    const qs = heroToSearchParams(hero).toString();
    return `/${slug}/${lang}${qs ? `?${qs}` : ""}`;
  };

  const share = () => {
    void navigator.clipboard?.writeText(window.location.href).then(
      () => setCopied(true),
      () => setCopied(false),
    );
  };

  return (
    <div className="evs-tex evs-tex--map evs-tex--no-sun rounded-lg border border-slate-300 bg-white p-4 shadow-[var(--shadow-sticker)] sm:p-6" data-testid="hero">
      <div className="grid items-center gap-6 md:grid-cols-[minmax(0,1fr)_minmax(0,22rem)]">
        <div>
          <h1 className="font-[family-name:var(--font-display)] text-[2.375rem] font-extrabold leading-tight tracking-tight sm:text-[3.25rem]">{t("hero.title")}</h1>
          <p className="mt-3 max-w-2xl text-lg text-slate-800">{t("hero.intro")}</p>
        </div>
        <Scene city={hero.answers.area === "city"} />
      </div>

      <div className="mt-6 grid gap-6">
        <Step n={1} title={t("hero.step1")} t={t}>
          <ul className="flex flex-wrap gap-2" data-testid="hero-countries">
            {COUNTRY_SLUGS.map((slug) => (
              <li key={slug}>
                <a
                  href={countryHref(slug)}
                  aria-current={slug === props.country ? "true" : undefined}
                  className={`${toggleCls} aria-[current]:border-blue-800 aria-[current]:bg-blue-100 aria-[current]:font-semibold`}
                >
                  {COUNTRIES[slug].name}
                </a>
              </li>
            ))}
          </ul>
        </Step>

        <Step n={2} title={t("hero.step2")} t={t}>
          <Choice name="role" legend={t("hero.q.role")} values={ROLES} value={hero.answers.role} label={(v) => t(`hero.a.role.${v}` as MsgKey)} onChange={(role) => setAnswers({ role })} />
          {asksTrips(hero.answers) ? (
            <Choice name="trips" legend={t("hero.q.trips")} values={TRIPS} value={hero.answers.trips} label={(v) => t(`hero.a.trips.${v}` as MsgKey)} onChange={(trips) => setAnswers({ trips })} />
          ) : null}
          <Choice name="charge" legend={t("hero.q.charge")} values={CHARGES} value={hero.answers.charge} label={(v) => t(`hero.a.charge.${v}` as MsgKey)} onChange={(charge) => setAnswers({ charge })} />
          <Choice name="area" legend={t("hero.q.area")} values={AREAS} value={hero.answers.area} label={(v) => t(`hero.a.area.${v}` as MsgKey)} onChange={(area) => setAnswers({ area })} info={tip("home-area")} />
          {/* The ⓘ sits next to the label, not inside it (Term.tsx): inside, its text joins the checkbox's name. */}
          <div className="mt-3 flex items-center gap-1">
            <label className="inline-flex min-h-11 items-center gap-2 text-sm">
              <input type="checkbox" checked={hero.answers.keep8} onChange={(e) => setAnswers({ keep8: e.target.checked })} className="h-5 w-5" data-testid="hero-keep8" />
              {t("hero.keep8")}
            </label>
            {tip("keep-8-years")}
          </div>
          {/* The release scores have no keep-8-years combination yet (T-069 combos), so the box is
              remembered but can't change the order: say so rather than pretend (Decision 065). */}
          {hero.answers.keep8 ? <p className="text-xs text-slate-700" data-testid="hero-keep8-note">{t("hero.keep8.pending")}</p> : null}

          <div className="mt-3 rounded-md bg-slate-50 p-3" aria-live="polite" data-testid="hero-profile">
            {rp ? (
              <>
                <p className="text-sm">
                  <span className="text-slate-700">{t("hero.profile.label")}: </span>
                  <strong>{profileName(rp, t)}</strong> {tip(rp.base.id)}
                  {rp.layer ? tip(rp.layer.id) : null}
                </p>
                <p className="mt-1 text-sm text-slate-800">
                  {t(`hero.profile.${rp.base.id}.short` as MsgKey)}
                  {rp.layer ? ` ${t(`hero.profile.${rp.layer.id}.short` as MsgKey)}` : ""}
                </p>
                {presets.length ? (
                  <div className="mt-2">
                    <p className="text-xs font-semibold text-slate-700">{t("hero.presets.title")}</p>
                    <ul className="mt-1 flex flex-wrap gap-2" data-testid="hero-presets">
                      {presets
                        .filter((p) => !hero.presetsOff.includes(p.field))
                        .map((p) => {
                          const label = presetLabel(p, t, locale);
                          return (
                            <li key={p.field}>
                              <button
                                type="button"
                                onClick={() => update({ presetsOff: [...hero.presetsOff, p.field] })}
                                className="inline-flex min-h-11 items-center gap-2 rounded-md border border-slate-400 bg-white px-3 py-1 text-sm"
                                aria-label={t("hero.presets.remove", { label })}
                              >
                                {label}
                                <span aria-hidden="true">×</span>
                              </button>
                            </li>
                          );
                        })}
                    </ul>
                    {hero.presetsOff.length ? (
                      <button type="button" onClick={() => update({ presetsOff: [] })} className="mt-2 text-sm text-blue-800 underline underline-offset-2">
                        {t("hero.presets.restore")}
                      </button>
                    ) : null}
                  </div>
                ) : null}
              </>
            ) : (
              <p className="text-sm text-slate-700">{t("hero.profile.pickFirst")}</p>
            )}
          </div>
        </Step>

        <Step n={3} title={t("hero.step3")} t={t}>
          <BudgetField
            value={hero.budget}
            currency={props.currency}
            info={tip("budget")}
            t={t}
            money={money}
            onChange={(budget) => update({ budget })}
          />
          <div className="mt-2 text-sm" data-testid="hero-monthly">
            {hero.budget === null ? null : monthly ? (
              <>
                <p className="text-base font-semibold">
                  {t("hero.monthly", { amount: money(monthly.monthly) })}{" "}
                  <TermInfo term={props.terms.loan} base={props.base} text={termText} />
                </p>
                <p className="text-slate-700">
                  {t("hero.monthly.how", {
                    deposit: formatNumber(loan.depositPct, locale, 1),
                    term: loan.termMonths,
                    apr: formatNumber(loan.aprPct, locale, 2),
                  })}
                </p>
              </>
            ) : (
              <p className="text-slate-700">{t("hero.monthly.noRate")}</p>
            )}
            {hero.budget !== null ? <LoanWarning t={t} /> : null}
            <details className="mt-2" onToggle={(e) => setLoanOpen(e.currentTarget.open)}>
              <summary className="min-h-11 cursor-pointer py-2 text-blue-800 underline underline-offset-2">{t("hero.monthly.edit")}</summary>
              {loanOpen ? <LoanBox profile={props.finance} settings={loanSettings} onChange={setLoanSettings} ui={ui} price={hero.budget} /> : null}
            </details>
          </div>
          <Choice<Condition>
            name="cond"
            legend={t("hero.cond.label")}
            values={["any", "used", "new"]}
            value={hero.cond}
            label={(v) => t(`hero.cond.${v}` as MsgKey)}
            onChange={(cond) => update({ cond })}
          />
        </Step>

        <details className="border-t border-slate-200 pt-4" data-testid="hero-refine">
          <summary className="min-h-11 cursor-pointer py-2 text-lg font-semibold">{t("hero.step4")}</summary>
          <Refine filters={hero.filters} onChange={setFilters} makes={props.makes} nowYear={props.nowYear} t={t} />
        </details>
      </div>

      <Results
        result={result}
        rp={rp}
        hero={hero}
        props={props}
        t={t}
        locale={locale}
        level={level}
        money={money}
        loan={loan}
        presets={presets}
        onRemovePreset={(f) => update({ presetsOff: [...hero.presetsOff, f] })}
        share={share}
        copied={copied}
      />
    </div>
  );
}

function BudgetField({
  value,
  currency,
  info,
  t,
  money,
  onChange,
}: {
  value: number | null;
  currency: Currency;
  info?: ReactNode;
  t: T;
  money: (n: number) => string;
  onChange: (v: number | null) => void;
}) {
  const id = useId();
  const [text, setText] = useState(value === null ? "" : String(value));
  useEffect(() => {
    // Keep the field in step when a quick pick or the URL changes the budget.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setText((cur) => (Number(cur.replace(/[^\d]/g, "")) === value || (cur === "" && value === null) ? cur : value === null ? "" : String(value)));
  }, [value]);
  return (
    <div>
      <div className="flex items-center gap-1">
        <label htmlFor={id} className="text-sm font-semibold">
          {t("hero.budget.label")} ({currency})
        </label>
        {info}
      </div>
      <p id={`${id}-help`} className="text-sm text-slate-700">
        {t("hero.budget.help", { currency })}
      </p>
      <input
        id={id}
        inputMode="numeric"
        autoComplete="off"
        aria-describedby={`${id}-help`}
        value={text}
        onChange={(e) => {
          setText(e.target.value);
          const n = Number(e.target.value.replace(/[^\d]/g, ""));
          onChange(e.target.value.trim() === "" || !Number.isFinite(n) || n <= 0 ? null : n);
        }}
        className={`${inputCls} mt-1`}
        data-testid="hero-budget"
      />
      <div className="mt-2 flex flex-wrap gap-2" role="group" aria-label={t("hero.budget.quick")}>
        {QUICK_BUDGETS[currency].map((b) => (
          <button key={b} type="button" aria-pressed={value === b} onClick={() => onChange(b)} className={toggleCls} data-testid={`hero-budget-${b}`}>
            {money(b)}
          </button>
        ))}
        <button type="button" aria-pressed={value === null} onClick={() => onChange(null)} className={toggleCls}>
          {t("hero.budget.clear")}
        </button>
      </div>
    </div>
  );
}

function Refine({
  filters,
  onChange,
  makes,
  nowYear,
  t,
}: {
  filters: ExploreFilters;
  onChange: (f: ExploreFilters) => void;
  makes: { id: string; name: string }[];
  nowYear: number;
  t: T;
}) {
  const set = (patch: Partial<ExploreFilters>) => onChange({ ...filters, ...patch });
  const toggle = (list: string[], v: string) => (list.includes(v) ? list.filter((x) => x !== v) : [...list, v].sort());
  const years: number[] = [];
  for (let y = nowYear; y >= 2011; y--) years.push(y);
  const rangeId = useId();
  return (
    <div className="mt-3 grid gap-4">
      <fieldset>
        <legend className="text-sm font-semibold">{t("hero.refine.body")}</legend>
        <div className="mt-2 flex flex-wrap gap-2">
          {BODIES.map((b) => (
            <button
              key={b}
              type="button"
              aria-pressed={filters.bodies.includes(b)}
              onClick={() => set({ bodies: toggle(filters.bodies, b) as Body[] })}
              className={toggleCls}
            >
              {t(`body.${b}` as MsgKey)}
            </button>
          ))}
        </div>
      </fieldset>
      <div className="flex flex-wrap gap-4">
        <NumberSelect label={t("hero.refine.seats")} value={filters.seatsMin} options={[4, 5, 6, 7]} onChange={(seatsMin) => set({ seatsMin })} t={t} testid="hero-seats" />
        <NumberSelect label={t("hero.refine.towing")} value={filters.towingMin} options={[500, 750, 1000, 1500, 2000]} onChange={(towingMin) => set({ towingMin })} t={t} testid="hero-towing" />
        <NumberSelect label={t("hero.refine.ac")} value={filters.acMin} options={[7, 11, 22]} onChange={(acMin) => set({ acMin })} t={t} testid="hero-ac" />
        <div>
          <label htmlFor={rangeId} className="block text-sm font-semibold">
            {t("hero.refine.range")}
          </label>
          <input
            id={rangeId}
            inputMode="numeric"
            value={filters.rangeMin ?? ""}
            onChange={(e) => {
              const n = Number(e.target.value.replace(/[^\d]/g, ""));
              set({ rangeMin: e.target.value.trim() === "" || !n ? null : n });
            }}
            className={`${inputCls} mt-1`}
            data-testid="hero-range"
          />
        </div>
      </div>
      <fieldset>
        <legend className="text-sm font-semibold">{t("hero.refine.years")}</legend>
        <div className="mt-1 flex flex-wrap gap-4">
          <NumberSelect label={t("hero.refine.yearFrom")} value={filters.yearMin} options={years} onChange={(yearMin) => set({ yearMin })} t={t} testid="hero-ymin" />
          <NumberSelect label={t("hero.refine.yearTo")} value={filters.yearMax} options={years} onChange={(yearMax) => set({ yearMax })} t={t} testid="hero-ymax" />
        </div>
      </fieldset>
      {(
        [
          ["makes", "hero.refine.brands"],
          ["excludeMakes", "hero.refine.xbrands"],
        ] as const
      ).map(([key, label]) => (
        <details key={key}>
          <summary className="min-h-11 cursor-pointer py-2 text-sm font-semibold">
            {t(label)}
            {filters[key].length ? ` (${filters[key].length})` : ""}
          </summary>
          <div className="mt-2 flex flex-wrap gap-2">
            {makes.map((m) => (
              <button key={m.id} type="button" aria-pressed={filters[key].includes(m.id)} onClick={() => set({ [key]: toggle(filters[key], m.id) })} className={toggleCls}>
                {m.name}
              </button>
            ))}
          </div>
        </details>
      ))}
      <div className="flex flex-wrap items-center gap-4 text-sm">
        <button type="button" onClick={() => onChange({ ...defaultFilters(), voltageClasses: filters.voltageClasses, chemistries: filters.chemistries, coolings: filters.coolings })} className="text-blue-800 underline underline-offset-2">
          {t("hero.refine.reset")}
        </button>
        <a href="#explore" className="text-blue-800 underline underline-offset-2">
          {t("hero.refine.more")}
        </a>
      </div>
    </div>
  );
}

// ── Results ─────────────────────────────────────────────────────────────────────────────────

interface ResultsProps {
  result: HeroResult | null;
  rp: ResolvedProfile | null;
  hero: HeroState;
  props: HeroProps;
  t: T;
  locale: string;
  level: ReturnType<typeof useLevel>;
  money: (n: number) => string;
  loan: ReturnType<typeof effectiveLoan>;
  presets: ActivePreset[];
  onRemovePreset: (f: PresetField) => void;
  share: () => void;
  copied: boolean;
}

function Results(r: ResultsProps) {
  const { t, result, rp } = r;
  const id = useId();
  if (!rp) {
    return (
      <section aria-labelledby={id} className="mt-6 rounded-md bg-slate-50 p-4" data-testid="hero-results">
        <h2 id={id} className="sr-only">
          {t("hero.results.title", { n: 10 })}
        </h2>
        <p className="text-slate-800">{t("hero.results.pick")}</p>
      </section>
    );
  }
  // "Your shortlist" = priced cars only (Decision 064); more priced cars follow under "Also worth a
  // look"; cars with no price get their own section without place numbers, after every priced car.
  const top = result?.picks.slice(0, result.shortlistN) ?? [];
  const more = result?.picks.slice(result?.shortlistN ?? 0, result?.priced ?? 0) ?? [];
  const noPrice = result?.picks.slice(result?.priced ?? 0) ?? [];
  const activePresets = r.presets.filter((p) => !r.hero.presetsOff.includes(p.field));
  return (
    <section aria-labelledby={id} className="mt-8" data-testid="hero-results">
      {result?.status === "no-scores" ? (
        // No release scores: no count, no "top 0", just the plain reason (Decision 065).
        <>
          <h2 id={id} className="sr-only">
            {t("hero.results.title", { n: 10 })}
          </h2>
          <div className="mt-4 rounded-md border border-slate-300 p-4" role="status" data-testid="hero-no-scores">
            <p className="font-semibold">{t("hero.noScores")}</p>
            <p className="mt-1 text-sm text-slate-800">{t("hero.noScores.why")}</p>
          </div>
        </>
      ) : (
        <>
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 id={id} className="font-[family-name:var(--font-display)] text-2xl font-bold">
              {result && result.priced === 0 && result.picks.length > 0
                ? t("hero.results.titleUnpriced")
                : t("hero.results.title", { n: result ? Math.min(10, result.priced) : 10 })}
            </h2>
            <button type="button" onClick={r.share} className="min-h-11 text-sm text-blue-800 underline underline-offset-2">
              {r.copied ? t("hero.results.copied") : t("hero.results.share")}
            </button>
          </div>
          <p className="mt-1 text-sm text-slate-800" aria-live="polite" data-testid="hero-count">
            {result ? t("hero.results.count", { n: result.qualifying }) : t("hero.results.updating")}
          </p>
          <ul className="mt-2 grid gap-1 text-xs text-slate-700">
            <li>{rp.base.calibrated ? t("hero.caveat.owner") : t("hero.caveat.research")}</li>
            {/* With release scores the winter figures are the release's own estimates (Decision 065). */}
            <li>{result?.picks.some((p) => p.result.derived.winter_range_km !== undefined) ? t("hero.caveat.winterEstimate") : t("hero.caveat.winter")}</li>
            {result && result.unpriced > 0 ? <li data-testid="hero-unpriced">{t("hero.unpriced")}</li> : null}
          </ul>
        </>
      )}

      {result && result.status === "ranked" && result.picks.length === 0 ? (
        <div className="mt-4 rounded-md border border-slate-300 p-4" data-testid="hero-empty">
          <p>{t("hero.results.empty")}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {activePresets.map((p) => {
              const label = presetLabel(p, t, r.locale);
              return (
                <button key={p.field} type="button" onClick={() => r.onRemovePreset(p.field)} className={toggleCls}>
                  {t("hero.results.removePreset", { label })}
                </button>
              );
            })}
          </div>
        </div>
      ) : null}

      {result && result.status === "ranked" && result.picks.length > 0 && result.shortlistN === 0 ? (
        // Decision 064: unpriced cars never fill the shortlist, so say why it is empty.
        <p className="mt-4 rounded-md border border-slate-300 p-3 text-sm" data-testid="hero-no-priced">
          {t(r.hero.budget !== null ? "hero.results.noPriced" : "hero.results.noPricedAny")}
        </p>
      ) : null}
      {top.length ? (
        <div className="mt-4 rounded-lg bg-[var(--sunflower-tint)] p-3 sm:p-4" data-testid="hero-shortlist">
          <h3 className="text-lg font-semibold">
            {t("hero.results.shortlist")} <TermInfo term={r.props.terms.shortlist} base={r.props.base} text={{ about: t("term.about"), learnMore: t("term.learnMore") }} />
          </h3>
          <ol className="mt-3 grid gap-3">
            {top.map((p) => (
              <Card key={p.row.model_id} pick={p} r={r} />
            ))}
          </ol>
        </div>
      ) : null}
      {more.length ? (
        <div className="mt-6" data-testid="hero-more">
          <h3 className="text-lg font-semibold">{t("hero.results.more")}</h3>
          <ol className="mt-3 grid gap-3" start={top.length + 1}>
            {more.map((p) => (
              <Card key={p.row.model_id} pick={p} r={r} />
            ))}
          </ol>
        </div>
      ) : null}
      {noPrice.length ? (
        <div className="mt-6" data-testid="hero-no-price">
          {/* Fewer than five priced cars fit: say so plainly instead of ranking unpriced cars as picks. */}
          <h3 className="text-lg font-semibold">
            {t((result?.priced ?? 0) < SHORTLIST_N ? "hero.results.noPriceFits" : "hero.results.noPriceList")}
          </h3>
          <ul className="mt-3 grid gap-3">
            {noPrice.map((p) => (
              <Card key={p.row.model_id} pick={p} r={r} />
            ))}
          </ul>
        </div>
      ) : null}
      {r.props.learnLinks?.length ? (
        <nav aria-label={t("hero.learn.title")} className="mt-6 rounded-md bg-slate-50 p-3" data-testid="hero-learn">
          <p className="text-sm font-semibold">{t("hero.learn.title")}</p>
          <ul className="mt-1 grid gap-1 text-sm">
            {r.props.learnLinks.map((l) => (
              <li key={l.slug}>
                <a href={l.href} className="text-blue-800 underline underline-offset-2">
                  {l.title}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      ) : null}
      <p className="mt-6">
        <a href="#explore" className="font-semibold text-blue-800 underline underline-offset-2">
          {t("hero.explore", { n: r.props.total })}
        </a>
      </p>
    </section>
  );
}

function reasonText(pick: HeroPick, r: ResultsProps): string {
  const { t, locale } = r;
  const row = pick.row;
  const d = pick.result.derived;
  // Plus reasons from the release, with the values the release scored them on (winter range and
  // real efficiency are its own derived estimates, Decision 065).
  const bits = reasons(pick.result).map((x) => {
    switch (x.id) {
      case "dc-speed":
        return t("hero.why.dc-speed", { km: formatNumber(row.dc_km_per_20min, locale, 0) });
      case "winter-range":
        return d.winter_range_km !== undefined ? t("hero.why.winter-range.winter", { km: formatNumber(d.winter_range_km, locale, 0) }) : t("hero.factor.winter-range");
      case "space":
        return t("hero.why.space", { l: formatNumber(row.boot_l, locale, 0) });
      case "efficiency":
        return d.real_wh_km !== undefined ? t("hero.why.efficiency", { kwh: formatNumber(d.real_wh_km / 10, locale, 1) }) : t("hero.factor.efficiency");
      case "ac-speed":
        return t("hero.why.ac-speed", { kw: formatNumber(row.ac_kw, locale, 1) });
      case "size":
        return t("hero.why.size", { m: formatNumber((row.length_mm ?? 0) / 1000, locale, 2) });
      default:
        return t(`hero.why.${x.id}` as MsgKey);
    }
  });
  if (pick.result.adjustments.some((a) => a.id === "newest-version")) bits.push(t("hero.why.newest-version"));
  if (!bits.length) bits.push(t("hero.why.none"));
  if (r.hero.budget !== null && pick.price) {
    const head = r.hero.budget - pick.price.amount;
    if (head >= 500) bits.push(t("hero.card.underBudget", { amount: r.money(Math.floor(head / 500) * 500) }));
  }
  return cap(bits.join(", "));
}

function Card({ pick, r }: { pick: HeroPick; r: ResultsProps }) {
  const { t, locale, level, props } = r;
  const row = pick.row;
  const cmp = useListStore(compareStore);
  const inCmp = cmp.some((c) => c.id === row.variant_id);
  const full = !inCmp && cmp.length >= COMPARE_MAX;
  const name = `${row.make_name} ${row.model_name}`;
  const years = formatYears(pick.price?.yearFrom ?? row.year_start, pick.price ? pick.price.yearTo : row.year_end, t("years.now"));
  const site = props.listingSites[0];
  const monthly = pick.price ? monthlyFor(pick.price.amount, r.loan) : null;
  const unknownLabels = [
    ...pick.result.unknown,
    ...pick.presetUnknown.map((f) => PRESET_FACTOR[f]).filter((x): x is string => !!x),
  ]
    .filter((x, i, a) => a.indexOf(x) === i && !PARKED_FACTORS.has(x))
    .map((id) => t(`hero.factor.${id}` as MsgKey));

  let price: string;
  if (!pick.price) price = t("hero.card.priceUnknown");
  else if (pick.price.kind === "new") price = t("hero.card.priceNew", { amount: r.money(pick.price.amount) });
  else if (pick.price.low !== null && pick.price.high !== null)
    price = t("hero.card.priceUsed", { years, low: r.money(pick.price.low), high: r.money(pick.price.high), country: COUNTRIES[props.country].name });
  else price = t("hero.card.priceUsedOne", { years, amount: r.money(pick.price.amount), country: COUNTRIES[props.country].name });
  const priceNote =
    pick.price?.basis === "estimate"
      ? t(pick.price.lowConfidence ? "hero.card.estimateLow" : "hero.card.estimate")
      : pick.price?.basis === "band" && pick.price.scope === "generation"
        ? t("hero.card.generationBand")
        : null;
  const priceHow = level === "nerd" && pick.price ? priceHowText(pick.price, t, locale, r.money, props.sources) : null;

  return (
    <li className="min-w-0 rounded-lg border border-slate-300 bg-white p-3 sm:p-4" data-testid="hero-card" data-rank={pick.rank ?? undefined} data-variant={row.variant_id} data-price={pick.price?.amount} data-price-basis={pick.price?.basis ?? "none"}>
      <div className="flex items-start gap-3">
        {/* A car with no price has no place number (Decision 064): it is not a ranked pick. */}
        {pick.rank !== null ? (
          <span className="mt-0.5 inline-flex h-8 min-w-8 items-center justify-center rounded-full bg-[var(--ink)] px-2 text-sm font-bold text-[var(--surface)]" aria-label={t("hero.card.rank", { n: pick.rank })}>
            {pick.rank}
          </span>
        ) : null}
        <div className="min-w-0 flex-1">
          <h4 className="text-base font-semibold">
            <a href={generationHref(props.base, row)} className="text-blue-800 underline-offset-2 hover:underline">
              {name}
            </a>
          </h4>
          <p className="text-sm text-slate-700">
            {row.variant_name} · {formatYears(row.year_start, row.year_end, t("years.now"))}
          </p>
          <p className="mt-2 text-sm" data-testid="hero-why">
            {reasonText(pick, r)}
          </p>
          <dl className="mt-2 grid grid-cols-1 gap-x-4 gap-y-1 text-sm sm:grid-cols-3">
            <div>
              <dt className="text-slate-700">
                {t("hero.card.realRange")} <TermInfo term={props.terms["real-range"]} base={props.base} text={{ about: t("term.about"), learnMore: t("term.learnMore") }} />
              </dt>
              <dd className="font-semibold tabular-nums">{row.real_range_km ? `${formatNumber(row.real_range_km, locale, 0)} km` : t("hero.card.notKnown")}</dd>
            </div>
            <div>
              <dt className="text-slate-700">
                {t("hero.card.winter")} <TermInfo term={props.terms["real-winter-range"]} base={props.base} text={{ about: t("term.about"), learnMore: t("term.learnMore") }} />
              </dt>
              <dd className={pick.result.derived.winter_range_km !== undefined ? "font-semibold tabular-nums" : "text-slate-800"} data-testid="hero-winter">
                {pick.result.derived.winter_range_km !== undefined ? (
                  <>
                    {`${formatNumber(pick.result.derived.winter_range_km, locale, 0)} km`}
                    <span className="block text-xs font-normal text-slate-700">{t("hero.card.winterEstimate")}</span>
                  </>
                ) : (
                  t("hero.card.notKnown")
                )}
              </dd>
            </div>
            <div>
              <dt className="text-slate-700">{t("hero.card.price")}</dt>
              <dd className="font-semibold" data-testid="hero-price">
                {price}
                {priceNote ? <span className="block text-xs font-normal text-slate-700" data-testid="hero-price-note">{priceNote}</span> : null}
                {priceHow ? <span className="block text-xs font-normal text-slate-700" data-testid="hero-price-how">{priceHow}</span> : null}
                {monthly ? <span className="block text-sm font-normal text-slate-800">{t("hero.monthly", { amount: r.money(monthly.monthly) })}</span> : null}
              </dd>
            </div>
          </dl>
          {level !== "simple" && unknownLabels.length ? <p className="mt-2 text-xs text-slate-700">{t("hero.card.unknown", { list: unknownLabels.join(", ") })}</p> : null}
          {level !== "simple" && pick.alternatives > 0 ? <p className="mt-1 text-xs text-slate-700">{t("hero.card.alternatives", { n: pick.alternatives })}</p> : null}
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              aria-pressed={inCmp}
              aria-disabled={full || undefined}
              onClick={() => {
                if (inCmp) compareStore.remove(row.variant_id);
                else if (!full) compareStore.add({ id: row.variant_id, label: `${name} ${row.variant_name}` });
              }}
              className={toggleCls}
              data-testid="hero-compare"
            >
              {/* Name = the visible words + the car (WCAG 2.5.3 Label in Name: voice users say what they see). */}
              {inCmp ? t("hero.card.inCompare") : full ? t("hero.card.compareFull") : t("hero.card.compare")}
              <span className="sr-only">: {`${name} ${row.variant_name}`}</span>
            </button>
            {site ? (
              <a
                href={buildListingUrl(site, row.make_name, row.model_name)}
                rel="nofollow noopener"
                target="_blank"
                className="inline-flex min-h-11 items-center gap-1 rounded-md border border-blue-800 px-3 py-2 text-sm font-semibold text-blue-900 hover:bg-blue-50"
                data-testid="hero-listings"
              >
                {t("hero.card.listings", { site: site.label })}
                <span aria-hidden="true">↗</span>
                <span className="sr-only"> {t("hero.card.newTab")}</span>
              </a>
            ) : null}
          </div>
        </div>
      </div>
      {/* Full card width (not beside the rank badge): the score table needs the room on a phone. */}
      {level === "nerd" ? <NerdScore pick={pick} r={r} /> : null}
    </li>
  );
}

function NerdScore({ pick, r }: { pick: HeroPick; r: ResultsProps }) {
  const { t, locale } = r;
  const res = pick.result;
  return (
    <div className="mt-2 rounded border border-slate-300 bg-slate-50 p-2 text-xs" data-testid="hero-nerd">
      <p className="font-semibold">
        {t("hero.card.score", { score: formatNumber(res.score, locale, 1), band: t(`hero.band.${res.band}` as MsgKey) })}
      </p>
      {/* Numbers never break mid-value; only factor names wrap. If a language still needs more room,
          the table scrolls inside the card instead of widening the page (verify-web, 360 px). */}
      <div className="mt-1 overflow-x-auto">
      <table className="w-full text-left [&_td]:pr-2 [&_th]:pr-2">
        <caption className="sr-only">{t("hero.nerd.factors")}</caption>
        <thead>
          <tr>
            <th scope="col">{t("hero.nerd.factor")}</th>
            <th scope="col">{t("hero.nerd.value")}</th>
            {/* One column for points × weight: two narrow numeric columns cost ~45 px a 360 px card
                doesn't have (T-097 review: headers broke mid-word, "Poi/ds"). */}
            <th scope="col">
              {t("hero.nerd.points")} × {t("hero.nerd.weight")}
            </th>
          </tr>
        </thead>
        <tbody>
          {res.factors.map((f) => (
            <tr key={f.id}>
              <th scope="row" className="font-normal hyphens-auto [overflow-wrap:anywhere]">
                {t(`hero.factor.${f.id}` as MsgKey)}
              </th>
              {/* The car's own figure with its unit (T-097), not the scaled scoring value. May wrap at
                  the spaces of the unit ("387 km in 20 min") on a phone; the number itself never splits
                  (no spaces inside formatted numbers; FR uses a no-break space). Units and words stay short and
                  breakable so the table fits a 360 px card in every language (axe: no scroll region). Headers
                  and words may break mid-word when a wider system font needs it (CI DE was 16 px over);
                  numbers sit in nowrap spans so they never split. */}
              <td className="tabular-nums hyphens-auto [overflow-wrap:anywhere]" data-testid={`hero-nerd-value-${f.id}`}>
                {numberParts(nerdValue(f, t, locale)).map((p, i) =>
                  p.num ? <span key={i} className="whitespace-nowrap">{p.text}</span> : p.text,
                )}
              </td>
              <td className="whitespace-nowrap tabular-nums" data-testid={`hero-nerd-points-${f.id}`}>
                {formatNumber(f.score ?? 0.5, locale, 2)} × {formatNumber(f.weight, locale, 1)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
      {res.adjustments.length ? (
        <p className="mt-1">{t("hero.nerd.adjust", { list: res.adjustments.map((a) => `${t(`hero.adj.${a.id}` as MsgKey)} ${a.points > 0 ? "+" : ""}${a.points}`).join(", ") })}</p>
      ) : null}
      <p className="mt-1">{t("hero.nerd.rules")}</p>
      <p className="mt-1" data-testid="hero-nerd-source">{t("hero.nerd.source", { n: r.props.release })}</p>
    </div>
  );
}
