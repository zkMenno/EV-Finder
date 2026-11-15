"use client";
// Price modes (Decision 017, T-043): the mode control, the loan settings + calculator, and the
// lease placeholder. Shared by Explore, the variant page and Compare. Every amount is an
// estimate from the inputs shown next to it; Nerd level shows the formula and the APR source.
import type { Country, Currency } from "@ev/schema";
import { useEffect, useId, useMemo, useState } from "react";
import { TermInfo, type TermText } from "@/components/Term";
import type { Lang } from "@/config/countries";
import { makeT, type Dict, type MsgKey, type T } from "@/i18n/t";
import {
  effectiveLoan,
  financeLinksAllowed,
  isPayMode,
  monthlyFor,
  PAY_MODES,
  readLoanSettings,
  readPayMode,
  TERM_CHOICES,
  writeLoanSettings,
  writePayMode,
  type EffectiveLoan,
  type FinanceProfileView,
  type InputOrigin,
  type LoanSettings,
  type PayMode,
} from "@/lib/finance";
import { formatMoney, formatNumber, localeFor } from "@/lib/format";
import type { Level } from "@/lib/state";
import type { UiTerm } from "@/lib/taxonomy";

export interface FinanceUi {
  t: T;
  locale: string;
  currency: Currency;
  code: Country;
  level: Level;
  base: string;
  terms: Record<string, UiTerm | undefined>;
  termText: TermText;
}

export function PayModeToggle({
  value,
  onChange,
  ui,
}: {
  value: PayMode;
  onChange: (m: PayMode) => void;
  ui: FinanceUi;
}) {
  const { t } = ui;
  return (
    <div className="flex flex-wrap items-center gap-1" data-testid="pay-mode">
      <div
        role="group"
        aria-label={t("pay.label")}
        className="inline-flex rounded-md border border-slate-400 p-0.5"
      >
        {PAY_MODES.map((m) => (
          <button
            key={m}
            type="button"
            aria-pressed={value === m}
            onClick={() => onChange(m)}
            className={`rounded px-3 py-1 text-sm ${value === m ? "bg-slate-900 text-white" : "text-slate-900 hover:bg-slate-100"}`}
          >
            {t(`pay.${m}`)}
          </button>
        ))}
      </div>
      <TermInfo
        term={ui.terms[value === "lease" ? "lease" : "loan"]}
        base={ui.base}
        text={ui.termText}
      />
    </div>
  );
}

const ORIGIN_KEY: Record<InputOrigin, MsgKey> = {
  user: "loan.from.user",
  profile: "loan.from.profile",
  assumption: "loan.from.assumption",
  missing: "loan.from.missing",
};

function Origin({ o, t }: { o: InputOrigin; t: T }) {
  return (
    <span className={`text-xs ${o === "missing" ? "text-amber-900" : "text-slate-700"}`}>
      ({t(ORIGIN_KEY[o])})
    </span>
  );
}

/** The CCD2 warning (Directive (EU) 2023/2225) + "estimate, not an offer". Always shown with figures. */
export function LoanWarning({ t }: { t: T }) {
  return (
    <div className="mt-3 border-t border-slate-200 pt-2 text-sm" data-testid="loan-warning">
      <p className="font-semibold">{t("loan.warning")}</p>
      <p className="text-slate-800">{t("loan.notOffer")}</p>
    </div>
  );
}

/** Nerd level: the formula and where the APR comes from. */
function LoanNerd({
  profile,
  e,
  ui,
}: {
  profile: FinanceProfileView | null;
  e: EffectiveLoan;
  ui: FinanceUi;
}) {
  const { t } = ui;
  if (ui.level !== "nerd") return null;
  return (
    <div
      className="mt-2 rounded border border-slate-300 bg-slate-50 p-2 text-xs"
      data-testid="loan-nerd"
    >
      <p className="font-mono">{t("loan.formula")}</p>
      {e.aprPct !== null ? (
        <p className="mt-1 font-mono">
          r = {formatNumber((Math.pow(1 + e.aprPct / 100, 1 / 12) - 1) * 100, "en-GB", 4)} % / month
        </p>
      ) : null}
      {profile?.typical_apr != null && profile.source ? (
        <p className="mt-1">
          {t("loan.aprSource", {
            rate: formatNumber(profile.typical_apr, ui.locale, 2),
            source: profile.source.series_id
              ? `${profile.source.name} (${profile.source.series_id})`
              : profile.source.name,
            period: profile.source.period ?? "—",
            date: profile.retrieved_at ?? "—",
          })}{" "}
          <a
            href={profile.source.url}
            rel="noopener nofollow"
            target="_blank"
            className="break-all text-blue-800 underline underline-offset-2"
          >
            {profile.source.url}
          </a>{" "}
          {t("loan.aprScope")} {profile.review ? t("loan.aprReview") : null}
        </p>
      ) : null}
    </div>
  );
}

