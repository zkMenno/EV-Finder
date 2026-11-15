// Build-time loader for /learn articles (WS3 content, content/learn/README.md): reads
// content/learn/index.yaml and content/learn/<slug>/<lang>.md, parses the front matter and a small
// Markdown subset into a JSON tree, and writes src/config/learn.generated.json. The server renders
// that tree (src/components/LearnArticle.tsx); no Markdown library reaches any bundle.
//
// Markdown subset (what the drafts use): # / ## / ### headings, paragraphs, "- " lists,
// "1. " lists, pipe tables, **bold**, *italic*, `code`, [text](https://…), and glossary markers
// [[id]] / [[id|shown text]]. Raw HTML is never passed through (it stays text).
//
//   node scripts/learn.mjs           write the JSON (runs before `next build` and `next dev`)
//   node scripts/learn.mjs --check   fail if the committed JSON is out of date
//
// The Docker build context has no content/, so there the committed JSON is kept (a unit test
// keeps it in step with the Markdown).
/* global process, console */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import * as yaml from "js-yaml";

const here = path.dirname(fileURLToPath(import.meta.url));
export const CONTENT_DIR = path.resolve(here, "../../../content/learn");
export const OUT_FILE = path.resolve(here, "../src/config/learn.generated.json");
export const LANGS = ["en", "nl", "de", "fr", "es", "it"];
const SLUG_RE = /^[a-z0-9][a-z0-9-]*$/;

