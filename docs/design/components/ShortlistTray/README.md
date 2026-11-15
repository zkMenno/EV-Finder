# ShortlistTray

The docked tray that shows your shortlist as you browse; it never resets.

- One shortlist, not a separate compare basket. Every car you tick lands here, up to 12. Compare takes up to 4 at once: by default the first 4, and you pick others on the shortlist page.
- Docked above the tab bar on phones (collapsed to "Shortlist 3" with the count badge), bottom-right on desktop. `surface`, a 1.5px ink border, `radius-lg`, `shadow-lift`, the small tick-road mark at the start.
- Slots show the short name and a remove button (48px hit area, aria-label naming the car).
- "Compare N cars" is primary while the tray is visible. On car pages "See listings" stays primary, so the tray button switches to secondary.
- Persists across pages and visits: on the device for anonymous users, in the account when signed in. Shareable as a link.
- A new car slides in (200ms). With reduced motion it appears in place.
