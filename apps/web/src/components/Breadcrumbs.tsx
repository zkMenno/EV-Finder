// Breadcrumb trail. Server component; the last item is the current page.
import Link from "next/link";

export interface Crumb {
  label: string;
  href?: string;
}

export function Breadcrumbs({ items, label }: { items: Crumb[]; label: string }) {
  return (
    <nav aria-label={label} className="mb-4 text-sm print:hidden">
      <ol className="flex flex-wrap items-center gap-x-1 gap-y-1 text-slate-700">
        {items.map((c, i) => {
          const last = i === items.length - 1;
          return (
            <li key={`${i}-${c.label}`} className="flex items-center gap-1">
              {c.href && !last ? (
                <Link href={c.href} className="text-blue-800 underline underline-offset-2 hover:text-blue-950">
                  {c.label}
                </Link>
              ) : (
                <span aria-current={last ? "page" : undefined} className={last ? "font-medium text-slate-900" : undefined}>
                  {c.label}
                </span>
              )}
              {last ? null : (
                <span aria-hidden="true" className="text-slate-500">
                  ›
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
