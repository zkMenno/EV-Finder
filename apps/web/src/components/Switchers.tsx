"use client";
// Language and country switchers. Both keep the rest of the URL (path after the country + query).
import type { CountrySlug, Lang } from "@/config/countries";

const LANG_NAMES: Record<Lang, string> = {
  en: "English",
  nl: "Nederlands",
  de: "Deutsch",
  fr: "Français",
  es: "Español",
  it: "Italiano",
};

/** URL for the same page in another country. Exported for tests. */
export function swapCountry(pathname: string, search: string, to: string): string {
  const rest = pathname.replace(/^\/[^/]+/, "");
  return `/${to}${rest}${search}`;
}

/** URL for the same page in another language (sets ?lang=, the proxy stores the cookie). */
export function withLang(pathname: string, search: string, lang: string): string {
  const p = new URLSearchParams(search);
  p.set("lang", lang);
  return `${pathname}?${p.toString()}`;
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
          document.cookie = `lang=${next}; path=/; max-age=31536000; samesite=lax`;
          window.location.assign(withLang(window.location.pathname, window.location.search, next));
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
          window.location.assign(swapCountry(window.location.pathname, window.location.search, e.target.value));
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
