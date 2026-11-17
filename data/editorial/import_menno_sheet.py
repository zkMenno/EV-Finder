"""Import Menno's "New Car" Google Sheet (xlsx export) into data/editorial/menno-picks.yaml.

Usage:  python3 -I data/editorial/import_menno_sheet.py <New Car.xlsx> [out.yaml]
        python3 -I data/editorial/import_menno_sheet.py --remap [picks.yaml]   (seed ids only, no sheet)

What it keeps: his verdicts (tier, cell colour, bold = favourite, emoji), notes, the era he put a
model in, and the EV Database car id he linked. Spec numbers from the sheet are kept under
`sheet_values` with `use: internal`: they were copied by hand from ev-database.org and Bjørn
Nyland's 1000 km sheet, so they are calibration input for the rules (rules.yaml), never published
facts (AGENTS.md data rules 1-2).

Privacy: La Centrale search links in the sheet carry his postcode and search radius
(dptCp / distance). Those parameters are stripped before anything is written.
Re-run after Menno updates the sheet; the output is fully regenerated (do not hand-edit it,
put corrections in overrides below or in the sheet).
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import openpyxl
import yaml

HERE = Path(__file__).resolve().parent
SEED = HERE.parent / "seed" / "models.yaml"

# Cell fill → verdict. Read from the sheet's own colour use (see README.md "Legend").
FILL_VERDICT = {
    "FFD9EAD3": "shortlist",  # green
    "FFFFF2CC": "consider",  # yellow
    "FFFCE5CD": "fallback",  # orange: works, but clearly behind the greens
}
GREY_FONT = "FF999999"  # greyed-out row = ruled out
EMOJI = {"😍": "love", "👍": "like", "👀": "watching", "💸": "expensive"}

# (make, model) as Menno writes them → seed model id. None = not in the seed yet.
MODEL_MAP: dict[tuple[str, str], str | None] = {
    ("xpeng", "g6"): "xpeng-g6",
    ("xpeng", "p7+"): "xpeng-p7-plus",
    ("xpeng", "p7"): "xpeng-p7",
    ("xpeng", "l03"): "xpeng-l03",
    ("xpeng", "l05"): "xpeng-l05",
    ("xpeng", "g6 refresh"): "xpeng-g6",
    ("kia", "ev6"): "kia-ev6",
    ("kia", "ev6 refresh"): "kia-ev6",
    ("kia", "ev4"): "kia-ev4",
    ("kia", "ev3"): "kia-ev3",
    ("kia", "niro"): "kia-niro-ev",
    ("kia", "niro ev"): "kia-niro-ev",
    ("kia", "e-niro"): "kia-niro-ev",
    ("kia", "niro ev ii"): "kia-niro-ev",
    ("kia", "e-soul"): "kia-soul-ev",
    ("volvo", "ex60"): "volvo-ex60",
    ("volvo", "ex50"): "volvo-ex50",
    ("volvo", "xc40 refresh"): "volvo-xc40-recharge",
    ("volvo", "xc40"): "volvo-xc40-recharge",
    ("volvo", "c40"): "volvo-ec40",
    ("volvo", "ec40"): "volvo-ec40",
    ("hyundai", "ioniq 5"): "hyundai-ioniq-5",
    ("hyundai", "ioniq 5 refresh"): "hyundai-ioniq-5",
    ("hyundai", "ioniq 6"): "hyundai-ioniq-6",
    ("hyundai", "ioniq 3"): "hyundai-ioniq-3",
    ("hyundai", "kona"): "hyundai-kona-electric",
    ("zeekr", "7gt"): "zeekr-7gt",
    ("zeekr", "7x"): "zeekr-7x",
    ("zeekr", "001"): "zeekr-001",
    ("zeekr", "x"): "zeekr-x",
    ("im motors (mg)", "im6"): "mg-im6",
    ("mg", "im6"): "mg-im6",
    ("mercedes", "cla shooting brake 250+"): "mercedes-cla",
    ("bmw", "ix3"): "bmw-ix3",
    ("audi", "a6 avant e-tron"): "audi-a6-e-tron",
    ("audi", "a2"): "audi-a2-e-tron",
    ("renault", "megane e-tech"): "renault-megane-e-tech",
    ("renault", "megane"): "renault-megane-e-tech",
    ("renault", "scenic e-tech"): "renault-scenic-e-tech",
    ("renault", "scenic"): "renault-scenic-e-tech",
    ("renault", "zoe"): "renault-zoe",
    ("renault", "4"): "renault-4-e-tech",
    ("renault", "5"): "renault-5-e-tech",
    ("mg", "mg4"): "mg-mg4",
    ("mg", "mg5"): "mg-mg5",
    ("mg", "zs ev"): "mg-zs-ev",
    ("mg", "zs ev ii"): "mg-zs-ev",
    ("mg", "marvel r"): "mg-marvel-r",
    ("škoda", "elroq 85"): "skoda-elroq",
    ("škoda", "elroq"): "skoda-elroq",
    ("skoda", "elroq"): "skoda-elroq",
    ("škoda", "enyaq"): "skoda-enyaq",
    ("skoda", "enyaq"): "skoda-enyaq",
    ("skoda", "enyaq iv 80"): "skoda-enyaq",
    ("skoda", "enyaq 85"): "skoda-enyaq",
    ("skoda", "enyaq iv 60"): "skoda-enyaq",
    ("škoda", "enyaq coupe"): "skoda-enyaq",
    ("polestar", "2"): "polestar-2",
    ("polestar", "4 suv"): "polestar-4",
    ("volkswagen", "id.7 tourer"): "volkswagen-id7",
    ("volkswagen", "id.3"): "volkswagen-id3",
    ("volkswagen", "id.3 pro"): "volkswagen-id3",
    ("volkswagen", "id.3 pro s"): "volkswagen-id3",
    ("volkswagen", "id.4"): "volkswagen-id4",
    ("volkswagen", "id.4 pro"): "volkswagen-id4",
    ("volkswagen", "id.5"): "volkswagen-id5",
    ("volkswagen", "id.5 pro"): "volkswagen-id5",
    ("id", "id.5"): "volkswagen-id5",
    ("cupra", "born"): "cupra-born",
    ("tesla", "model y"): "tesla-model-y",
    ("tesla", "model 3"): "tesla-model-3",
    ("tesla", "model s"): "tesla-model-s",
    ("opel", "ampera-e"): "opel-ampera-e",
    ("opel", "corsa-e"): "opel-corsa-e",
    ("opel", "astra"): "opel-astra-electric",
    ("opel", "astra sports tourer"): "opel-astra-electric",
    ("nissan", "leaf"): "nissan-leaf",
    ("nissan", "leaf ii"): "nissan-leaf",
    ("nissan", "ariya"): "nissan-ariya",
    ("peugeot", "e-208"): "peugeot-e-208",
    ("peugeot", "e-308"): "peugeot-e-308",
    ("peugeot", "e-308 sw"): "peugeot-e-308",
    ("ds", "ds3"): "ds-3-e-tense",
    ("citroën", "ë-c4"): "citroen-e-c4",
    ("citroën", "ë-c4 refresh"): "citroen-e-c4",
    ("ford", "mustang mach-e"): "ford-mustang-mach-e",
    ("ford", "capri"): "ford-capri",
    ("ford", "explorer"): "ford-explorer",
    ("genesis", "ev60"): "genesis-gv60",
    ("fiat", "600e"): "fiat-600e",
    ("byd", "atto 3"): "byd-atto-3",
    ("byd", "atto 3 evo"): "byd-atto-3",
    ("byd", "sealion 7"): "byd-sealion-7",
    ("smart", "#3"): "smart-3",
    ("leapmotor", "b05"): "leapmotor-b05",
    ("geely", "e5"): "geely-e5",
    ("subaru", "uncharted"): "subaru-uncharted",
    ("jaguar", "i-pace"): "jaguar-i-pace",
    ("lynk&co", "2"): "lynk-co-02",
    ("mg", "mgs5"): "mg-s5",
}
# Era tab: Menno used ".0" to stop Sheets turning "4" into a number (Renault 4, Polestar 2, Renault 5).
NAME_FIX = {"4.0": "4", "5.0": "5", "2.0": "2"}


def norm(s: object) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def strip_private(url: str | None) -> str | None:
    """Drop postcode and radius from marketplace search links (they locate Menno's home)."""
    if not url:
        return None
    parts = urlsplit(url)
    q = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k not in {"dptCp", "distance"}
    ]
    return urlunsplit(parts._replace(query=urlencode(q, safe=":%,;")))


