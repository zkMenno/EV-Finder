// Types for scripts/charging-links.mjs (imported by the drift-guard test).
export interface ChargingLinkConfig {
  job: string;
  label: { en: string } & Record<string, string>;
  url: string;
  order: number;
  tool: string | null;
  official: boolean;
  utm: boolean;
  verified: boolean;
}
export function toolId(tool: string): string;
export const OUT_FILE: string;
export const MAX_LINKS: number;
export function validateChargingLinks(country: string, list: unknown): ChargingLinkConfig[];
export function loadChargingLinks(dir?: string): Record<string, ChargingLinkConfig[]>;
export function serialize(config: Record<string, ChargingLinkConfig[]>): string;
