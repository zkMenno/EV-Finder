// URL segments for model / generation / variant pages, from stable catalogue ids.
// Segment = id minus its parent's id prefix ("audi-e-tron-ge" under "audi-e-tron" → "ge")
// when that is clean; otherwise the full id ("vw-e-golf" under "volkswagen").
import type { PublishedVariant } from "@ev/schema";

type Ids = Pick<PublishedVariant, "make_id" | "model_id" | "generation_id" | "variant_id">;

export function childSegment(id: string, parentId: string): string {
  const p = `${parentId}-`;
  return id.startsWith(p) && id.length > p.length ? id.slice(p.length) : id;
}

export const makeSeg = (r: Pick<Ids, "make_id">) => r.make_id;
export const modelSeg = (r: Pick<Ids, "make_id" | "model_id">) => childSegment(r.model_id, r.make_id);
export const genSeg = (r: Pick<Ids, "model_id" | "generation_id">) => childSegment(r.generation_id, r.model_id);
export const variantSeg = (r: Pick<Ids, "generation_id" | "variant_id">) => childSegment(r.variant_id, r.generation_id);

export function modelHref(country: string, r: Pick<Ids, "make_id" | "model_id">): string {
  return `/${country}/ev/${makeSeg(r)}/${modelSeg(r)}`;
}
export function generationHref(country: string, r: Pick<Ids, "make_id" | "model_id" | "generation_id">): string {
  return `${modelHref(country, r)}/${genSeg(r)}`;
}
export function variantHref(country: string, r: Ids): string {
  return `${generationHref(country, r)}/${variantSeg(r)}`;
}

export function modelRows<T extends Ids>(rows: readonly T[], make: string, model: string): T[] {
  return rows.filter((r) => makeSeg(r) === make && modelSeg(r) === model);
}
export function generationRows<T extends Ids>(rows: readonly T[], make: string, model: string, gen: string): T[] {
  return modelRows(rows, make, model).filter((r) => genSeg(r) === gen);
}
export function findVariant<T extends Ids>(rows: readonly T[], make: string, model: string, gen: string, variant: string): T | undefined {
  return generationRows(rows, make, model, gen).find((r) => variantSeg(r) === variant);
}

function uniq<T>(items: T[], key: (t: T) => string): T[] {
  const seen = new Map<string, T>();
  for (const i of items) if (!seen.has(key(i))) seen.set(key(i), i);
  return [...seen.values()];
}

export function modelParams(rows: readonly Ids[]): { make: string; model: string }[] {
  return uniq(
    rows.map((r) => ({ make: makeSeg(r), model: modelSeg(r) })),
    (p) => `${p.make}/${p.model}`,
  );
}
export function generationParams(rows: readonly Ids[]): { make: string; model: string; generation: string }[] {
  return uniq(
    rows.map((r) => ({ make: makeSeg(r), model: modelSeg(r), generation: genSeg(r) })),
    (p) => `${p.make}/${p.model}/${p.generation}`,
  );
}
export function variantParams(rows: readonly Ids[]): { make: string; model: string; generation: string; variant: string }[] {
  return rows.map((r) => ({ make: makeSeg(r), model: modelSeg(r), generation: genSeg(r), variant: variantSeg(r) }));
}

/** Paths that more than one variant would map to (must be empty; tested). */
export function segmentCollisions(rows: readonly Ids[]): string[] {
  const seen = new Map<string, string>();
  const out: string[] = [];
  for (const r of rows) {
    const p = variantHref("x", r);
    const prev = seen.get(p);
    if (prev && prev !== r.variant_id) out.push(p);
    seen.set(p, r.variant_id);
  }
  return out;
}
