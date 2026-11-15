// Staff-only, read-only view of the pipeline's review queue (data/review/unmatched.csv and
// conflicts.csv). 404 unless STAFF_PAGES=1 and the staff credentials are sent; never indexed; not linked from public pages.
// Plain links and a GET form: works without JS, no client component.
import type { Metadata } from "next";
import Link from "next/link";
import { getT } from "@/i18n";
import { formatNumber } from "@/lib/format";
import { isReviewFile, loadReview, REVIEW_FILES, REVIEW_PAGE_SIZE, reviewPage, type ReviewFile } from "@/lib/review";
import { requireStaff } from "@/lib/staff-guard";

export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Review queue", robots: { index: false, follow: false } };

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);

function href(file: ReviewFile, source?: string, page?: number): string {
  const q = new URLSearchParams({ file });
  if (source) q.set("source", source);
  if (page && page > 1) q.set("page", String(page));
  return `/staff/review?${q}`;
}

export default async function StaffReviewPage({ searchParams }: Props) {
  // 404 unless STAFF_PAGES=1 and the Basic credentials match, checked here too (A-05 F2).
  await requireStaff();
  const t = getT("en");
  const sp = await searchParams;
  const rawFile = one(sp.file);
  const file: ReviewFile = isReviewFile(rawFile) ? rawFile : "unmatched";
  const source = one(sp.source) || undefined;
  const load = loadReview(file);
  const view = load.ok ? reviewPage(load.table, { source, page: Number(one(sp.page) ?? 1) }) : null;
  const fmt = (n: number) => formatNumber(n, "en-GB", 0);

  return (
    <main id="main" className="mx-auto max-w-[100rem] px-4 py-6">
      <h1 className="text-2xl font-bold tracking-tight">{t("staff.review.title")}</h1>
      <p className="mt-1 max-w-3xl text-sm text-slate-800">{t("staff.review.intro")}</p>

      <nav aria-label={t("staff.review.files")} className="mt-4 flex gap-4">
        {REVIEW_FILES.map((f) => (
          <Link
            key={f}
            href={href(f)}
            aria-current={f === file ? "page" : undefined}
            className={f === file ? "font-semibold underline underline-offset-4" : "text-blue-800 underline underline-offset-2"}
          >
            {f}.csv
          </Link>
        ))}
      </nav>

      {!load.ok || !view ? (
        <p role="status" className="mt-6 rounded border border-amber-700 p-3 text-amber-900">
          {t(!load.ok && load.reason === "missing" ? "staff.review.missing" : "staff.review.unreadable", { file: `${file}.csv` })}
        </p>
      ) : (
        <>
          <form method="get" action="/staff/review" className="mt-4 flex flex-wrap items-end gap-3">
            <input type="hidden" name="file" value={file} />
            <label className="flex flex-col text-sm">
              {t("staff.review.source")}
              <select name="source" defaultValue={source ?? ""} className="rounded border border-slate-400 px-2 py-1">
                <option value="">{t("staff.review.allSources")}</option>
                {view.sources.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" className="rounded border border-slate-500 px-3 py-1 text-sm">
              {t("staff.review.apply")}
            </button>
          </form>

          <p role="status" className="mt-3 text-sm" data-testid="staff-count">
            {t("staff.review.count", {
              matching: fmt(view.matching),
              total: fmt(load.table.rows.length),
              page: view.page,
              pages: view.pages,
              size: REVIEW_PAGE_SIZE,
              updated: load.updated.toISOString().slice(0, 16).replace("T", " "),
            })}
          </p>

          <div className="mt-3 overflow-x-auto rounded border border-slate-300">
            <table className="min-w-full text-left text-xs">
              <caption className="sr-only">{`${file}.csv`}</caption>
              <thead className="bg-slate-100">
                <tr>
                  {load.table.header.map((h) => (
                    <th key={h} scope="col" className="whitespace-nowrap px-2 py-1 font-semibold">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {view.rows.map((r, i) => (
                  <tr key={i} className="border-t border-slate-200 align-top" data-testid="staff-row">
                    {load.table.header.map((h, j) => (
                      <td key={h} className="max-w-md break-words px-2 py-1">
                        {r[j] ?? ""}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {view.pages > 1 ? (
            <nav aria-label={t("staff.review.pages")} className="mt-3 flex gap-4 text-sm">
              {view.page > 1 ? (
                <Link href={href(file, source, view.page - 1)} className="text-blue-800 underline">
                  {t("staff.review.prev")}
                </Link>
              ) : null}
              {view.page < view.pages ? (
                <Link href={href(file, source, view.page + 1)} className="text-blue-800 underline">
                  {t("staff.review.next")}
                </Link>
              ) : null}
            </nav>
          ) : null}
        </>
      )}
    </main>
  );
}
