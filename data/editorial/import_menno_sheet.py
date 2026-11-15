"""Import Menno's "New Car" Google Sheet (xlsx export) into data/editorial/menno-picks.yaml.

Usage:  python3 -I data/editorial/import_menno_sheet.py <New Car.xlsx> [out.yaml]

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
    ("xpeng", "g6"): None,
    ("xpeng", "p7+"): None,
    ("xpeng", "p7"): None,
    ("xpeng", "l03"): None,
    ("xpeng", "l05"): None,
    ("xpeng", "g6 refresh"): None,
    ("kia", "ev6"): "kia-ev6",
    ("kia", "ev6 refresh"): "kia-ev6",
    ("kia", "ev4"): None,
    ("kia", "ev3"): "kia-ev3",
    ("kia", "niro"): "kia-niro-ev",
    ("kia", "niro ev"): "kia-niro-ev",
    ("kia", "e-niro"): "kia-niro-ev",
    ("kia", "niro ev ii"): "kia-niro-ev",
    ("kia", "e-soul"): "kia-soul-ev",
    ("volvo", "ex60"): None,
    ("volvo", "ex50"): None,
    ("volvo", "xc40 refresh"): "volvo-xc40-recharge",
    ("volvo", "xc40"): "volvo-xc40-recharge",
    ("volvo", "c40"): None,
    ("volvo", "ec40"): None,
    ("hyundai", "ioniq 5"): "hyundai-ioniq-5",
    ("hyundai", "ioniq 5 refresh"): "hyundai-ioniq-5",
    ("hyundai", "ioniq 6"): "hyundai-ioniq-6",
    ("hyundai", "ioniq 3"): None,
    ("hyundai", "kona"): "hyundai-kona-electric",
    ("zeekr", "7gt"): None,
    ("zeekr", "7x"): None,
    ("zeekr", "001"): None,
    ("zeekr", "x"): None,
    ("im motors (mg)", "im6"): None,
    ("mg", "im6"): None,
    ("mercedes", "cla shooting brake 250+"): "mercedes-cla",
    ("bmw", "ix3"): "bmw-ix3",
    ("audi", "a6 avant e-tron"): "audi-a6-e-tron",
    ("audi", "a2"): None,
    ("renault", "megane e-tech"): "renault-megane-e-tech",
    ("renault", "megane"): "renault-megane-e-tech",
    ("renault", "scenic e-tech"): "renault-scenic-e-tech",
    ("renault", "scenic"): "renault-scenic-e-tech",
    ("renault", "zoe"): "renault-zoe",
    ("renault", "4"): None,
    ("renault", "5"): "renault-5-e-tech",
    ("mg", "mg4"): "mg-mg4",
    ("mg", "mg5"): None,
    ("mg", "zs ev"): "mg-zs-ev",
    ("mg", "zs ev ii"): "mg-zs-ev",
    ("mg", "marvel r"): None,
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
    ("polestar", "4 suv"): None,
    ("volkswagen", "id.7 tourer"): "volkswagen-id7",
    ("volkswagen", "id.3"): "volkswagen-id3",
    ("volkswagen", "id.3 pro"): "volkswagen-id3",
    ("volkswagen", "id.3 pro s"): "volkswagen-id3",
    ("volkswagen", "id.4"): "volkswagen-id4",
    ("volkswagen", "id.4 pro"): "volkswagen-id4",
    ("volkswagen", "id.5"): None,
    ("volkswagen", "id.5 pro"): None,
    ("id", "id.5"): None,
    ("cupra", "born"): "cupra-born",
    ("tesla", "model y"): "tesla-model-y",
    ("tesla", "model 3"): "tesla-model-3",
    ("tesla", "model s"): "tesla-model-s",
    ("opel", "ampera-e"): None,
    ("opel", "corsa-e"): "opel-corsa-e",
    ("opel", "astra"): None,
    ("opel", "astra sports tourer"): None,
    ("nissan", "leaf"): "nissan-leaf",
    ("nissan", "leaf ii"): "nissan-leaf",
    ("nissan", "ariya"): None,
    ("peugeot", "e-208"): "peugeot-e-208",
    ("peugeot", "e-308"): None,
    ("peugeot", "e-308 sw"): None,
    ("ds", "ds3"): None,
    ("citroën", "ë-c4"): "citroen-e-c4",
    ("citroën", "ë-c4 refresh"): "citroen-e-c4",
    ("ford", "mustang mach-e"): "ford-mustang-mach-e",
    ("ford", "capri"): None,
    ("ford", "explorer"): "ford-explorer",
    ("genesis", "ev60"): None,
    ("fiat", "600e"): None,
    ("byd", "atto 3"): "byd-atto-3",
    ("byd", "atto 3 evo"): "byd-atto-3",
    ("byd", "sealion 7"): None,
    ("smart", "#3"): None,
    ("leapmotor", "b05"): None,
    ("geely", "e5"): None,
    ("subaru", "uncharted"): None,
    ("jaguar", "i-pace"): "jaguar-i-pace",
    ("lynk&co", "2"): None,
    ("mg", "mgs5"): None,
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


def pick_generation(model_id: str | None, year: int | None) -> str | None:
    if not model_id or not year:
        return None
    best = None
    for g in GENS.get(model_id, []):
        start, end = g["years"]
        if start <= year and (end is None or year <= end):
            best = g["id"]  # later generations win on overlap years
    return best


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
    return {
        "seed_model_id": None if model_id == "UNMAPPED" else model_id,
        "seed_generation_id": pick_generation(None if model_id == "UNMAPPED" else model_id, year),
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


def main() -> None:
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
