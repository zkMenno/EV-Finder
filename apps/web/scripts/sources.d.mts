// Types for scripts/sources.mjs (imported by the drift-guard test).
export interface RegistryEntry {
  name: string;
  owner?: string;
  licence: string;
  status: string;
  url?: string;
  attribution?: string;
}
export const SOURCES_FILE: string;
export const OUT_FILE: string;
export function attributionOf(entry: Record<string, unknown>): string | undefined;
export function buildRegistry(doc: unknown): Record<string, RegistryEntry>;
export function loadRegistry(file?: string): Record<string, RegistryEntry>;
export function serialize(registry: Record<string, RegistryEntry>): string;