/**
 * Loan inputs (APR, term, deposit) with their origin labels, and — when `price` is given — the
 * monthly amount, the total over the term and the cost of the loan.
 */
export function LoanBox({
  profile,
  settings,
  onChange,
  ui,
  price,
}: {
  profile: FinanceProfileView | null;
  settings: LoanSettings;
  onChange: (s: LoanSettings) => void;
  ui: FinanceUi;
  /** The car's price; undefined = settings only (Explore), null = this car has no price. */
  price?: number | null;
}) {
  const { t } = ui;
  const id = useId();
  const e = effectiveLoan(profile, settings);
  const result = typeof price === "number" ? monthlyFor(price, e) : null;
  const money = (n: number) => formatMoney(n, ui.currency, ui.locale);
  const num = (v: string): number | null => {
    if (v.trim() === "") return null;
    const n = Number(v.replace(",", "."));
    return Number.isFinite(n) && n >= 0 && n <= 100 ? n : null;
  };
  const inputCls = "w-24 rounded-md border border-slate-400 px-2 py-1 text-sm tabular-nums";

  return (
    <section
      aria-labelledby={`${id}-h`}
      className="rounded-md border border-slate-300 p-3"
      data-testid="loan-box"
    >
      <h3 id={`${id}-h`} className="flex items-center gap-1 font-semibold">
        {t("loan.title")}
        <TermInfo term={ui.terms.loan} base={ui.base} text={ui.termText} />
        <span className="ml-1 rounded border border-slate-500 px-1 text-xs font-normal">
          {t("pay.estimate")}
        </span>
      </h3>
      <div className="mt-2 grid gap-3 sm:grid-cols-3">
        <div className="flex flex-col gap-1 text-sm">
          <label htmlFor={`${id}-apr`} className="font-medium">
            {t("loan.apr")}
          </label>
          <TermInfo term={ui.terms["apr"]} base={ui.base} text={ui.termText} />
          <input
            id={`${id}-apr`}
            inputMode="decimal"
            className={inputCls}
            data-testid="loan-apr"
            // No rate without a source: the field stays empty and asks (NL today).
            placeholder={e.aprPct === null ? t("pay.needRate") : undefined}
            defaultValue={e.aprPct === null ? "" : String(e.aprPct)}
            key={`apr-${e.aprPct ?? "none"}-${e.origin.apr}`}
            onBlur={(ev) => onChange({ ...settings, aprPct: num(ev.target.value) })}
            onKeyDown={(ev) => {
              if (ev.key === "Enter")
                onChange({ ...settings, aprPct: num((ev.target as HTMLInputElement).value) });
            }}
          />
          <Origin o={e.origin.apr} t={t} />
        </div>
        <div className="flex flex-col gap-1 text-sm">
          <label htmlFor={`${id}-term`} className="font-medium">
            {t("loan.term")}
          </label>
          <TermInfo term={ui.terms["loan-term"]} base={ui.base} text={ui.termText} />
          <select
            id={`${id}-term`}
            className="w-32 rounded-md border border-slate-400 bg-white px-2 py-1 text-sm"
            value={e.termMonths}
            data-testid="loan-term"
            onChange={(ev) => onChange({ ...settings, termMonths: Number(ev.target.value) })}
          >
            {[...new Set([...TERM_CHOICES, e.termMonths])]
              .sort((a, b) => a - b)
              .map((n) => (
                <option key={n} value={n}>
                  {t("loan.termMonths", { n })}
                </option>
              ))}
          </select>
          <Origin o={e.origin.term} t={t} />
        </div>
        <div className="flex flex-col gap-1 text-sm">
          <label htmlFor={`${id}-dep`} className="font-medium">
            {t("loan.deposit")}
          </label>
          <TermInfo term={ui.terms["deposit"]} base={ui.base} text={ui.termText} />
          <input
            id={`${id}-dep`}
            inputMode="decimal"
            className={inputCls}
            data-testid="loan-deposit"
            defaultValue={String(e.depositPct)}
            key={`dep-${e.depositPct}`}
            onBlur={(ev) => onChange({ ...settings, depositPct: num(ev.target.value) })}
          />
          <Origin o={e.origin.deposit} t={t} />
        </div>
      </div>

      {price === null ? <p className="mt-3 text-sm text-slate-800">{t("loan.noPrice")}</p> : null}
      {typeof price === "number" && result ? (
        <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-3" data-testid="loan-result">
          <div>
            <dt className="text-slate-700">{t("loan.monthly")}</dt>
            <dd className="text-lg font-semibold tabular-nums" data-testid="loan-monthly">
              ≈ {money(result.monthly)}
            </dd>
          </div>
          <div>
            <dt className="flex items-center gap-1 text-slate-700">
              {t("loan.total")}
              <TermInfo term={ui.terms["total-cost-over-term"]} base={ui.base} text={ui.termText} />
            </dt>
            <dd className="tabular-nums" data-testid="loan-total">
              ≈ {money(result.totalOverTerm)}{" "}
              <span className="text-xs text-slate-700">({t("loan.totalHelp")})</span>
            </dd>
          </div>
          <div>
            <dt className="text-slate-700">{t("loan.cost")}</dt>
            <dd className="tabular-nums">≈ {money(result.costOfCredit)}</dd>
          </div>
        </dl>
      ) : null}

      <p className="mt-3 text-xs text-slate-800" data-testid="loan-assumptions">
        <span className="font-medium">{t("loan.assumptions")}:</span>{" "}
        {typeof price === "number" ? `${t("loan.price")} ${money(price)} · ` : null}
        {t("loan.apr")} {e.aprPct === null ? "—" : `${formatNumber(e.aprPct, ui.locale, 2)} %`} ·{" "}
        {t("loan.termMonths", { n: e.termMonths })} · {t("loan.deposit")}{" "}
        {formatNumber(e.depositPct, ui.locale, 1)} %
      </p>
      {!financeLinksAllowed(ui.code) ? (
        <p className="mt-1 text-xs text-slate-800">{t("finance.uk")}</p>
      ) : null}
      <LoanNerd profile={profile} e={e} ui={ui} />
      <LoanWarning t={t} />
      {settings.aprPct !== null || settings.termMonths !== null || settings.depositPct !== null ? (
        <button
          type="button"
          className="mt-2 text-xs text-blue-800 underline underline-offset-2"
          onClick={() => onChange({ aprPct: null, termMonths: null, depositPct: null })}
        >
          {t("loan.reset")}
        </button>
      ) : null}
    </section>
  );
}

