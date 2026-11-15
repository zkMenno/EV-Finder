type Env = Record<string, string | undefined>;
export const DEV_APP_URL: string;
export function isTestBuild(env: Env): boolean;
export function resolveAppUrl(env: Env): string;
