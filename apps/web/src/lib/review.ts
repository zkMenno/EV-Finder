// Read-only access to the pipeline's review queue (data/review/*.csv) for the staff page.
// Server only. Never linked from public pages; the page itself checks STAFF_PAGES=1.
import { readFileSync, statSync } from "node:fs";
import path from "node:path";

export const REVIEW_FILES = ["unmatched", "conflicts"] as const;
export type ReviewFile = (typeof REVIEW_FILES)[number];
export const REVIEW_PAGE_SIZE = 500;

export function isReviewFile(v: unknown): v is ReviewFile {
  return typeof v === "string" && (REVIEW_FILES as readonly string[]).includes(v);
}

/** Staff pages are off unless STAFF_PAGES=1. */
export function staffPagesEnabled(env: Record<string, string | undefined> = process.env): boolean {
  return env.STAFF_PAGES === "1";
}

/** Directory holding the review CSVs. REVIEW_DIR overrides it. */
export function reviewDir(): string {
  return process.env.REVIEW_DIR || path.resolve(process.cwd(), "../../data/review");
}

/** RFC 4180 CSV: quoted fields, "" escapes, commas and newlines inside quotes, CRLF or LF. */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i++;
        } else quoted = false;
      } else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") {
      row.push(field);
      field = "";
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else field += c;
  }
  if (field !== "" || row.length) {
    row.push(field);
    rows.push(row);
  }
  return rows.filter((r) => !(r.length === 1 && r[0] === ""));
}

export interface ReviewTable {
  header: string[];
  rows: string[][];
}

export type ReviewLoad = { ok: true; table: ReviewTable; updated: Date } | { ok: false; reason: "missing" | "unreadable" };

export function loadReview(file: ReviewFile, dir = reviewDir()): ReviewLoad {
  const p = path.join(dir, `${file}.csv`);
  let updated: Date;
  try {
    updated = statSync(p).mtime;
  } catch {
    return { ok: false, reason: "missing" };
  }
  try {
    const [header = [], ...rows] = parseCsv(readFileSync(p, "utf8"));
    return { ok: true, table: { header, rows }, updated };
  } catch {
    return { ok: false, reason: "unreadable" };
  }
}

export interface ReviewPage {
  /** Distinct values of the `source_id` column, sorted. */
  sources: string[];
  rows: string[][];
  /** Rows matching the source filter. */
  matching: number;
  page: number;
  pages: number;
}

/** Filter by source (exact match on `source_id`) and cut one page of at most `size` rows. */
export function reviewPage(table: ReviewTable, opts: { source?: string; page?: number }, size = REVIEW_PAGE_SIZE): ReviewPage {
  const col = table.header.indexOf("source_id");
  const sources = col < 0 ? [] : [...new Set(table.rows.map((r) => r[col] ?? ""))].filter(Boolean).sort();
  const filtered = opts.source && col >= 0 ? table.rows.filter((r) => r[col] === opts.source) : table.rows;
  const pages = Math.max(1, Math.ceil(filtered.length / size));
  const page = Math.min(Math.max(1, Math.trunc(opts.page ?? 1) || 1), pages);
  return { sources, rows: filtered.slice((page - 1) * size, page * size), matching: filtered.length, page, pages };
}
