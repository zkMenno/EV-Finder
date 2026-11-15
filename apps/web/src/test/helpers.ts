import type { Catalogue, PublishedVariant } from "@ev/schema";
import fixture from "@/fixtures/catalogue.sample.json";
import { toExploreRow, type ExploreRow } from "@/lib/explore-data";

export const catalogue = fixture as unknown as Catalogue;
export const rows: ExploreRow[] = catalogue.rows.map((r) => toExploreRow(r));

export function row(over: Partial<PublishedVariant> & { variant_id: string }): ExploreRow {
  const base: PublishedVariant = {
    release: 1,
    variant_name: "V",
    generation_id: "g",
    generation_name: "G",
    model_id: "m",
    model_name: "M",
    make_id: "mk",
    make_name: "Make",
    year_start: 2020,
    era: "2018-20",
    quality_tier: "sourced",
    provenance: {},
    ...over,
  };
  return toExploreRow(base);
}
