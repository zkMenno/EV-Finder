"""Car photos per generation (T-134, Decision 081): validate, fetch once, resize, attach.

Inputs (WS3, T-133): `data/images/photos.yaml` (one photo per generation) and
`data/images/press-terms.yaml` (maker press terms, verdict per maker). See photos.py.

Flow:
1. `ev images fetch` (network, night job): every valid photo's `file_url` is downloaded once into
   `data/cache/images/<sha256(file_url)>.bin` (+ `.json` with bytes, sha256, content type).
   An original already in the cache is never fetched again. Hosts come from data/sources.yaml
   (`wikimedia-commons`, `maker-press-photos`); the SSRF guard and size cap in net.py apply.
2. The release step resizes each cached original to 400 / 800 / 1600 px wide WebP (never
   upscaled), writes them under `images/` in the release folder (published as assets, never in
   git, never hotlinked) and attaches `generations[].image` with paths, source URL, licence,
   credit and retrieval date.
3. Release QA (`check_images`) blocks a release whose image has a licence outside the allowlist
   or no credit line. Images are not part of the CC BY open data bundle (it holds variant rows
   only; tests guard that).
"""
