export const RULES_FILE: string;
export const OUT_FILE: string;
export function validateRules(doc: unknown): Record<string, unknown>;
export function loadRules(file?: string): Record<string, unknown>;
export function serialize(config: unknown): string;
