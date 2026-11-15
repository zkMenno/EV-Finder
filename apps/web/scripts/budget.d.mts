// Types for scripts/budget.mjs (imported by its unit test).
export const WEB_DIR: string;
export const JS_BUDGET_KB: number;
export const CATALOGUE_BUDGET_KB: number;
export const EXPLORE_ENTRIES: string[];
export function gzipBytes(buf: Uint8Array): number;
export function kb(bytes: number): number;
export function parseClientReferenceManifest(src: string): { entryJSFiles?: Record<string, string[]> };
export function exploreChunks(
  buildManifest: { rootMainFiles?: string[]; polyfillFiles?: string[] },
  clientManifest: { entryJSFiles?: Record<string, string[]> },
  entries?: string[],
): { modern: string[]; polyfills: string[] };
export function latestCatalogue(dir: string): string | null;
