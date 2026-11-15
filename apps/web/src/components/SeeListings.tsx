// "See listings" buttons: outbound deep links to marketplace searches for this country.
// Plain links (no fetching, no tracking); rel="nofollow noopener", new tab.
import type { SeeListingsLink } from "@/lib/listings";

export interface SeeListingsText {
  title: string;
  intro: string;
  newTab: string;
  unverified: string;
  none: string;
}

export function SeeListings({ links, text, headingLevel = 2 }: { links: SeeListingsLink[]; text: SeeListingsText; headingLevel?: 2 | 3 }) {
  const H = headingLevel === 2 ? "h2" : "h3";
  return (
    <section aria-labelledby="see-listings" className="rounded-md border border-slate-300 p-4 print:hidden">
      <H id="see-listings" className="text-lg font-semibold">
        {text.title}
      </H>
      {links.length ? (
        <>
          <p className="mt-1 text-sm text-slate-800">{text.intro}</p>
          <ul className="mt-3 flex flex-wrap gap-2" data-testid="see-listings">
            {links.map((l) => (
              <li key={l.id}>
                <a
                  href={l.url}
                  rel={l.rel}
                  target={l.target}
                  className="inline-flex min-h-11 items-center gap-1 rounded-md border border-blue-800 px-4 py-2 text-sm font-semibold text-blue-900 hover:bg-blue-50"
                >
                  {l.name}
                  <span aria-hidden="true">↗</span>
                  <span className="sr-only"> {text.newTab}</span>
                </a>
              </li>
            ))}
          </ul>
          {links.some((l) => !l.verified) ? <p className="mt-2 text-xs text-slate-700">{text.unverified}</p> : null}
        </>
      ) : (
        <p className="mt-1 text-sm text-slate-800">{text.none}</p>
      )}
    </section>
  );
}