def evdb_id(url: str | None) -> int | None:
    m = re.search(r"ev-database\.org/car/(\d+)/", url or "")
    return int(m.group(1)) if m else None


def num(v: object) -> float | None:
    if v is None or v == "" or v == "?":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    m = re.search(r"-?\d+(?:\.\d+)?", str(v).replace(",", "."))
    return float(m.group()) if m else None


def yes(v: object) -> bool | str | None:
    s = norm(v).lower()
    if s in {"yes", "y"}:
        return True
    if s in {"no", "n"}:
        return False
    return norm(v) or None


def seed_generations() -> dict[str, list[dict]]:
    d = yaml.safe_load(SEED.read_text())
    out: dict[str, list[dict]] = {}
    for mk in d["makes"]:
        for m in mk["models"]:
            out[m["id"]] = m["generations"]
    return out


GENS = seed_generations()


# Decision 058: a sheet year one year before or after every seed generation of the model
# (his reveal or order year vs our registration-based span, e.g. Elroq 2024 vs 2025) maps to
# the nearest generation (listed on stdout; the picks schema has no field for it yet). Further
# away stays unmapped.
NEAREST_YEARS = 1
NEAREST: list[str] = []


def pick_generation_noted(model_id: str | None, year: int | None) -> tuple[str | None, str | None]:
    """(generation id, None) on an exact span hit, (id, 'nearest') within NEAREST_YEARS."""
    if not model_id or not year:
        return None, None
    best = None
    for g in GENS.get(model_id, []):
        start, end = g["years"]
        if start <= year and (end is None or year <= end):
            best = g["id"]  # later generations win on overlap years
    if best:
        return best, None
    near: list[tuple[int, str]] = []
    for g in GENS.get(model_id, []):
        start, end = g["years"]
        gap = start - year if year < start else year - (end if end is not None else year)
        if 0 < gap <= NEAREST_YEARS:
            near.append((gap, g["id"]))
    if len(near) == 1 or (near and sorted(near)[0][0] < sorted(near)[1][0]):
        return sorted(near)[0][1], "nearest"
    return None, None


