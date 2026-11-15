"use client";
// Explore's "Suggested" order (T-067): the shortlist rules for the profile picked in the hero,
// with an ⓘ that says why the list is in this order (the heaviest factors and the rules that
// put a car last). Plain words come from the dictionaries; the numbers from the rules file.
import type { MsgKey, T } from "@/i18n/t";
import type { ResolvedProfile } from "@/lib/shortlist";
import { RULES } from "@/lib/shortlist";
import { InfoTip, type TermText } from "./Term";

/** "Road-tripper · no charger at home · countryside" */
export function profileName(rp: ResolvedProfile, t: T): string {
  const parts = [t(`hero.profile.${rp.base.id}` as MsgKey)];
  if (rp.layer) parts.push(t(`hero.profile.${rp.layer.id}` as MsgKey).toLowerCase());
  if (rp.modifier) parts.push(t(`hero.profile.modifier.${rp.modifier.id}` as MsgKey));
  return parts.join(" · ");
}

/** The three heaviest factors after the profile's weight steps. */
export function topFactors(rp: ResolvedProfile, n = 3): string[] {
  const steps: Record<string, number> = {};
  for (const src of [rp.layer?.weight_steps, rp.modifier?.weight_steps, ...rp.addons.map((a) => a.weight_steps)]) {
    for (const [k, v] of Object.entries(src ?? {})) steps[k] = (steps[k] ?? 0) + v;
  }
  return [...rp.base.factors, ...(rp.layer?.extra_factors ?? [])]
    .filter((f) => f.kind !== "unknown")
    .map((f) => ({ id: f.id, w: f.weight * Math.pow(RULES.weight_step_factor, steps[f.id] ?? 0) }))
    .sort((a, b) => b.w - a.w)
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
}: {
  rp: ResolvedProfile | null;
  active: boolean;
  onToggle: () => void;
  t: T;
  termText: TermText;
  profileName: string;
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
    </div>
  );
}
