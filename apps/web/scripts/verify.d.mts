// Types for the pure helpers in verify.mjs (T-126), used by src/lib/verify-map.test.ts.
export interface FeatureMap {
  defaults?: { timeout_ms?: number; always_all?: string[] };
  features: { id: string; title: string; triggers: string[]; steps: Record<string, unknown>[]; expect: Record<string, unknown>[] }[];
}
export const MAP_FILE: string;
export function globToRegExp(glob: string): RegExp;
export function expandSelector(sel: string): string;
export function selectFeatures(map: FeatureMap, changed: string[]): { features: FeatureMap["features"]; reason: string };
export function checkMap(map: unknown): string[];
export function loadMap(file?: string): FeatureMap;
export function rawKeysIn(text: string, keys: Set<string>): string[];
export function plainError(err: string, step: Record<string, unknown>): string;
