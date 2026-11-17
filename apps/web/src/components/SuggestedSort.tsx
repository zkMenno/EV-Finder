"use client";
// Explore's "Suggested" order (T-067): the shortlist rules for the profile picked in the hero,
// with an ⓘ that says why the list is in this order (the heaviest factors and the rules that
// put a car last). Plain words come from the dictionaries; the numbers from the rules file.
import type { MsgKey, T } from "@/i18n/t";
import type { ResolvedProfile } from "@/lib/shortlist";
import { factorRows } from "@/lib/shortlist";
import { InfoTip, type TermText } from "./Term";

/** "Road-tripper · no charger at home · countryside" */
export function profileName(rp: ResolvedProfile, t: T): string {
  const parts = [t(`hero.profile.${rp.base.id}` as MsgKey)];
  if (rp.layer) parts.push(t(`hero.profile.${rp.layer.id}` as MsgKey).toLowerCase());
  if (rp.modifier) parts.push(t(`hero.profile.modifier.${rp.modifier.id}` as MsgKey));
  return parts.join(" · ");
}

/** The three heaviest factors after the layer's and modifier's weight steps (the release's combos). */
export function topFactors(rp: ResolvedProfile, n = 3): string[] {
  return factorRows(rp)
    .sort((a, b) => b.weight - a.weight)
    .slice(0, n)
    .map((f) => f.id);
}

export function SuggestedSort({
  rp,
  active,
  onToggle,
  t,
  termText,
  profileName,
  hasScores = true,
}: {
  rp: ResolvedProfile | null;
  active: boolean;
  onToggle: () => void;
  t: T;
  termText: TermText;
  profileName: string;
  /** False when the release has no shortlist scores: the order can't follow the profile yet. */
  hasScores?: boolean;
}) {
  if (!rp) {
    return active ? (
      <p className="mb-3 text-sm text-slate-700" data-testid="suggested-none">
        {t("suggested.needProfile")}
      </p>
    ) : null;
  }
  const label = t("suggested.label", { profile: profileName });
  return (
    <div className="mb-3 flex flex-wrap items-center gap-2" data-testid="suggested">
      <button
        type="button"
        aria-pressed={active}
        onClick={onToggle}
        className="inline-flex min-h-11 items-center rounded-md border border-slate-400 bg-white px-3 py-2 text-sm aria-pressed:border-blue-800 aria-pressed:bg-blue-100 aria-pressed:font-semibold"
        data-testid="suggested-toggle"
      >
        {label}
      </button>
      <InfoTip label={t("suggested.why")} text={termText}>
        <span className="block" data-testid="suggested-why">
          {t("suggested.weights", { list: topFactors(rp).map((id) => t(`hero.factor.${id}` as MsgKey)).join(", ") })}
        </span>
        {rp.base.gates.length ? (
          <span className="mt-1 block">
            {t("suggested.last")}{" "}
            {rp.base.gates.map((g) => t(`hero.gate.${g.id}` as MsgKey)).join(" ")}
          </span>
        ) : null}
        <span className="mt-1 block">{t("suggested.unknown")}</span>
        <span className="mt-1 block">{rp.base.calibrated ? t("hero.caveat.owner") : t("hero.caveat.research")}</span>
      </InfoTip>
      {active && !hasScores ? (
        <p className="w-full text-sm text-slate-700" data-testid="suggested-no-scores">
          {t("hero.noScores")}
        </p>
      ) : null}
    </div>
  );
}