/** Inline Markdown → tokens: {t:"text"|"strong"|"em"|"code"|"link"|"term", …}. */
export function parseInline(src) {
  const out = [];
  let buf = "";
  const flush = () => {
    if (buf) out.push({ t: "text", v: buf });
    buf = "";
  };
  let i = 0;
  while (i < src.length) {
    const rest = src.slice(i);
    let m;
    if ((m = /^\[\[([a-z0-9][a-z0-9-]*)(?:\|([^\]]+))?\]\]/.exec(rest))) {
      flush();
      out.push({ t: "term", id: m[1], ...(m[2] ? { v: m[2] } : {}) });
      i += m[0].length;
    } else if ((m = /^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/.exec(rest))) {
      flush();
      out.push({ t: "link", href: m[2], c: parseInline(m[1]) });
      i += m[0].length;
    } else if ((m = /^\*\*(.+?)\*\*/.exec(rest))) {
      flush();
      out.push({ t: "strong", c: parseInline(m[1]) });
      i += m[0].length;
    } else if ((m = /^\*([^*\s][^*]*?)\*/.exec(rest))) {
      flush();
      out.push({ t: "em", c: parseInline(m[1]) });
      i += m[0].length;
    } else if ((m = /^`([^`]+)`/.exec(rest))) {
      flush();
      out.push({ t: "code", v: m[1] });
      i += m[0].length;
    } else {
      buf += src[i];
      i += 1;
    }
  }
  flush();
  return out;
}

const cells = (line) =>
  line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((c) => c.trim());

/** Block Markdown → [{t:"h", level, c} | {t:"p", c} | {t:"ul"|"ol", items} | {t:"table", head, rows}]. */
export function parseBlocks(md) {
  const lines = md.replace(/\r\n/g, "\n").split("\n");
  const blocks = [];
  let para = [];
  const endPara = () => {
    if (para.length) blocks.push({ t: "p", c: parseInline(para.join(" ")) });
    para = [];
  };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    let m;
    if (!line.trim()) {
      endPara();
    } else if ((m = /^(#{1,3})\s+(.*)$/.exec(line))) {
      endPara();
      blocks.push({ t: "h", level: m[1].length, c: parseInline(m[2].trim()) });
    } else if (/^\s*[-*]\s+/.test(line) || /^\s*\d+\.\s+/.test(line)) {
      endPara();
      const ordered = /^\s*\d+\.\s+/.test(line);
      const re = ordered ? /^\s*\d+\.\s+/ : /^\s*[-*]\s+/;
      const items = [];
      while (i < lines.length && re.test(lines[i])) {
        let item = lines[i].replace(re, "");
        // Continuation lines (indented, not a new item).
        while (i + 1 < lines.length && /^\s{2,}\S/.test(lines[i + 1]) && !re.test(lines[i + 1])) item += ` ${lines[++i].trim()}`;
        items.push(parseInline(item));
        i++;
      }
      i--;
      blocks.push({ t: ordered ? "ol" : "ul", items });
    } else if (/^\s*\|/.test(line) && i + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[i + 1])) {
      endPara();
      const head = cells(line).map(parseInline);
      i += 2;
      const rows = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) rows.push(cells(lines[i++]).map(parseInline));
      i--;
      blocks.push({ t: "table", head, rows });
    } else {
      para.push(line.trim());
    }
  }
  endPara();
  return blocks;
}

/** Splits front matter from the body; returns { front, body }. */
export function splitFrontMatter(text, where) {
  const m = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/.exec(text.replace(/\r\n/g, "\n"));
  if (!m) throw new Error(`${where}: missing front matter`);
  return { front: yaml.load(m[1], { schema: yaml.CORE_SCHEMA }) ?? {}, body: m[2] };
}

function termIds(blocks) {
  const ids = new Set();
  const walk = (toks) => {
    for (const tk of toks) {
      if (tk.t === "term") ids.add(tk.id);
      if (tk.c) walk(tk.c);
    }
  };
  for (const b of blocks) {
    if (b.c) walk(b.c);
    for (const it of b.items ?? []) walk(it);
    for (const row of [...(b.head ? [b.head] : []), ...(b.rows ?? [])]) for (const c of row) walk(c);
  }
  return [...ids].sort();
}

/** One article file → { title, review, updated, glossary, sources, blocks }. */
export function parseArticle(text, where, expect) {
  const { front: f, body } = splitFrontMatter(text, where);
  const errors = [];
  if (f.slug !== expect.slug) errors.push(`slug must be "${expect.slug}"`);
  if (f.lang !== expect.lang) errors.push(`lang must be "${expect.lang}"`);
  if (typeof f.title !== "string" || !f.title.trim()) errors.push("title is required");
  if (f.review !== "needed" && f.review !== "done") errors.push('review must be "needed" or "done"');
  const sources = Array.isArray(f.sources) ? f.sources : [];
  for (const [i, s] of sources.entries()) {
    if (!s || typeof s.title !== "string" || typeof s.url !== "string" || !/^https?:\/\//.test(s.url)) errors.push(`sources[${i}] needs title and url`);
  }
  if (errors.length) throw new Error(`${where}: ${errors.join("; ")}`);
  // Drop a leading H1 that repeats the title: the page renders the title itself.
  let blocks = parseBlocks(body);
  if (blocks[0]?.t === "h" && blocks[0].level === 1) blocks = blocks.slice(1);
  return {
    title: f.title.trim(),
    review: f.review,
    updated: f.updated == null ? null : String(f.updated),
    glossary: Array.isArray(f.glossary) ? f.glossary.map(String) : [],
    terms: termIds(blocks),
    sources: sources.map((s) => ({ title: s.title, url: s.url, retrieved: s.retrieved == null ? null : String(s.retrieved) })),
    blocks,
  };
}

export function loadLearn(dir = CONTENT_DIR) {
  const idx = yaml.load(readFileSync(path.join(dir, "index.yaml"), "utf8"), { schema: yaml.CORE_SCHEMA });
  if (!idx || !Array.isArray(idx.articles)) throw new Error("content/learn/index.yaml: articles must be a list");
  const articles = [];
  const seen = new Set();
  for (const a of idx.articles) {
    if (typeof a.slug !== "string" || !SLUG_RE.test(a.slug)) throw new Error(`index.yaml: bad slug ${a.slug}`);
    if (seen.has(a.slug)) throw new Error(`index.yaml: duplicate slug ${a.slug}`);
    seen.add(a.slug);
    const langs = (a.langs ?? []).filter((l) => LANGS.includes(l));
    if (!langs.includes("en")) throw new Error(`index.yaml: ${a.slug} needs an en file`);
    const files = {};
    for (const lang of langs) {
      const p = path.join(dir, a.slug, `${lang}.md`);
      if (!existsSync(p)) throw new Error(`index.yaml lists ${a.slug}/${lang}.md but it doesn't exist`);
      files[lang] = parseArticle(readFileSync(p, "utf8"), `${a.slug}/${lang}.md`, { slug: a.slug, lang });
    }
    articles.push({ slug: a.slug, order: Number(a.order ?? 0), title: a.title ?? {}, langs, files });
  }
  articles.sort((x, y) => x.order - y.order);
  return { articles };
}

export function serialize(config) {
  return JSON.stringify(config) + "\n";
}

function main() {
  const check = process.argv.includes("--check");
  if (!existsSync(path.join(CONTENT_DIR, "index.yaml"))) {
    if (check) throw new Error(`${CONTENT_DIR}/index.yaml not found`);
    console.warn(`learn: ${CONTENT_DIR} not found, keeping ${path.basename(OUT_FILE)}`);
    if (!existsSync(OUT_FILE)) writeFileSync(OUT_FILE, serialize({ articles: [] }));
    return;
  }
  const json = serialize(loadLearn());
  const current = existsSync(OUT_FILE) ? readFileSync(OUT_FILE, "utf8") : "";
  if (check) {
    if (current !== json) {
      console.error("learn: src/config/learn.generated.json is out of date; run `node scripts/learn.mjs`");
      process.exit(1);
    }
    return;
  }
  if (current !== json) writeFileSync(OUT_FILE, json);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
