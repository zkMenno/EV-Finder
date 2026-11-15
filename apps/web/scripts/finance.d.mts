export const FINANCE_FILE: string;
export const OUT_FILE: string;
export const COUNTRY_CODES: string[];
export const PRODUCT: string;
export function validateFinance(doc: unknown): Record<string, unknown>;
export function loadFinance(file?: string): Record<string, unknown>;
export function serialize(config: unknown): string;