/** Lease mode: a labelled placeholder, never a figure (Decision 017). UK: no lease links at all. */
export function LeaseNotice({ ui }: { ui: FinanceUi }) {
  const { t } = ui;
  if (!financeLinksAllowed(ui.code)) {
    return (
      <p className="rounded-md border border-slate-300 p-3 text-sm" data-testid="lease-notice">
        {t("lease.uk")}
      </p>
    );
  }
  return (
    <p
      className="flex flex-wrap items-center gap-1 rounded-md border border-slate-300 p-3 text-sm"
      data-testid="lease-notice"
    >
      <span
        className="font-medium text-slate-700 underline decoration-dotted underline-offset-2"
        aria-disabled="true"
        data-testid="lease-link-placeholder"
      >
        {t("lease.placeholder")}
      </span>
      <TermInfo term={ui.terms.lease} base={ui.base} text={ui.termText} />
      <TermInfo term={ui.terms["private-lease"]} base={ui.base} text={ui.termText} />
      <TermInfo term={ui.terms["residual-value"]} base={ui.base} text={ui.termText} />
      <TermInfo term={ui.terms["balloon-pcp"]} base={ui.base} text={ui.termText} />
      <span className="text-slate-800">— {t("lease.soon")}</span>
    </p>
  );
}

/** Price cell text for a mode: buy = price, loan = "≈ €x/month", lease = no figure. */
export function payCellText(
  mode: PayMode,
  price: number | null,
  e: EffectiveLoan,
  ui: Pick<FinanceUi, "t" | "currency" | "locale">,
): string | null {
  if (mode === "buy") return price === null ? null : formatMoney(price, ui.currency, ui.locale);
  if (mode === "lease") return null;
  const r = monthlyFor(price, e);
  return r
    ? `≈ ${ui.t("pay.perMonth", { amount: formatMoney(r.monthly, ui.currency, ui.locale) })}`
    : null;
}

