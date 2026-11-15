// About / credits page: what the site is, how the numbers are made, the licences, and the
// credits generated from the current release's `sources` array (src/lib/credits.ts).
// Server component; nothing here reaches the client bundle.
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { isCountrySlug, isServed } from "@/config/countries";
import { siteName } from "@/config/site";
import { getT, type MsgKey } from "@/i18n";
import { credits, linkParts } from "@/lib/credits";
import { pageCtx, pageMeta, servedRoute } from "../ev/_lib/context";

type Props = { params: Promise<{ country: string; lang: string }> };

/** Real-world range fallback rungs, best evidence first (labels: `rung.<id>`). */
const RUNGS = ["owner-data", "exact-test", "sibling-variant", "brand-body-drivetrain-ratio", "body-ratio"] as const;

const AGPL = "https://www.gnu.org/licenses/agpl-3.0.html";
const CC_BY = "https://creativecommons.org/licenses/by/4.0/";
const linkCls = "text-blue-800 underline underline-offset-2 hover:text-blue-950";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const route = servedRoute(await params);
  if (!route) return {};
  return pageMeta(route, "about", { title: getT(route.lang)("about.title", { app: siteName }) });
}

function Linked({ text }: { text: string }) {
  return (
    <>
      {linkParts(text).map((p, i) =>
        p.href ? (
          <a key={i} href={p.href} rel="noopener" className={`${linkCls} break-all`}>
            {p.text}
          </a>
        ) : (
          <span key={i}>{p.text}</span>
        ),
      )}
    </>
  );
}

export default async function AboutPage({ params }: Props) {
  const { country, lang } = await params;
  if (!isCountrySlug(country) || !isServed(country, lang)) notFound();
  const ctx = pageCtx(country, lang);
  const { base } = ctx;
  const { t, cat, labels } = ctx;
  const app = siteName;
  const release = { n: cat.origin() === "fixture" ? "dev" : cat.release(), date: ctx.asOf };
  const list = credits(cat.sources());

  return (
    <>
      <Breadcrumbs label={t("crumb.label")} items={[{ label: t("crumb.home"), href: base }, { label: t("about.title", { app }) }]} />
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{t("about.title", { app })}</h1>
      <p className="mt-2 max-w-3xl text-slate-800">{t("about.intro", { app })}</p>

      <div className="mt-6 flex max-w-3xl flex-col gap-8 text-slate-900">
        <section aria-labelledby="about-what">
          <h2 id="about-what" className="text-xl font-semibold">
            {t("about.what.title", { app })}
          </h2>
          <p className="mt-2">{t("about.what.body", { app })}</p>
          <p className="mt-2">{t("about.what.links")}</p>
        </section>

        <section aria-labelledby="about-numbers">
          <h2 id="about-numbers" className="text-xl font-semibold">
            {t("about.numbers.title")}
          </h2>
          <p className="mt-2">{t("about.numbers.sources")}</p>
          <p className="mt-2">
            {t("about.numbers.confidence", {
              agree: labels.agree.replace("{n}", "2"),
              one: labels.oneSource,
              estimate: labels.estimate,
              claim: labels.claim,
            })}
          </p>
          <p className="mt-2">{t("about.numbers.estimates")}</p>
          <p className="mt-2">{t("about.numbers.rungs")}</p>
          <ol className="mt-1 list-decimal pl-6">
            {RUNGS.map((r) => (
              <li key={r}>{t(`rung.${r}` as MsgKey)}</li>
            ))}
          </ol>
          <p className="mt-2">{t("about.numbers.missing")}</p>
        </section>

        <section aria-labelledby="about-licences">
          <h2 id="about-licences" className="text-xl font-semibold">
            {t("about.licences.title")}
          </h2>
          <p className="mt-2">
            <a href={AGPL} rel="noopener" className={linkCls}>
              {t("about.licences.code")}
            </a>
          </p>
          <p className="mt-2">
            <a href={CC_BY} rel="noopener" className={linkCls}>
              {t("about.licences.data", { app, n: release.n, date: release.date })}
            </a>
          </p>
          <p className="mt-2">{t("about.licences.third")}</p>
        </section>
      </div>

      <section aria-labelledby="about-credits" className="mt-8" data-testid="credits">
        <h2 id="about-credits" className="text-xl font-semibold">
          {t("about.credits.title")}
        </h2>
        <p className="mt-2 max-w-3xl text-slate-800">{t("about.credits.intro", { n: release.n, date: release.date })}</p>
        {cat.origin() === "fixture" ? <p className="mt-2 max-w-3xl font-medium text-amber-900">{t("footer.fixture")}</p> : null}
        {list.length ? (
          <div className="relative mt-3 overflow-x-auto rounded-md border border-slate-300" tabIndex={0} role="region" aria-labelledby="about-credits">
            <table className="min-w-full border-collapse text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th scope="col" className="px-3 py-2 text-left font-semibold">
                    {t("about.credits.source")}
                  </th>
                  <th scope="col" className="px-3 py-2 text-left font-semibold">
                    {t("about.credits.licence")}
                  </th>
                  <th scope="col" className="px-3 py-2 text-left font-semibold">
                    {t("about.credits.attribution")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {list.map((c) => (
                  <tr key={c.id} className="border-t border-slate-200" data-source={c.id}>
                    <th scope="row" className="px-3 py-2 text-left align-top font-medium">
                      {c.url ? (
                        <a href={c.url} rel="noopener" className={linkCls}>
                          {c.name}
                        </a>
                      ) : (
                        c.name
                      )}
                      {c.owner ? <span className="block text-xs font-normal text-slate-700">{c.owner}</span> : null}
                    </th>
                    <td className="whitespace-nowrap px-3 py-2 align-top">
                      {c.licenceUrl ? (
                        <a href={c.licenceUrl} rel="noopener" className={linkCls}>
                          {c.licenceLabel}
                        </a>
                      ) : (
                        c.licenceLabel
                      )}
                    </td>
                    <td className="px-3 py-2 align-top">
                      {c.lines.map((l) => (
                        <span key={l} className="block">
                          <Linked text={l} />
                        </span>
                      ))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="mt-2">{t("about.credits.none")}</p>
        )}
      </section>
    </>
  );
}
