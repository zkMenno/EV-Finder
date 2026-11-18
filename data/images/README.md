# data/images

Car photos: one per generation (Decision 081, T-133). Owner: WS3. WS1 downloads and stores the files (T-134); WS2 shows them with the credit line (T-135).

| File | What |
|---|---|
| `press-terms.yaml` | Per maker: press/media terms URL, date checked, short quote, verdict (allowed / not_allowed / unclear) |
| `photos.yaml` | Per generation: chosen photo, page URL, file URL, licence (SPDX-style), author, credit line, retrieval date (T-134 contract) |
| `tools/` | How the Commons photos were found: search, rules, contact sheets, choices |

## Coverage (2026-11-17)

| | Generations | Share |
|---|---|---|
| Seed generations (all, 35 makes) | 122 | 100 % |
| With a photo | **120** | **98 %** |
| from maker press | 0 | 0 % (no maker's terms allow our use: 13 not allowed, 22 unclear) |
| from Wikimedia Commons | 120 | 98 % |
| Missing | 2 | `volvo-ex50-gen1`, `xpeng-l05-gen1` (not on sale yet; no Commons photo) |

Licences: CC BY-SA 4.0 (82), CC BY 2.0 (13), CC BY 4.0 (11), CC BY 3.0 (6), CC BY-SA 3.0 (5), CC BY-SA 3.0 DE (3).

## How the Commons photos were chosen

1. Search Commons file titles per generation (`tools/queries.json`, through the Wikidata Query Service MWAPI bridge, because the Commons API itself rate-limits our egress).
2. Rules (`tools/pick.py`): licence CC BY or CC BY-SA only (Decision 081; CC0 and public domain are left out until WS0 says otherwise); at least 1,600 px wide, landscape; no interiors, rear views, details, concepts, prototypes, race cars; a leading model year must fall inside the generation's years; photo dates before the generation started are rejected; per-generation hints and exclusions separate pre-facelift and facelift (e.g. EV6, Ioniq 5, Kona) and catch traps (XC40 Recharge T5 is a plug-in hybrid; "Honda e" vs e:Ny1).
3. A person (agent) looked at every pick on contact sheets (`tools/sheet.py`) and replaced 13 weak picks with a better candidate (`tools/choices.json`).
4. `tools/build_photos.py` writes `photos.yaml`. Credit format: `<author>, <licence>, via Wikimedia Commons` (Commons' own attribution style).

Re-run: `python3 -I data/images/tools/batch.py data/images/tools/queries.json` (≈1 query batch per minute), then `pick.py`, look at the sheets, edit `choices.json`, `build_photos.py`.

## Rules

- Never hotlink: WS1 downloads `file_url` once into our storage (T-134). Nothing here is downloaded into git (data rule 4).
- CC BY-SA photos keep their licence and are excluded from the CC BY open-data download (data rule 3).
- A maker's press photos are used only when `press-terms.yaml` says `allowed` (written permission or terms that name our use). Asking a press office is an email in Menno's name: draft only.