/**
 * Mode + loan settings for a page without Explore's state (variant, compare): `?pay=` wins, else
 * the remembered mode; changes go to localStorage and the URL (replaceState).
 */
export function usePayMode(initial: PayMode = "buy"): [PayMode, (m: PayMode) => void] {
  const [mode, setMode] = useState<PayMode>(initial);
  useEffect(() => {
    const fromUrl = new URLSearchParams(window.location.search).get("pay");
    const next = isPayMode(fromUrl) ? fromUrl : readPayMode();
    // Browser-only state after hydration (URL of a static page, localStorage).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (next && next !== initial) setMode(next);
  }, [initial]);
  const set = (m: PayMode) => {
    setMode(m);
    writePayMode(m);
    const url = new URL(window.location.href);
    if (m === "buy") url.searchParams.delete("pay");
    else url.searchParams.set("pay", m);
    window.history.replaceState(null, "", url.pathname + url.search + url.hash);
  };
  return [mode, set];
}

export function useLoanSettings(): [LoanSettings, (s: LoanSettings) => void] {
  const [s, setS] = useState<LoanSettings>({ aprPct: null, termMonths: null, depositPct: null });
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setS(readLoanSettings());
  }, []);
  return [
    s,
    (next) => {
      setS(next);
      writeLoanSettings(next);
    },
  ];
}

/** Variant and compare pages: mode control + calculator (one car) or a per-car monthly list. */
export function PricePanel({
  cars,
  profile,
  currency,
  code,
  lang,
  dict,
  base,
  terms,
  level = "detailed",
}: {
  cars: { id: string; label: string; price: number | null }[];
  profile: FinanceProfileView | null;
  currency: Currency;
  code: Country;
  lang: Lang;
  dict: Dict;
  base: string;
  terms: Record<string, UiTerm | undefined>;
  level?: Level;
}) {
  const t = useMemo(() => makeT(dict), [dict]);
  const [mode, setMode] = usePayMode();
  const [settings, setSettings] = useLoanSettings();
  const [lvl, setLvl] = useState<Level>(level);
  useEffect(() => {
    const l = new URLSearchParams(window.location.search).get("level");
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (l === "nerd" || l === "simple" || l === "detailed") setLvl(l);
  }, []);
  const ui: FinanceUi = {
    t,
    locale: localeFor(lang),
    currency,
    code,
    level: lvl,
    base,
    terms,
    termText: { about: t("term.about"), learnMore: t("term.learnMore") },
  };
  const e = effectiveLoan(profile, settings);
  const one = cars.length === 1 ? cars[0]! : null;

  return (
    <section
      aria-label={t("pay.label")}
      className="mt-6 flex max-w-3xl flex-col gap-3 print:hidden"
      data-testid="price-panel"
    >
      <PayModeToggle value={mode} onChange={setMode} ui={ui} />
      {mode === "loan" ? (
        <>
          <LoanBox
            profile={profile}
            settings={settings}
            onChange={setSettings}
            ui={ui}
            price={one ? one.price : undefined}
          />
          {!one ? (
            <div>
              <h3 className="text-sm font-semibold">{t("loan.perCar")}</h3>
              <ul className="mt-1 text-sm" data-testid="loan-per-car">
                {cars.map((c) => {
                  const r = monthlyFor(c.price, e);
                  return (
                    <li key={c.id} className="tabular-nums">
                      {c.label}:{" "}
                      {r
                        ? `≈ ${t("pay.perMonth", { amount: formatMoney(r.monthly, currency, ui.locale) })}`
                        : "—"}
                    </li>
                  );
                })}
              </ul>
            </div>
          ) : null}
        </>
      ) : null}
      {mode === "lease" ? <LeaseNotice ui={ui} /> : null}
    </section>
  );
}
