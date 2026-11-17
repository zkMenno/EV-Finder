// "Owner's note" on model and generation pages (T-067, Decision 038): Menno's own verdict and
// note for a generation, from data/editorial/menno-picks.yaml via scripts/owner-picks.mjs. Always
// labelled as one person's opinion; never scored, never a sheet value. Renders nothing without a pick.
import notes from "@/config/owner-notes.generated.json";
import type { MsgKey } from "@/i18n";
import type { PageCtx } from "../_lib/context";

interface OwnerPick {
  model_year: number | null;
  variant: string | null;
  verdict: "shortlist" | "consider" | "fallback" | null;
  favourite: boolean;
  note: string | null;
}

const BY_GEN = (notes as unknown as { generations: Record<string, OwnerPick[]> }).generations;

export function ownerPicks(generationId: string): OwnerPick[] {
  return BY_GEN[generationId] ?? [];
}

export function OwnerNote({ ctx, generationIds, headingLevel = 2 }: { ctx: PageCtx; generationIds: string[]; headingLevel?: 2 | 3 }) {
  const { t } = ctx;
  const picks = generationIds.flatMap((id) => ownerPicks(id));
  if (!picks.length) return null;
  const H = headingLevel === 2 ? "h2" : "h3";
  return (
    <section aria-labelledby="owner-note" className="mt-8 max-w-3xl rounded-md border border-slate-300 bg-[var(--sunflower-tint)] p-4" data-testid="owner-note">
      <H id="owner-note" className="text-lg font-semibold">
        {t("owner.title")}
      </H>
      <ul className="mt-2 grid gap-2 text-sm">
        {picks.map((p, i) => (
          <li key={i}>
            <span className="font-semibold">
              {[p.model_year, p.variant].filter(Boolean).join(" · ")}
              {p.verdict ? `: ${t(`owner.verdict.${p.verdict}` as MsgKey)}` : ""}
              {p.favourite ? ` (${t("owner.favourite")})` : ""}
            </span>
            {p.note ? <span className="block text-slate-800">“{p.note}”</span> : null}
          </li>
        ))}
      </ul>
      <p className="mt-2 text-xs text-slate-700">{t("owner.label")}</p>
    </section>
  );
}
