// Root layout for every public page (Decision 015): /{country}/{lang}/…. The language comes from
// the URL, never from request headers, so pages below can be statically generated and
// <html lang> is right per route. Only served pairs exist (a country's own languages + EN).
import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { CompareTray } from "@/components/CompareTray";
import { LanguageBanner } from "@/components/LanguageBanner";
import { ThemeToggle } from "@/components/ThemeToggle";
import { CountrySwitcher, LanguageSwitcher } from "@/components/Switchers";
import { COUNTRIES, COUNTRY_SLUGS, isCountrySlug, isServed, servedPairs } from "@/config/countries";
import { siteName } from "@/config/site";
import { getClientDict, getDict, makeT } from "@/i18n";
import { getCatalogue } from "@/lib/catalogue";
import { siteBase, siteUrl } from "@/lib/site-paths";
import "../../globals.css";

export const dynamicParams = false;

export function generateStaticParams() {
  return servedPairs();
}

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl()),
  title: { default: siteName, template: `%s · ${siteName}` },
  description:
    "Independent finder for new and used electric cars: real-world range, charging and prices.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

type Props = { children: ReactNode; params: Promise<{ country: string; lang: string }> };

export default async function SiteLayout({ children, params }: Props) {
  const { country, lang } = await params;
  if (!isCountrySlug(country) || !isServed(country, lang)) notFound();
  const cfg = COUNTRIES[country];
  const dict = getClientDict(lang);
  const t = makeT(dict);
  const cat = getCatalogue();
  const base = siteBase(country, lang);

  return (
    // suppressHydrationWarning: /theme-init.js may set data-theme on <html> before React hydrates.
    <html lang={lang} suppressHydrationWarning>
      <head>
        {/* Same-origin, blocking on purpose: applies the remembered theme before first paint. */}
        {/* eslint-disable-next-line @next/next/no-sync-scripts */}
        <script src="/theme-init.js" />
      </head>
      <body className="min-h-screen">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded focus:bg-white focus:p-2"
        >
          {t("nav.skip")}
        </a>
        <LanguageBanner
          country={country}
          lang={lang}
          served={cfg.served}
          dict={dict}
          offers={Object.fromEntries(cfg.served.map((l) => [l, getDict(l)["banner.lang.offer"]]))}
        />
        <header className="border-b border-slate-300 bg-white print:hidden">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3">
            <Link href={base} className="text-lg font-bold tracking-tight">
              {siteName}
            </Link>
            <nav aria-label={t("nav.main")} className="flex gap-4 text-sm">
              <Link href={base} className="font-medium hover:underline">
                {t("nav.explore")}
              </Link>
              <Link href={`${base}/top`} className="font-medium hover:underline">
                {t("nav.rankings")}
              </Link>
              <Link href={`${base}/compare`} className="font-medium hover:underline">
                {t("nav.compare")}
              </Link>
              <Link href={`${base}/learn`} className="font-medium hover:underline">
                {t("nav.learn")}
              </Link>
            </nav>
            <div className="ml-auto flex flex-wrap items-center gap-3">
              <CountrySwitcher
                country={country}
                label={t("header.country")}
                countries={COUNTRY_SLUGS.map((c) => ({ slug: c, name: COUNTRIES[c].name }))}
              />
              <LanguageSwitcher lang={lang} label={t("header.language")} langs={cfg.served} />
              <ThemeToggle label={t("theme.night")} help={t("theme.help")} />
            </div>
          </div>
        </header>
        <main id="main" className="mx-auto max-w-7xl px-4 pb-32 pt-6">
          {children}
        </main>
        <footer className="mx-auto max-w-7xl px-4 pb-32 text-xs text-slate-700">
          <p>{t("footer.units", { currency: cfg.currency })}</p>
          <p>
            {cat.origin() === "fixture"
              ? t("footer.fixture")
              : t("footer.release", { n: cat.release() })}
          </p>
          <p className="mt-1">
            <Link
              href={`${base}/about`}
              className="text-blue-800 underline underline-offset-2 hover:text-blue-950"
              data-testid="footer-about"
            >
              {t("footer.about")}
            </Link>
            {" · "}
            <Link href={`${base}/data`} className="text-blue-800 underline underline-offset-2 hover:text-blue-950" data-testid="footer-data">
              {t("footer.data")}
            </Link>
          </p>
        </footer>
        <CompareTray base={base} dict={dict} />
      </body>
    </html>
  );
}
