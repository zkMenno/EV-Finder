// /learn articles (content/learn, WS3) as parsed at build time by scripts/learn.mjs. Server only.
import type { Lang } from "@/config/countries";
import generated from "@/config/learn.generated.json";

export type Inline =
  | { t: "text"; v: string }
  | { t: "code"; v: string }
  | { t: "strong" | "em"; c: Inline[] }
  | { t: "link"; href: string; c: Inline[] }
  | { t: "term"; id: string; v?: string };

export type Block =
  | { t: "h"; level: 1 | 2 | 3; c: Inline[] }
  | { t: "p"; c: Inline[] }
  | { t: "ul" | "ol"; items: Inline[][] }
  | { t: "table"; head: Inline[][]; rows: Inline[][][] };

export interface ArticleFile {
  title: string;
  review: "needed" | "done";
  updated: string | null;
  glossary: string[];
  terms: string[];
  sources: { title: string; url: string; retrieved: string | null }[];
  blocks: Block[];
}

export interface Article {
  slug: string;
  order: number;
  title: Partial<Record<Lang, string>>;
  langs: Lang[];
  files: Partial<Record<Lang, ArticleFile>>;
}

const data = generated as unknown as { articles: Article[] };

export function articles(): Article[] {
  return data.articles;
}

export function article(slug: string): Article | undefined {
  return data.articles.find((a) => a.slug === slug);
}

/** The file for `lang`, else EN (`fallback: true`). */
export function articleFile(a: Article, lang: Lang): { file: ArticleFile; lang: Lang; fallback: boolean } | null {
  const own = a.files[lang];
  if (own) return { file: own, lang, fallback: false };
  const en = a.files.en;
  return en ? { file: en, lang: "en", fallback: lang !== "en" } : null;
}

export function articleTitle(a: Article, lang: Lang): string {
  return a.title[lang] ?? a.title.en ?? a.slug;
}
