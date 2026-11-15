// Renders a /learn article tree (src/lib/learn.ts) on the server. Glossary markers become the
// shown text + an ⓘ tooltip (glossary ids link to their learn page; chemistry / voltage-class ids
// to /learn/chemistry and /learn/voltage-class). Unknown ids render as plain text.
import type { ReactNode } from "react";
import { InfoTip, type TermText } from "@/components/Term";
import type { Block, Inline } from "@/lib/learn";

export interface LearnTerm {
  label: string;
  short: string;
  href: string;
}

export interface LearnCtx {
  terms: Record<string, LearnTerm | undefined>;
  termText: TermText;
  newTab: string;
}

const linkCls = "text-blue-800 underline underline-offset-2 hover:text-blue-950";

function inline(toks: Inline[], c: LearnCtx, key = ""): ReactNode[] {
  return toks.map((tk, i) => {
    const k = `${key}${i}`;
    switch (tk.t) {
      case "text":
        return tk.v;
      case "code":
        return <code key={k}>{tk.v}</code>;
      case "strong":
        return <strong key={k}>{inline(tk.c, c, `${k}-`)}</strong>;
      case "em":
        return <em key={k}>{inline(tk.c, c, `${k}-`)}</em>;
      case "link":
        return (
          <a key={k} href={tk.href} rel="noopener nofollow" target="_blank" className={linkCls}>
            {inline(tk.c, c, `${k}-`)}
            <span className="sr-only"> {c.newTab}</span>
          </a>
        );
      case "term": {
        const term = c.terms[tk.id];
        const shown = tk.v ?? term?.label ?? tk.id;
        if (!term) return <span key={k}>{shown}</span>;
        return (
          <span key={k} className="inline-flex items-baseline" data-term={tk.id}>
            <span className="underline decoration-dotted underline-offset-2">{shown}</span>
            <InfoTip label={term.label} href={term.href} text={c.termText}>
              <span className="block">{term.short}</span>
            </InfoTip>
          </span>
        );
      }
    }
  });
}

export function LearnBlocks({ blocks, ctx }: { blocks: Block[]; ctx: LearnCtx }) {
  return (
    <>
      {blocks.map((b, i) => {
        const k = String(i);
        switch (b.t) {
          case "h": {
            // The page's H1 is the title, so article headings start at H2.
            const H = b.level <= 2 ? "h2" : "h3";
            return (
              <H key={k} className={H === "h2" ? "mt-8 text-xl font-semibold" : "mt-6 text-lg font-semibold"}>
                {inline(b.c, ctx, `${k}-`)}
              </H>
            );
          }
          case "p":
            return (
              <p key={k} className="mt-3">
                {inline(b.c, ctx, `${k}-`)}
              </p>
            );
          case "ul":
          case "ol": {
            const L = b.t;
            return (
              <L key={k} className={`mt-3 flex flex-col gap-1 pl-5 ${L === "ul" ? "list-disc" : "list-decimal"}`}>
                {b.items.map((it, j) => (
                  <li key={j}>{inline(it, ctx, `${k}-${j}-`)}</li>
                ))}
              </L>
            );
          }
          case "table":
            return (
              <div key={k} className="relative mt-4 overflow-x-auto">
                <table className="min-w-full border-collapse text-sm">
                  <thead>
                    <tr>
                      {b.head.map((h, j) => (
                        <th key={j} scope="col" className="border-b border-slate-300 bg-slate-100 px-3 py-2 text-left font-semibold">
                          {inline(h, ctx, `${k}-h${j}-`)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {b.rows.map((row, r) => (
                      <tr key={r}>
                        {row.map((cell, j) => (
                          <td key={j} className="border-b border-slate-200 px-3 py-2 align-top">
                            {inline(cell, ctx, `${k}-${r}-${j}-`)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
        }
      })}
    </>
  );
}
