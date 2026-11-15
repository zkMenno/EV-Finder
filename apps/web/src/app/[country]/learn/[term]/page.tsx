// Learn pages (Decision 010): stubs rendered straight from glossary_terms. Server component, no JS.
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { isCountrySlug } from "@/config/countries";
import { getT } from "@/i18n";
import { getCatalogue } from "@/lib/catalogue";
import { requestLang } from "@/lib/request-lang";
import { loc } from "@/lib/taxonomy";

type Props = { params: Promise<{ country: string; term: string }> };

function findTerm(id: string) {
  return getCatalogue().taxonomy().glossary_terms.find((g) => g.id === id);
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { country, term } = await params;
  const g = findTerm(term);
  if (!g || !isCountrySlug(country)) return {};
  return { title: loc(g.label, await requestLang(country)) };
}

export default async function LearnPage({ params }: Props) {
  const { country, term } = await params;
  if (!isCountrySlug(country)) notFound();
  const g = findTerm(term);
  if (!g) notFound();
  const lang = await requestLang(country);
  const t = getT(lang);
  // `related` may point at glossary terms or at chemistry / cooling / voltage-class rows.
  const tax = getCatalogue().taxonomy();
  const terms = new Map(tax.glossary_terms.map((x) => [x.id, { label: x.label, href: `/${country}/learn/${x.id}` }]));
  const rows = [...tax.chemistries.map((x) => ({ x, term: "chemistry" })), ...tax.cooling_types.map((x) => ({ x, term: "cooling" })), ...tax.voltage_classes.map((x) => ({ x, term: "voltage-class" }))];
  for (const { x, term: parent } of rows) if (!terms.has(x.id)) terms.set(x.id, { label: x.label, href: `/${country}/learn/${parent}` });
  const related = (g.related ?? []).flatMap((id) => {
    const r = terms.get(id);
    return r ? [{ id, ...r }] : [];
  });

  return (
    <article className="max-w-2xl">
      <p className="mb-4 text-sm">
        <Link href={`/${country}`} className="text-blue-800 underline underline-offset-2">
          ← {t("learn.back")}
        </Link>
      </p>
      <h1 className="text-2xl font-bold tracking-tight">{loc(g.label, lang)}</h1>
      {g.technical ? <p className="text-slate-700">{loc(g.technical, lang)}</p> : null}
      <p className="mt-4 text-lg">{loc(g.short, lang)}</p>
      {g.long ? <p className="mt-4">{loc(g.long, lang)}</p> : null}
      {g.nerd_note ? (
        <section className="mt-6 rounded-md border border-slate-300 bg-slate-50 p-4">
          <h2 className="font-semibold">{t("learn.nerd")}</h2>
          <p className="mt-1 text-sm">{loc(g.nerd_note, lang)}</p>
        </section>
      ) : null}
      {related.length ? (
        <section className="mt-6">
          <h2 className="font-semibold">{t("learn.related")}</h2>
          <ul className="mt-1 list-disc pl-5">
            {related.map((r) => (
              <li key={r.id}>
                <Link href={r.href} className="text-blue-800 underline underline-offset-2">
                  {loc(r.label, lang)}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </article>
  );
}
