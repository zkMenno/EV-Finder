import Link from "next/link";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { CompareTray } from "@/components/CompareTray";
import { CountrySwitcher, LanguageSwitcher } from "@/components/Switchers";
import { COUNTRIES, COUNTRY_SLUGS, isCountrySlug, LANGS } from "@/config/countries";
import { siteName } from "@/config/site";
import { getDict, makeT } from "@/i18n";
import { getCatalogue } from "@/lib/catalogue";
import { requestLang } from "@/lib/request-lang";

export default async function CountryLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ country: string }>;
}) {
  const { country } = await params;
  if (!isCountrySlug(country)) notFound();
  const cfg = COUNTRIES[country];
  const lang = await requestLang(country);
  const dict = getDict(lang);
  const t = makeT(dict);
  const cat = getCatalogue();

  return (
    <>
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded focus:bg-white focus:p-2">
        {t("nav.skip")}
      </a>
      <header className="border-b border-slate-300 bg-white print:hidden">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3">
          <Link href={`/${country}`} className="text-lg font-bold tracking-tight">
            {siteName}
          </Link>
          <nav aria-label={t("nav.main")} className="flex gap-4 text-sm">
            <Link href={`/${country}`} className="font-medium hover:underline">
              {t("nav.explore")}
            </Link>
            <Link href={`/${country}/compare`} className="font-medium hover:underline">
              {t("nav.compare")}
            </Link>
          </nav>
          <div className="ml-auto flex flex-wrap items-center gap-3">
            <CountrySwitcher
              country={country}
              label={t("header.country")}
              countries={COUNTRY_SLUGS.map((c) => ({ slug: c, name: COUNTRIES[c].name }))}
            />
            <LanguageSwitcher lang={lang} label={t("header.language")} langs={LANGS} />
          </div>
        </div>
      </header>
      <main id="main" className="mx-auto max-w-7xl px-4 pb-32 pt-6">
        {children}
      </main>
      <footer className="mx-auto max-w-7xl px-4 pb-32 text-xs text-slate-700">
        <p>{t("footer.units", { currency: cfg.currency })}</p>
        <p>{cat.origin() === "fixture" ? t("footer.fixture") : t("footer.release", { n: cat.release() })}</p>
      </footer>
      <CompareTray country={country} dict={dict} />
    </>
  );
}
