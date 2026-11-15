// Side-by-side compare table (T-010). Server component: the page prepares cell content and the
// `differs` flags (from differingCells in src/lib/spec-diff.ts). Differences are shown with
// background + a ◆ marker + sr-only text, never colour alone. Print styles: compare/print.css.
import type { ReactNode } from "react";

export interface CompareColumn {
  key: string;
  header: ReactNode;
}
export interface CompareRowView {
  key: string;
  label: ReactNode;
  cells: { content: ReactNode; differs: boolean }[];
}
export interface CompareGroupView {
  key: string;
  title: string;
  rows: CompareRowView[];
}

export function CompareTable({
  caption,
  fieldHeader,
  differsLabel,
  columns,
  groups,
}: {
  caption: string;
  fieldHeader: string;
  differsLabel: string;
  columns: CompareColumn[];
  groups: CompareGroupView[];
}) {
  return (
    <div className="compare-scroll overflow-x-auto rounded-md border border-slate-300" tabIndex={0} role="region" aria-label={caption}>
      <table className="compare-table w-full min-w-[36rem] border-collapse text-sm" data-testid="compare-table">
        <caption className="sr-only">{caption}</caption>
        <colgroup>
          <col className="w-44" />
          {columns.map((c) => (
            <col key={c.key} />
          ))}
        </colgroup>
        <thead className="bg-slate-50">
          <tr>
            <th scope="col" className="sticky left-0 z-10 bg-slate-50 px-3 py-2 text-left font-semibold">
              {fieldHeader}
            </th>
            {columns.map((c) => (
              <th key={c.key} scope="col" className="px-3 py-2 text-left align-bottom font-semibold">
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        {groups.map((g) => (
          <tbody key={g.key}>
            <tr className="border-t-2 border-slate-400 bg-slate-100">
              <th scope="colgroup" colSpan={columns.length + 1} className="px-3 py-1.5 text-left text-xs font-bold uppercase tracking-wide text-slate-800">
                {g.title}
              </th>
            </tr>
            {g.rows.map((r) => (
              <tr key={r.key} className="border-t border-slate-200" data-differs={r.cells.some((c) => c.differs) || undefined}>
                <th scope="row" className="sticky left-0 z-10 bg-white px-3 py-2 text-left align-top font-medium">
                  {r.label}
                </th>
                {r.cells.map((c, i) => (
                  <td
                    key={i}
                    className={`px-3 py-2 align-top ${c.differs ? "compare-differs bg-amber-50 font-semibold shadow-[inset_3px_0_0_#b45309]" : ""}`}
                    data-differs={c.differs || undefined}
                  >
                    <span className="inline-flex items-start gap-1">
                      {c.differs ? (
                        <span className="text-amber-800" aria-hidden="true">
                          ◆
                        </span>
                      ) : null}
                      {c.differs ? <span className="sr-only">{differsLabel}: </span> : null}
                      {c.content}
                    </span>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        ))}
      </table>
    </div>
  );
}
