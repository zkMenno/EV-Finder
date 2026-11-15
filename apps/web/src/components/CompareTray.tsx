"use client";
// Compare tray: lives in the country layout so it shows on every page. State is in
// localStorage (compare-store), so it survives navigation and reloads.
import Link from "next/link";
import { useMemo } from "react";
import { makeT, type Dict } from "@/i18n/t";
import { COMPARE_MAX, compareHref, compareStore } from "@/lib/compare-store";
import { useListStore } from "@/lib/use-list-store";

/** `base` = "/{country}/{lang}". */
export function CompareTray({ base, dict }: { base: string; dict: Dict }) {
  const t = useMemo(() => makeT(dict), [dict]);
  const items = useListStore(compareStore);
  if (!items.length) return null;

  return (
    <section
      aria-label={t("compare.tray")}
      data-testid="compare-tray"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-slate-300 bg-white/95 shadow-[0_-4px_12px_rgba(0,0,0,0.08)] backdrop-blur print:hidden"
    >
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-2 px-4 py-3">
        <h2 className="mr-2 text-sm font-semibold">
          {t("compare.tray")}{" "}
          <span className="font-normal text-slate-700" data-testid="compare-count">
            ({t("compare.count", { n: items.length, max: COMPARE_MAX })})
          </span>
        </h2>
        <ul className="flex flex-1 flex-wrap gap-2">
          {items.map((i) => (
            <li key={i.id} className="flex items-center gap-1 rounded-full border border-slate-300 bg-slate-50 py-0.5 pl-3 pr-1 text-sm">
              <span>{i.label}</span>
              <button
                type="button"
                onClick={() => compareStore.remove(i.id)}
                aria-label={t("compare.removeLabel", { name: i.label })}
                className="grid h-7 w-7 place-items-center rounded-full text-slate-700 hover:bg-slate-200"
              >
                <span aria-hidden="true">×</span>
              </button>
            </li>
          ))}
        </ul>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => compareStore.clear()}
            className="rounded-md px-3 py-2 text-sm text-slate-800 underline-offset-2 hover:underline"
          >
            {t("compare.clear")}
          </button>
          {items.length >= 2 ? (
            <Link
              href={compareHref(base, items)}
              className="rounded-md bg-blue-800 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-900"
            >
              {t("compare.go")} ({items.length})
            </Link>
          ) : (
            <span className="text-sm text-slate-700">{t("compare.hint")}</span>
          )}
        </div>
      </div>
    </section>
  );
}
