import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { loadLearn, OUT_FILE, parseArticle, parseBlocks, parseInline, serialize } from "../../scripts/learn.mjs";
import { getCatalogue } from "./catalogue";
import { article, articleFile, articles } from "./learn";
import { sitemapUrls } from "./sitemap";

describe("learn Markdown subset (scripts/learn.mjs)", () => {
  it("inline: terms, links, bold, italic, code; raw HTML stays text", () => {
    expect(parseInline("A [[heat-pump|heat pump]] and [[lfp]].")).toEqual([
      { t: "text", v: "A " },
      { t: "term", id: "heat-pump", v: "heat pump" },
      { t: "text", v: " and " },
      { t: "term", id: "lfp" },
      { t: "text", v: "." },
    ]);
    expect(parseInline("**80 %** in [KBB](https://kbb.com/x) *often* `x`")).toEqual([
      { t: "strong", c: [{ t: "text", v: "80 %" }] },
      { t: "text", v: " in " },
      { t: "link", href: "https://kbb.com/x", c: [{ t: "text", v: "KBB" }] },
      { t: "text", v: " " },
      { t: "em", c: [{ t: "text", v: "often" }] },
      { t: "text", v: " " },
      { t: "code", v: "x" },
    ]);
    expect(parseInline("<script>x</script>")).toEqual([{ t: "text", v: "<script>x</script>" }]);
    expect(parseInline("[bad](javascript:alert(1))")[0]).toMatchObject({ t: "text" });
  });
  it("blocks: headings, paragraphs, lists, tables", () => {
    const b = parseBlocks("## Why\n\nLine one\nline two.\n\n- a\n- b\n\n1. x\n2. y\n\n| A | B |\n|---|---|\n| [[400v]] | 1 |\n");
    expect(b.map((x) => (x as { t: string }).t)).toEqual(["h", "p", "ul", "ol", "table"]);
    expect((b[1] as { c: unknown[] }).c).toEqual([{ t: "text", v: "Line one line two." }]);
    expect((b[4] as { rows: unknown[][] }).rows[0]![0]).toEqual([{ t: "term", id: "400v" }]);
  });
  it("front matter is checked; the leading H1 is dropped (the page renders the title)", () => {
    const md = '---\ntitle: "T"\nslug: s\nlang: en\nreview: needed\nupdated: 2026-11-15\nglossary: [lfp]\nsources:\n  - {title: "S", url: "https://x.example", retrieved: 2026-11-15}\n---\n# T\n\nBody [[lfp]].\n';
    const a = parseArticle(md, "s/en.md", { slug: "s", lang: "en" });
    expect(a.title).toBe("T");
    expect(a.review).toBe("needed");
    expect((a.blocks as unknown[]).length).toBe(1);
    expect(a.terms).toEqual(["lfp"]);
    expect(() => parseArticle(md.replace("lang: en", "lang: nl"), "s/en.md", { slug: "s", lang: "en" })).toThrow(/lang/);
  });
  it("the committed JSON matches content/learn", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(serialize(loadLearn()));
  });
});

describe("learn articles in the app", () => {
  it("every article has EN, falls back to EN, and is in the sitemap; no clash with glossary ids", () => {
    const ids = new Set(getCatalogue().taxonomy().glossary_terms.map((g) => g.id));
    expect(articles().length).toBeGreaterThan(0);
    for (const a of articles()) {
      expect(a.files.en).toBeDefined();
      expect(articleFile(a, "it")?.fallback).toBe(!a.files.it); // falls back only without an IT file (T-039/T-082 added some)
      expect(ids.has(a.slug)).toBe(false);
    }
    const urls = sitemapUrls(getCatalogue(), "https://x.example");
    expect(urls).toContain(`https://x.example/nl/nl/learn/${articles()[0]!.slug}`);
    expect(urls).toContain("https://x.example/be/fr/learn");
    expect(article("winter-range")?.files.nl?.review).toBe("needed");
  });
});