def pick_generation(model_id: str | None, year: int | None) -> str | None:
    return pick_generation_noted(model_id, year)[0]


def cell_style(ws, row: int) -> dict:
    a = ws.cell(row=row, column=1)
    b = ws.cell(row=row, column=2)
    fill = a.fill.fgColor.rgb if a.fill and a.fill.fill_type else None
    font = (
        a.font.color.rgb if a.font and a.font.color and isinstance(a.font.color.rgb, str) else None
    )
    verdict = "ruled_out" if font == GREY_FONT else FILL_VERDICT.get(str(fill), "unrated")
    return {"verdict": verdict, "favourite": bool(a.font.b or b.font.b)}


def split_model(raw: str) -> tuple[str, int | None, list[str]]:
    flags = [EMOJI[e] for e in EMOJI if e in raw]
    for e in EMOJI:
        raw = raw.replace(e, "")
    m = re.search(r"\((\d{4})\)", raw)
    year = int(m.group(1)) if m else None
    name = norm(re.sub(r"\(\d{4}\)", "", raw))
    name = re.sub(r"\s+long range$", "", name, flags=re.I)
    return name, year, flags


def entry_ids(make: str, model: str, year: int | None) -> dict:
    key = (make.lower(), NAME_FIX.get(model, model).lower())
    model_id = MODEL_MAP.get(key, "UNMAPPED")
    mid = None if model_id == "UNMAPPED" else model_id
    gen, how = pick_generation_noted(mid, year)
    if how:  # schema EditorialPick has no field for this yet (asked WS0); report on stdout only
        NEAREST.append(f"{make} {model} {year} -> {gen}")
    return {
        "seed_model_id": mid,
        "seed_generation_id": gen,
        "in_seed": model_id not in (None, "UNMAPPED"),
        **({"mapping": "unmapped"} if model_id == "UNMAPPED" else {}),
    }


