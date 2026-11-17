// "Most popular" sort (T-130, Decision 038 blend). Pure: safe on server and client.
// Inputs come from src/config/popularity.generated.json (scripts/popularity.mjs: data/seed/top40.yaml registration
// scores per model, Menno's verdicts per generation, weights from config/popularity.yaml). Ranked per generation:
// every variant of one generation shares its score and "#n popular".

export interface PopularityInputs {
  weights: { registrations: number; owner_picks: number };
  /** model id → registration score (% share of the BEV fleet, top40 method). */
  models: Record<string, number>;
  /** generation id → owner pick 0..1 (absent = no verdict). */
  generations: Record<string, number>;
}

export interface Popularity {
  /** 0–100, one decimal. */
  score: number;
  /** 1 = most popular generation in this catalogue. */
  rank: number;
}

/** 0–100 or null when we know neither registrations nor a pick for this car (sorts last, no tag). */
export function popularityScore(modelId: string, generationId: string, inputs: PopularityInputs): number | null {
  const reg = inputs.models[modelId];
  const pick = inputs.generations[generationId];
  if (reg === undefined && pick === undefined) return null;
  const max = Math.max(0, ...Object.values(inputs.models));
  const share = reg !== undefined && max > 0 ? reg / max : 0;
  const { registrations: wr, owner_picks: wp } = inputs.weights;
  const total = wr + wp;
  if (total <= 0) return null;
  const s = (100 * (wr * share + wp * (pick ?? 0))) / total;
  return Math.round(s * 10) / 10;
}

/**
 * Score and rank per generation id, over the generations present in `rows`.
 * Ties keep a stable order by generation id, so the rank never flips between builds.
 */
export function rankGenerations(
  rows: readonly { model_id: string; generation_id: string }[],
  inputs: PopularityInputs,
): Map<string, Popularity> {
  const scores = new Map<string, number>();
  for (const r of rows) {
    if (scores.has(r.generation_id)) continue;
    const s = popularityScore(r.model_id, r.generation_id, inputs);
    if (s !== null) scores.set(r.generation_id, s);
  }
  const order = [...scores.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  return new Map(order.map(([id, score], i) => [id, { score, rank: i + 1 }]));
}
