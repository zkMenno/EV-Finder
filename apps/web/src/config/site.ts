// Brand config. The name is a working title (Decision 018: "EV Shortlist"), still open, so it
// lives only here (or in APP_NAME): never hard-code it in components.
export const brand = {
  name: process.env.APP_NAME ?? "EV Shortlist",
} as const;

export const siteName: string = brand.name;
