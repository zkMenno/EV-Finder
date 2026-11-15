export const CONTENT_DIR: string;
export const OUT_FILE: string;
export function parseInline(src: string): unknown[];
export function parseBlocks(md: string): unknown[];
export function parseArticle(text: string, where: string, expect: { slug: string; lang: string }): Record<string, unknown>;
export function loadLearn(dir?: string): { articles: { slug: string; langs: string[]; files: Record<string, Record<string, unknown>> }[] };
export function serialize(config: unknown): string;
