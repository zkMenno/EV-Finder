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

type PopRow = { model_id: string; generation_id: string; registered_count_nl?: number | null };

/**
 * Registration share per generation. top40 scores are per MODEL, so a model's share is split over its
 * generations in this catalogue by the release's own RDW count per generation (`registered_count_nl`,
 * counted at generation level). A generation without a count while its siblings have one gets none of
 * the share (not on Dutch roads in the RDW window). A model with no RDW count at all is split evenly.
 */
export function generationShares(rows: readonly PopRow[], models: Record<string, number>): Map<string, number> {
  const gens = new Map<string, { model: string; count: number | null }>();
  for (const r of rows) {
    const c = typeof r.registered_count_nl === "number" && r.registered_count_nl >= 0 ? r.registered_count_nl : null;
    const g = gens.get(r.generation_id);
    if (!g) gens.set(r.generation_id, { model: r.model_id, count: c });
    else if (c !== null) g.count = Math.max(g.count ?? 0, c);
  }
  const byModel = new Map<string, string[]>();
  for (const [id, g] of gens) (byModel.get(g.model) ?? byModel.set(g.model, []).get(g.model)!).push(id);
  const out = new Map<string, number>();
  for (const [model, ids] of byModel) {
    const reg = models[model];
    if (reg === undefined) continue;
    const total = ids.reduce((t, id) => t + (gens.get(id)!.count ?? 0), 0);
    for (const id of ids) out.set(id, total > 0 ? (reg * (gens.get(id)!.count ?? 0)) / total : reg / ids.length);
  }
  return out;
}

/**
 * Score (0–100, one decimal) and rank per generation id, over the generations present in `rows`.
 * Null score = neither registrations nor a pick known: no rank, sorts last. Ties keep a stable order by id.
 */
export function rankGenerations(rows: readonly PopRow[], inputs: PopularityInputs): Map<string, Popularity> {
  const shares = generationShares(rows, inputs.models);
  const max = Math.max(0, ...shares.values());
  const { registrations: wr, owner_picks: wp } = inputs.weights;
  const total = wr + wp;
  const scores = new Map<string, number>();
  if (total <= 0) return new Map();
  for (const r of rows) {
    if (scores.has(r.generation_id)) continue;
    const share = shares.get(r.generation_id);
    const pick = inputs.generations[r.generation_id];
    if (share === undefined && pick === undefined) continue;
    const s = (100 * (wr * (share !== undefined && max > 0 ? share / max : 0) + wp * (pick ?? 0))) / total;
    scores.set(r.generation_id, Math.round(s * 10) / 10);
  }
  const order = [...scores.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  return new Map(order.map(([id, score], i) => [id, { score, rank: i + 1 }]));
}
