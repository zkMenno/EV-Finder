"use client";
// Language and country switchers. Both keep the rest of the URL (path after /{country}/{lang} + query),
// so filters (query) and the compare tray (localStorage) survive a switch.
import type { CountrySlug, Lang } from "@/config/countries";
import { LANG_COOKIE } from "@/lib/lang";
import { swapCountry, swapLang } from "@/lib/site-paths";

export const LANG_NAMES: Record<Lang, string> = {
  en: "English",
  nl: "Nederlands",
  de: "Deutsch",
  fr: "Français",
  es: "Español",
  it: "Italiano",
};

export { swapCountry, swapLang } from "@/lib/site-paths";

/** Remembers the choice (cookie, used only where a URL has no language: `/{country}`). */
export function rememberLang(lang: string) {
  document.cookie = `${LANG_COOKIE}=${lang}; path=/; max-age=31536000; samesite=lax`;
}

const selectCls =
  "rounded-md border border-slate-400 bg-white px-2 py-1.5 text-sm text-slate-900 hover:border-slate-600";

export function LanguageSwitcher({ lang, label, langs }: { lang: Lang; label: string; langs: readonly Lang[] }) {
  return (
    <label className="flex items-center gap-2 text-sm">
      <span className="sr-only sm:not-sr-only">{label}</span>
      <select
        className={selectCls}
        value={lang}
        onChange={(e) => {
          const next = e.target.value;
          rememberLang(next);
          window.location.assign(swapLang(window.location.pathname, window.location.search, next as Lang));
        }}
      >
        {langs.map((l) => (
          <option key={l} value={l}>
            {LANG_NAMES[l]}
          </option>
        ))}
      </select>
    </label>
  );
}

export function CountrySwitcher({
  country,
  label,
  countries,
}: {
  country: CountrySlug;
  label: string;
  countries: { slug: CountrySlug; name: string }[];
}) {
  return (
    <label className="flex items-center gap-2 text-sm">
      <span className="sr-only sm:not-sr-only">{label}</span>
      <select
        className={selectCls}
        value={country}
        onChange={(e) => {
          window.location.assign(swapCountry(window.location.pathname, window.location.search, e.target.value as CountrySlug));
        }}
      >
        {countries.map((c) => (
          <option key={c.slug} value={c.slug}>
            {c.slug.toUpperCase()} · {c.name}
          </option>
        ))}
      </select>
    </label>
  );
}
