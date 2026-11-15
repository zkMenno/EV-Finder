// The client-safe half of i18n: types, interpolation and makeT, with no dictionary imports.
// Client components import from "@/i18n/t" so the six JSON dictionaries stay out of the browser
// bundle (they arrive as the `dict` prop instead); "@/i18n" re-exports all of this for servers.
export type MsgKey = keyof typeof import("./en.json");
export type Dict = Record<MsgKey, string>;
export type Vars = Record<string, string | number>;
export type T = (key: MsgKey, vars?: Vars) => string;

export function interpolate(s: string, vars?: Vars): string {
  if (!vars) return s;
  return s.replace(/\{(\w+)\}/g, (m, k: string) => (k in vars ? String(vars[k]) : m));
}

export function makeT(dict: Dict): T {
  return (key, vars) => interpolate(dict[key] ?? key, vars);
}