def top_tier(ws) -> list[dict]:
    head = [norm(c.value) for c in ws[1]]
    col = {h: i for i, h in enumerate(head)}
    out, section, group = [], None, None
    for r in ws.iter_rows(min_row=2, max_row=ws.max_row):
        vals = [c.value for c in r]
        make = norm(vals[0])
        if not make:
            continue
        if not norm(vals[1]):  # section header row
            if make.upper().startswith(("COMPARE", "ALSO")):
                continue
            if "VOLT" in make.upper():
                section, group = make.title(), None
            else:
                group = make.title()
                section = section or "Primary car picks"
            continue
        name, year, flags = split_model(norm(vals[1]))
        variant_cell = r[2]
        link = variant_cell.hyperlink.target if variant_cell.hyperlink else None

        def g(h: str, vals: list = vals) -> object:
            return vals[col[h]] if h in col and col[h] < len(vals) else None

        bjorn = g("Bjorn 1000km")
        bjorn_txt = bjorn.strftime("%H:%M") if hasattr(bjorn, "strftime") else (norm(bjorn) or None)
        if bjorn_txt in {"?", ""}:
            bjorn_txt = None
        e = {
            "tab": ws.title,
            "row": r[0].row,
            "section": section or "Primary car picks",
            "group": group,
            "make": make,
            "model": name,
            "model_year": year,
            "variant": norm(vals[2]) or None,
            **entry_ids(make, name, year),
            "evdb_car_id": evdb_id(link),
            "tier": num(g("Tier")),
            **cell_style(ws, r[0].row),
            "flags": flags,
            "notes": norm(g("Notes")) or None,
            "sheet_values": {
                "use": "internal",
                "bjorn_1000km_hhmm": bjorn_txt,
                "efficiency_wh_km": num(g("Eff (Wh/km)")),
                "battery_usable_kwh": num(g("Batt Usable (kWh)")),
                "voltage_v": num(g("Batt (V)")),
                "chemistry": norm(g("BatteryChem")) or None,
                "ac_kw": num(g("AC charge")),
                "range_winter_km": num(g("Range Winter (KM)")),
                "range_summer_km": num(g("Range Summer (KM)")),
                "one_stop_range_km": num(g("1-Stop Range (KM)")),
                "dc_km_per_h": num(g("DC Speed (km/h)")),
                "dc_avg_kw_10_80": num(g("DC charge 10-80% (kW)")),
                "boot_l": num(g("Boot Volume (L)")),
                "frunk_l": num(g("Frunk (L)")),
                "v2l": yes(g("V2L")),
                "v2h": yes(g("V2H")),
                "v2g": yes(g("V2G")),
            },
        }
        if ws.cell(row=r[0].row, column=1).comment:
            txt = ws.cell(row=r[0].row, column=1).comment.text
            e["comment"] = norm(txt.split("Comment:")[-1])
        out.append(e)
    return out


def eras(ws) -> list[dict]:
    out, era = [], None
    for r in ws.iter_rows(min_row=2, max_row=ws.max_row):
        make, model, var, rem = (norm(c.value) for c in r[:4])
        if not make:
            continue
        if re.search(r"\d{4}-\d{4} era", make):
            era = make.replace(" era", "")
            continue
        if not model:
            continue
        start = int(era.split("-")[0]) if era else None
        name = NAME_FIX.get(model, model)
        kwh = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*kwh", var, flags=re.I)]
        out.append(
            {
                "tab": ws.title,
                "row": r[0].row,
                "era": era,
                "make": make,
                "model": name,
                **entry_ids(make, name, start + 1 if start else None),
                "battery_options_kwh": kwh or None,
                **cell_style(ws, r[0].row),
                "remark": rem or None,
            }
        )
    return out


def used(ws) -> list[dict]:
    out, band, head = [], None, None
    for r in ws.iter_rows(min_row=1, max_row=ws.max_row):
        vals = [c.value for c in r]
        first = norm(vals[0])
        if not first:
            continue
        if "euro on La Centrale" in first or first.startswith("Models to Lease"):
            band = first
            continue
        if first == "Tier":
            head = [norm(v) for v in vals]
            continue
        if first.startswith(("http", "Analysis")) or not head or len(vals) < 3 or not norm(vals[2]):
            continue
        h = {k: vals[i] for i, k in enumerate(head) if k and i < len(vals)}
        raw = norm(h.get("Model"))
        m = re.search(r"\(([\d.]+)\s*kWh", raw)
        name = norm(re.sub(r"\(.*$", "", raw))
        make = norm(h.get("Make"))
        lc = (
            r[11].hyperlink.target
            if len(r) > 11 and r[11].hyperlink
            else (norm(vals[11]) if len(vals) > 11 else None)
        )
        out.append(
            {
                "tab": ws.title,
                "row": r[0].row,
                "price_band": band,
                "tier": first,
                "make": make,
                "model": name,
                **entry_ids(make, name, None),
                "battery_kwh": float(m.group(1)) if m else None,
                **cell_style(ws, r[0].row),
                "availability": norm(h.get("Availability")) or None,
                "pros": norm(h.get("Pros")) or None,
                "cons": norm(h.get("Cons")) or None,
                "sheet_values": {
                    "use": "internal",
                    "dc_km_per_h": num(h.get("Rapid charge")),
                    "boot_l": num(h.get("Bootspace")),
                    "range_winter_km": num(h.get("Range winter")),
                    "range_summer_km": num(h.get("Range summer")),
                    "one_pedal": norm(h.get("1-pedal")) or None,
                    "v2l_v2g": norm(h.get("V2L / V2G")) or None,
                    "ota": norm(h.get("OTA")) or None,
                    "evdb_car_id": evdb_id(norm(h.get("EVDB"))),
                    "marketplace_search": strip_private(
                        lc if lc and str(lc).startswith("http") else None
                    ),
                },
            }
        )
    return out


