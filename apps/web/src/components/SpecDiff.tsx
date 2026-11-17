// Spec diff table for a generation (T-009): rows = key fields, columns = variants in timeline
// order. Cells that differ from the column to their left are marked with text (▲ + sr-only), not colour alone.
// Server component; the page prepares cell content (numbers already wrapped in <Num>).
import type { ReactNode } from "react";

export interface SpecDiffColumn {
  key: string;
  header: ReactNode;
}
export interface SpecDiffRowView {
  key: string;
  label: ReactNode;
  cells: { content: ReactNode; changed: boolean }[];
  /** No cell changed: hidden under "differences only" (DiffOnly, T-045). */
  same?: boolean;
}

export function SpecDiff({
  caption,
  fieldHeader,
  changedLabel,
  columns,
  rows,
}: {
  caption: string;
  fieldHeader: string;
  changedLabel: string;
  columns: SpecDiffColumn[];
  rows: SpecDiffRowView[];
}) {
  return (
    <div className="relative overflow-x-auto rounded-md border border-slate-300" tabIndex={0} role="region" aria-label={caption}>
      <table className="min-w-full border-collapse text-sm" data-testid="spec-diff">
        <caption className="px-3 py-2 text-left text-sm text-slate-800">{caption}</caption>
        <thead className="bg-slate-50">
          <tr>
            <th scope="col" className="sticky left-0 z-10 bg-slate-50 px-3 py-2 text-left font-semibold">
              {fieldHeader}
            </th>
            {columns.map((c) => (
              <th key={c.key} scope="col" className="min-w-36 px-3 py-2 text-left align-bottom font-semibold">
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr
              key={r.key}
              className={`border-t border-slate-200 ${r.same ? "group-data-[only-diff]:hidden" : ""}`}
              data-same={r.same || undefined}
            >
              <th scope="row" className="sticky left-0 z-10 bg-white px-3 py-2 text-left align-top font-medium">
                {r.label}
              </th>
              {r.cells.map((c, i) => (
                <td
                  key={i}
                  className={`px-3 py-2 align-top ${c.changed ? "bg-amber-50 shadow-[inset_3px_0_0_var(--warning)]" : ""}`}
                  data-changed={c.changed || undefined}
                >
                  <span className="inline-flex items-start gap-1">
                    {c.changed ? (
                      <span className="text-amber-800" aria-hidden="true">
                        ▲
                      </span>
                    ) : null}
                    {c.changed ? <span className="sr-only">{changedLabel}: </span> : null}
                    {c.content}
                  </span>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
