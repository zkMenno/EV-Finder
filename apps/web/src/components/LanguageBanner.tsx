"use client";
// Language suggestion (Decision 015): if the browser's languages (navigator.languages, the same
// list as Accept-Language) prefer another language this country serves, a small dismissible
// banner offers it. Never redirects; the URL's language always wins. Dismissal is remembered.
import { useEffect, useMemo, useState } from "react";
import { LANG_NAMES, rememberLang } from "@/components/Switchers";
import type { CountrySlug, Lang } from "@/config/countries";
import { makeT, type Dict } from "@/i18n/t";
import { suggestLang } from "@/lib/lang";
import { swapLang } from "@/lib/site-paths";
import { readStorage, writeStorage } from "@/lib/storage";

export const BANNER_KEY = "ev.langBanner.dismissed";

/**
 * `offers`: the "also available in …" line in each served language, so the suggestion is written
 * in the language it offers (the reader may not read the current one).
 */
export function LanguageBanner({
  country,
  lang,
  served,
  dict,
  offers,
}: {
  country: CountrySlug;
  lang: Lang;
  served: readonly Lang[];
  dict: Dict;
  offers: Partial<Record<Lang, string>>;
}) {
  const t = useMemo(() => makeT(dict), [dict]);
  const [suggest, setSuggest] = useState<Lang | null>(null);

  useEffect(() => {
    if (readStorage(BANNER_KEY) === "1") return;
    const s = suggestLang(navigator.languages ?? [navigator.language], served, lang);
    // Reading the browser's languages is only possible after hydration.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (s) setSuggest(s);
  }, [country, lang, served]);

  if (!suggest) return null;
  const href = swapLang(window.location.pathname, window.location.search, suggest);
  return (
    <div
      role="region"
      aria-label={t("banner.lang.label")}
      data-testid="lang-banner"
      className="border-b border-slate-300 bg-slate-50 print:hidden"
    >
      <p className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-3 gap-y-1 px-4 py-2 text-sm">
        <span lang={suggest}>
          <a
            href={href}
            onClick={() => rememberLang(suggest)}
            className="font-medium text-blue-800 underline underline-offset-2 hover:text-blue-950"
            hrefLang={suggest}
          >
            {(offers[suggest] ?? t("banner.lang.offer")).replace("{language}", LANG_NAMES[suggest])}
          </a>
        </span>
        <button
          type="button"
          className="ml-auto rounded border border-slate-400 px-2 py-0.5 text-xs hover:border-slate-600"
          onClick={() => {
            writeStorage(BANNER_KEY, "1");
            setSuggest(null);
          }}
        >
          {t("banner.lang.dismiss")}
        </button>
      </p>
    </div>
  );
}
