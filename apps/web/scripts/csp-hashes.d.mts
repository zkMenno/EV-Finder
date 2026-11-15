export const NEXT_DIR: string;
export const MANIFEST: string;
export function inlineScriptHashes(html: string): string[];
export function buildManifest(appDir: string): { notFound: string[]; pages: Record<string, string[]> };
export function baked404s(appDir: string): string[];
