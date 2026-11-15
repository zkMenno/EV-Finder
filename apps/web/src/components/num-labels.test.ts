import type { FieldProvenance } from "@ev/schema";
import { describe, expect, it } from "vitest";
import { getT } from "@/i18n";
import { getCatalogue } from "@/lib/catalogue";
import { localizeTaxonomy } from "@/lib/taxonomy";
import { NUM_TERMS, numGlossary, numLabels } from "./num-labels";
import { numBadgeTerms, numBadges } from "./Num";

describe("Num glossary wiring (glossary sweep item 7)", () => {
  it("links only the terms the glossary has", () => {
    const g = numGlossary({ base: "/nl/en", terms: ["estimate", "sources-agree"] });
    expect(g).toEqual({ estimate: "/nl/en/learn/estimate", agree: "/nl/en/learn/sources-agree" });
  });

  it("every NUM_TERMS id exists in the published glossary", () => {
    const terms = localizeTaxonomy(getCatalogue().taxonomy(), "en").terms;
    const g = numGlossary({ base: "/nl/en", terms });
    for (const [k, id] of Object.entries(NUM_TERMS)) {
      expect(terms[id], `glossary term ${id}`).toBeDefined();
      expect(g[k as keyof typeof NUM_TERMS]).toBe(`/nl/en/learn/${id}`);
    }
  });

  it("badges carry their term; numBadges keeps the plain text", () => {
    const labels = numLabels(getT("en"));
    const prov: FieldProvenance = { source_ids: ["a", "b"], confidence: "high", estimate: true, agreeing_sources: 2 };
    expect(numBadgeTerms(prov, labels, true).map((b) => b.term)).toEqual(["claim", "estimate", "agree"]);
    expect(numBadges(prov, labels, true)).toEqual(["claim", "estimate", "2 sources agree"]);
    expect(labels.glossary).toBeUndefined();
  });
});
