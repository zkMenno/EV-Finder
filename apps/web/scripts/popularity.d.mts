export const TOP40_FILE: string;
export const CONFIG_FILE: string;
export const OUT_FILE: string;
export interface PopularityConfig {
  registrations: number;
  owner_picks: number;
  pick_values: Record<"shortlist" | "consider" | "fallback", number>;
  favourite_bonus: number;
}
export function parseConfig(doc: unknown): PopularityConfig;
export function registrationScores(doc: unknown): Record<string, number>;
export function pickScores(picksDoc: unknown, cfg: PopularityConfig): Record<string, number>;
export function buildPopularity(top40Doc: unknown, picksDoc: unknown, configDoc: unknown): Record<string, unknown>;
export function loadPopularity(): Record<string, unknown>;
export function serialize(x: unknown): string;
