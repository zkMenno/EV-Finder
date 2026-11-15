// "Find a charger / plan a trip" block (T-026). Server component, no JS: plain text links that
// open in a new tab. Renders nothing when the country has no links (and no ABRP line is asked for).
import { hasMsgKey, type T } from "@/i18n";
import type { ChargingLink } from "@/lib/charging-links";

export function ChargingLinks({ links, abrp, t, headingLevel = 2 }: { links: ChargingLink[]; abrp?: ChargingLink; t: T; headingLevel?: 2 | 3 }) {
  if (!links.length && !abrp) return null;
  const H = headingLevel === 2 ? "h2" : "h3";
  const job = (j: string) => {
    const key = `charging.job.${j}`;
    return hasMsgKey(key) ? t(key) : null;
  };
  const item = (l: ChargingLink, testId: string, text?: string) => (
    <li key={l.id} className="flex flex-col gap-0.5 sm:flex-row sm:flex-wrap sm:items-baseline sm:gap-2">
      <a href={l.url} target={l.target} rel={l.rel} className="break-words font-medium text-blue-800 underline underline-offset-2 hover:text-blue-950" data-testid={testId}>
        {text ?? l.label}
        <span aria-hidden="true"> ↗</span>
        <span className="sr-only"> {t("charging.newTab")}</span>
      </a>
      {text ? null : job(l.job) ? <span className="text-sm text-slate-700">{job(l.job)}</span> : null}
    </li>
  );
  return (
    <section aria-labelledby="charging-links" className="mt-10 max-w-3xl rounded-md border border-slate-300 p-4 print:hidden" data-testid="charging-links">
      <H id="charging-links" className="text-lg font-semibold">
        {t("charging.title")}
      </H>
      {links.length ? (
        <>
          <p className="mt-1 text-sm text-slate-800">{t("charging.intro")}</p>
          <ul className="mt-3 flex flex-col gap-2">{links.map((l) => item(l, "charging-link"))}</ul>
        </>
      ) : null}
      {abrp ? (
        <ul className={`${links.length ? "mt-3 border-t border-slate-200 pt-3" : "mt-2"} flex flex-col gap-1`}>
          {item(abrp, "abrp-link", t("charging.abrp"))}
          <li className="text-xs text-slate-700">{t("charging.abrpNote")}</li>
        </ul>
      ) : null}
    </section>
  );
}
