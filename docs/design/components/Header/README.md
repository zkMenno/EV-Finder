# Header

The site header on desktop and the bottom tab bar on phones.

- Desktop: the EV Shortlist lockup (32px tall), then Explore, Rankings, Learn, Charging. Right side: search, the detail switch, and the Shortlist button with its sunflower count badge, then sign in. The current page gets a 3px tomato underline and `aria-current="page"`.
- Phones: the lockup at 28px in a slim top bar. A 60px bottom tab bar (`evs-tabbar`) has Explore, Compare, Shortlist (a tick, with the count badge), Learn. The current tab turns its icon tomato and its label bold.
- The badge (`evs-badge`) is the sunflower disc from the logo: it always means "chosen".
- Nav items are at least 48px. Labels always visible.
- Respect safe areas on phones (`env(safe-area-inset-bottom)` under the tab bar).
