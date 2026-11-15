// Ranking list table (T-011). Server component: the page prepares the cells (numbers in <Num>).
import type { ReactNode } from "react";

export interface RankingRowView {
  key: string;
  rank: number;
  cells: ReactNode[];
}

export function RankingTable({
  caption,
  rankHeader,
  headers,
  rows,
}: {
  caption: string;
  rankHeader: string;
  /** Column headers after the rank; the first column is the row header (the car). May carry a glossary ⓘ. */
  headers: ReactNode[];
  rows: RankingRowView[];
}) {
  return (
    <div className="overflow-x-auto rounded-md border border-slate-300" tabIndex={0} role="region" aria-label={caption}>
      <table className="min-w-full border-collapse text-sm" data-testid="ranking-table">
        <caption className="px-3 py-2 text-left font-semibold">{caption}</caption>
        <thead className="bg-slate-50">
          <tr>
            <th scope="col" className="w-14 px-3 py-2 text-right font-semibold">
              {rankHeader}
            </th>
            {headers.map((h, i) => (
              <th key={i} scope="col" className="px-3 py-2 text-left font-semibold">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.key} className="border-t border-slate-200">
              <td className="px-3 py-2 text-right align-top tabular-nums">{r.rank}</td>
              {r.cells.map((c, i) =>
                i === 0 ? (
                  <th key={i} scope="row" className="px-3 py-2 text-left align-top font-medium">
                    {c}
                  </th>
                ) : (
                  <td key={i} className="px-3 py-2 align-top">
                    {c}
                  </td>
                ),
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