def _entry_year(section: str, e: dict) -> int | None:
    if section == "primary_car_picks":
        return e.get("model_year")
    if section == "eras" and e.get("era"):
        return int(str(e["era"]).split("-")[0]) + 1  # same rule as eras()
    return None


def remap(path: Path) -> None:
    """Refresh only the seed ids in an existing picks file (no sheet needed): after the seed
    or MODEL_MAP changes. Everything else in the file stays as the last full import wrote it."""
    raw = path.read_text()
    header = raw.split("\n", 1)[0] if raw.startswith("#") else ""
    doc = yaml.safe_load(raw)
    id_keys = ("seed_model_id", "seed_generation_id", "generation_match", "in_seed", "mapping")
    sections = {
        "primary_car_picks": doc["primary_car_picks"],
        "eras": doc["eras"],
        "used": doc["used_budget_bands_2025_07"]["rows"],
    }
    for section, rows in sections.items():
        for i, e in enumerate(rows):
            ids = entry_ids(e["make"], e["model"], _entry_year(section, e))
            out: dict = {}
            for k, v in e.items():
                if k in id_keys:
                    if k == "seed_model_id":
                        out.update(ids)
                    continue
                out[k] = v
            rows[i] = out
    with path.open("w") as f:
        if header:
            f.write(header + "\n")
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True, width=110)
    left = sorted(
        {f"{e['make']} {e['model']}" for rows in sections.values() for e in rows if not e["in_seed"]}
    )
    print(f"remapped {path}; not in seed: {left or 'none'}; nearest-year matches: {sorted(set(NEAREST)) or 'none'}")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--remap":
        remap(Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "menno-picks.yaml")
        return
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "menno-picks.yaml"
    wb = openpyxl.load_workbook(src)
    doc = {
        "schema": "editorial-picks/v1",
        "author": "Menno (owner)",
        "source": {
            "name": "Google Sheet 'New Car' (private)",
            "imported": date.today().isoformat(),
            "importer": "data/editorial/import_menno_sheet.py",
        },
        "scope": "Used and new EVs as a primary car with quick charging; looked at the Dutch and French used "
        "market. Availability and prices differ per country: read as direction, not as fact.",
        "licence": "CC-BY-4.0 for verdicts and notes (Menno's own words). sheet_values: internal only, never published.",
        "primary_car_picks": top_tier(wb["EVs top tier"]),
        "eras": eras(wb["OTHER EVs"]),
        "used_budget_bands_2025_07": {
            "note": "Analysis of July 2025, before the 2026 oil shock pushed used EV prices up. Price bands and "
            "availability are stale; tiers and pros/cons still show what mattered.",
            "rows": used(wb["Used EVs"]),
        },
    }
    with dst.open("w") as f:
        f.write(
            "# GENERATED by data/editorial/import_menno_sheet.py from Menno's 'New Car' sheet. Do not edit by hand.\n"
        )
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True, width=110)
    unm = [
        f"{e['make']} {e['model']}"
        for k in ("primary_car_picks", "eras")
        for e in doc[k]
        if e.get("mapping")
    ]
    unm += [
        f"{e['make']} {e['model']}"
        for e in doc["used_budget_bands_2025_07"]["rows"]
        if e.get("mapping")
    ]
    print(
        f"wrote {dst}: {len(doc['primary_car_picks'])} picks, {len(doc['eras'])} era rows, "
        f"{len(doc['used_budget_bands_2025_07']['rows'])} used rows; unmapped: {sorted(set(unm)) or 'none'}"
    )


if __name__ == "__main__":
    main()
