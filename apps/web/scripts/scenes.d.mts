// Types for scripts/scenes.mjs (imported by the drift-guard test).
export const SRC_DIR: string;
export const OUT_DIR: string;
export const GEN_FILE: string;
export function plan(): { manifest: unknown; scenes: Record<string, Record<"day" | "night", { flat: string; layers: { file: string; depth: number }[] }>> };
export function generate(p: ReturnType<typeof plan>): string;
