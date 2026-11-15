import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { isReviewFile, loadReview, parseCsv, reviewPage, staffPagesEnabled } from "./review";

describe("review queue (staff page)", () => {
  it("is off unless STAFF_PAGES=1", () => {
    expect(staffPagesEnabled({})).toBe(false);
    expect(staffPagesEnabled({ STAFF_PAGES: "true" })).toBe(false);
    expect(staffPagesEnabled({ STAFF_PAGES: "0" })).toBe(false);
    expect(staffPagesEnabled({ STAFF_PAGES: "1" })).toBe(true);
  });

  it("only knows the two review files", () => {
    expect(isReviewFile("unmatched")).toBe(true);
    expect(isReviewFile("conflicts")).toBe(true);
    expect(isReviewFile("validation")).toBe(false);
    expect(isReviewFile("../secrets")).toBe(false);
  });

  it("parses RFC 4180 CSV: quotes, escaped quotes, commas, CRLF", () => {
    const csv = 'a,b,c\r\n1,"KONA, KAUAI","say ""hi"""\n2,,\n"multi\nline",x,y\n';
    expect(parseCsv(csv)).toEqual([
      ["a", "b", "c"],
      ["1", "KONA, KAUAI", 'say "hi"'],
      ["2", "", ""],
      ["multi\nline", "x", "y"],
    ]);
    expect(parseCsv("a,b")).toEqual([["a", "b"]]);
    expect(parseCsv("")).toEqual([]);
  });

  it("filters by source and paginates", () => {
    const rows = Array.from({ length: 7 }, (_, i) => [i % 2 ? "rdw" : "eea", String(i)]);
    const table = { header: ["source_id", "n"], rows };
    const all = reviewPage(table, {}, 3);
    expect(all.sources).toEqual(["eea", "rdw"]);
    expect(all.pages).toBe(3);
    expect(all.rows).toHaveLength(3);
    const rdw = reviewPage(table, { source: "rdw", page: 2 }, 2);
    expect(rdw.matching).toBe(3);
    expect(rdw.rows.map((r) => r[1])).toEqual(["5"]);
    // Out-of-range pages clamp.
    expect(reviewPage(table, { page: 99 }, 3).page).toBe(3);
    expect(reviewPage(table, { page: -1 }, 3).page).toBe(1);
    expect(reviewPage(table, { source: "nope" }, 3)).toMatchObject({ matching: 0, pages: 1, rows: [] });
  });

  it("loads a file and reports a missing one", () => {
    const dir = mkdtempSync(path.join(tmpdir(), "review-"));
    mkdirSync(dir, { recursive: true });
    writeFileSync(path.join(dir, "conflicts.csv"), "variant_id,source_id\nv1,eea\n");
    const ok = loadReview("conflicts", dir);
    expect(ok.ok && ok.table).toEqual({ header: ["variant_id", "source_id"], rows: [["v1", "eea"]] });
    expect(loadReview("unmatched", dir)).toEqual({ ok: false, reason: "missing" });
  });
});
