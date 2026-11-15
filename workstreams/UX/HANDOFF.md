# UX handoff — 2026-11-15 (end of the first UX chat)

## Read first
- Project doc `claude/brand-design-decisions.md` (decisions, rejected logo ideas, the NEW solarpunk brief).
- Design system (source of truth): https://claude.ai/artifact/EiqvMW5NcFgxFq6c5YHuPP · repo mirror `docs/design/` (start at `docs/design/SOURCE.md`).
- Design board (visual companion, 9 artboards): https://claude.ai/artifact/7oaYaK26i6xQBogFuuctMp — Main (brand sheet), Icons, Elements, Textures, PhoneHome, PhoneCar, PhoneCompare, PhoneShortlist, DesktopExplore. It installs the system's tokens (`project/ds/evshortlist/tokens.json` + `designSystems` record). Keep the two in sync; Menno wants them to work together.

## State
- Palette Ink and sky (no orange), Bitter headings + logo, Atkinson body, Patrick Hand notes. Light "Day trip" / dark "Night drive".
- Working logo: one-colour sky EV with a winding tick for the V ending at a sunflower sun; tick stem 19 units (the Bitter card Menno picked — an earlier build was nearly 2× too thick). Icon: ink tile, logo within the middle 55%. "Generic but fine for now"; logo round 2 after the name is final, from Menno's references.
- Rules Menno set: never let backgrounds touch/crowd text (breathing-room rule in README); more texture (v5 textures + route divider); design system and board linked both ways.
- Design system artifact slug `6f1e71f2-2e9b-4afd-a45b-cce3bf54dd92` (last version 1794736101-5282). Board slug `3717b7c4-77a2-4b92-8796-a872f2dfa91b` (last version 1794736000-b59f). Always list_files / read before republishing.

## Next, in order
1. **Solarpunk x EV round** (Menno's brief, see project doc): optimism ("used EVs are finally good", charging is fine, be part of the transition), kids' road play-mat inspiration, road trips through nature, quiet electric exploring, rooftop solar. Approachable for people who don't care about tech or sustainability. Explore a play-mat illustration system (top-down rounded roads, houses with solar roofs, trees, wind turbines, chargers, toy-like EVs), secondary greens/solar gold, optimistic copy that says used EVs are now good at an approachable price (Menno's "350–500 km for €10–12k" was an illustration of the mood, not a line to print; specific numbers on the site come from our data), new hero + board artboards. Show options before rolling into the system; Menno dislikes generic work and wants to be involved step by step.
2. Variant finder designs for WS2 (Decision 019).
3. Visual audit of EV-media logos via Chrome (InsideEVs, EV Database, Fully Charged/Everything Electric, Electric Viking, It's Only Electric).

## Tools
`workstreams/UX/tools/` holds the Python generators used so far (board.py builds every board artboard; bitterlogo.py + logo4.py build the logo files; icons.py the icon set; textures.py the texture CSS; harness.py renders design-system previews locally with Chrome headless). They expect fonts from npm `@fontsource/*` and paths under /home/claude; adapt paths in a new session.

## Working style that worked / didn't
- Menno is on mobile: one screen, plain language, send rendered PNGs of options, ask with question popups (max 4).
- Go slower on brand work: explore → show → let him pick → refine. Don't push to the system before he approves a direction.
