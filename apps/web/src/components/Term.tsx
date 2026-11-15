"use client";
// Glossary terms (Decision 010): plain-language label with the technical name underneath,
// plus an ⓘ tooltip from glossary_terms linking to /[country]/[lang]/learn/[term].
import Link from "next/link";
import type { ReactNode } from "react";
import type { UiTerm } from "@/lib/taxonomy";
import { usePopover } from "./use-popover";

export interface TermText {
  /** "About {term}" — accessible name of the ⓘ button. */
  about: string;
  learnMore: string;
}

/** Label only (safe inside <label>, <legend> or a sort button). */
export function TermLabel({ term, fallback, showTechnical = true }: { term?: UiTerm; fallback: string; showTechnical?: boolean }) {
  return (
    <span className="inline-flex flex-col leading-tight">
      <span>{term?.label ?? fallback}</span>
      {showTechnical && term?.technical ? <span className="text-xs font-normal text-slate-700">{term.technical}</span> : null}
    </span>
  );
}

/** The ⓘ button + popover. Renders nothing when the glossary has no such term. */
export function InfoTip({
  label,
  children,
  href,
  text,
}: {
  label: string;
  children: ReactNode;
  href?: string;
  text: TermText;
}) {
  const { buttonProps, popoverProps } = usePopover();
  return (
    <span className="inline-flex">
      <button
        {...buttonProps}
        aria-label={text.about.replace("{term}", label)}
        className="grid h-6 w-6 shrink-0 place-items-center rounded-full text-sm font-normal text-blue-800 hover:bg-blue-50"
      >
        <span aria-hidden="true">ⓘ</span>
      </button>
      <span {...popoverProps}>
        <span className="mb-1 block font-semibold">{label}</span>
        {children}
        {href ? (
          <Link href={href} className="mt-2 block text-blue-800 underline underline-offset-2">
            {text.learnMore}
          </Link>
        ) : null}
      </span>
    </span>
  );
}

/** `base` = "/{country}/{lang}"; the ⓘ links to its learn page. */
export function TermInfo({ term, base, text }: { term?: UiTerm; base: string; text: TermText }) {
  if (!term) return null;
  return (
    <InfoTip label={term.label} href={`${base}/learn/${term.id}`} text={text}>
      <span className="block">{term.short}</span>
    </InfoTip>
  );
}

/** Label + ⓘ side by side. Don't nest inside <label> or <button>: use TermLabel + TermInfo there. */
export function Term({
  term,
  fallback,
  base,
  text,
  showTechnical = true,
}: {
  term?: UiTerm;
  fallback: string;
  base: string;
  text: TermText;
  showTechnical?: boolean;
}) {
  return (
    <span className="inline-flex items-start gap-1">
      <TermLabel term={term} fallback={fallback} showTechnical={showTechnical} />
      <TermInfo term={term} base={base} text={text} />
    </span>
  );
}
