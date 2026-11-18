"""Pick one Commons photo candidate per seed generation (T-133). Writes candidates.json (top 6 each)."""
import json, re, sys, time
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import yaml
import commons

SEED = str(__import__("pathlib").Path(__file__).parents[3] / "data/seed/models.yaml")
ALLOWED = re.compile(r"^CC BY(-SA)? (2\.0|2\.5|3\.0|4\.0)( [a-z]{2})?$", re.I)
BAD = re.compile(r"\b(interior|innen\w*|cockpit|dashboard|armaturen\w*|rear|heck|back|badge|logo|emblem|wheels?|rims?|"
                 r"felgen?|engine|seats?|boot|trunk|frunk|kofferraum|charging|charger|laden|ladestation|port|lights?|"
                 r"lamps?|leuchten?|details?|steering|screen|display|key|tail\w*|crash\w*|police|polizei|taxi|wrapped|"
                 r"concept|prototype|erlk\w*|camouflage\w*|render\w*|side|seite\w*|profile|top|underbody|chassis|"
                 r"platform|battery|akku|plate|sketch|toy|lego|parade|race|racing|rally|drift|e:?-?ny1)\b|&| and | vs\.? |model car",
                 re.I)
FRONT = re.compile(r"front|vorne|\bfl\b|\bfr\b|3/4|three.quarter|frontansicht|avant", re.I)
DATES = re.compile(r"\b\d{1,2}[-./]\d{1,2}[-./]20\d\d\b|\b20\d\d[-./]\d{1,2}[-./]\d{1,2}\b|\b\d{1,2}[-./]20\d\d\b")
YEAR = re.compile(r"(?<![0-9])(20[01][0-9]|202[0-7])(?![0-9])")

# Search text overrides (Commons title wording) and extra keywords that separate generations.
Q = {
    "tesla-model-3-gen1": ('"Tesla Model 3"', None), "tesla-model-3-highland": ('"Tesla Model 3" Highland', "highland|2024|2025|2026"),
    "tesla-model-y-gen1": ('"Tesla Model Y"', None), "tesla-model-y-juniper": ('"Tesla Model Y" Juniper', "juniper|2025|2026"),
    "hyundai-kona-electric-sx2": r"electric|\bev\b",
    "tesla-model-s-gen1": ('"Tesla Model S"', None), "tesla-model-s-facelift": ('"Tesla Model S" facelift', None),
    "tesla-model-s-palladium": ('"Tesla Model S" Plaid', None),
    "renault-zoe-ph1": ('"Renault Zoe"', None), "renault-zoe-ph2": ('"Renault Zoe"', "ze50|phase 2|ph2|2020|2021|2022"),
    "renault-megane-e-tech-gen1": ('"Megane E-Tech"', None), "renault-5-e-tech-gen1": ('"Renault 5 E-Tech"', None),
    "renault-scenic-e-tech-gen1": ('"Scenic E-Tech"', None), "renault-4-e-tech-gen1": ('"Renault 4 E-Tech"', None),
    "nissan-leaf-ze0": ('"Nissan Leaf"', "ze0"), "nissan-leaf-ze1": ('"Nissan Leaf"', "ze1"),
    "nissan-leaf-gen3": ('"Nissan Leaf"', "2025|2026|third|3rd|ze2"), "nissan-ariya-gen1": ('"Nissan Ariya"', None),
    "volkswagen-e-golf-mk7": ('"e-Golf"', None), "volkswagen-e-golf-mk75": ('"e-Golf"', "facelift|7.5|2017|2018|2019|2020"),
    "volkswagen-id3-gen1": ('"Volkswagen ID.3"', None), "volkswagen-id4-gen1": ('"Volkswagen ID.4"', None),
    "volkswagen-id7-gen1": ('"Volkswagen ID.7"', None), "volkswagen-id-buzz-gen1": ('"ID. Buzz"', None),
    "volkswagen-id5-gen1": ('"Volkswagen ID.5"', None),
    "hyundai-ioniq-electric-gen1": ('"Hyundai Ioniq" Electric', "electric"), "hyundai-kona-electric-os": ('"Hyundai Kona Electric"', None),
    "hyundai-kona-electric-sx2": ('"Hyundai Kona" Electric', "sx2|2023|2024|2025|2026"),
    "hyundai-ioniq-5-gen1": ('"Hyundai Ioniq 5"', None), "hyundai-ioniq-5-facelift": ('"Hyundai Ioniq 5"', "facelift|2025|2026"),
    "hyundai-ioniq-6-gen1": ('"Hyundai Ioniq 6"', None), "hyundai-inster-gen1": ('"Hyundai Inster"', None),
    "hyundai-ioniq-3-gen1": ('"Hyundai Ioniq 3"', None),
    "kia-soul-ev-ps": ('"Kia Soul EV"', None), "kia-soul-ev-sk3": ('"Kia e-Soul"', None),
    "kia-niro-ev-de": ('"Kia e-Niro"', None), "kia-niro-ev-sg2": ('"Kia Niro EV"', "sg2|2022|2023|2024|2025"),
    "kia-ev6-gen1": ('"Kia EV6"', None), "kia-ev6-facelift": ('"Kia EV6"', "facelift|2025|2026"),
    "kia-ev3-gen1": ('"Kia EV3"', None), "kia-ev4-gen1": ('"Kia EV4"', None),
    "bmw-i3-i01": ('"BMW i3"', None), "bmw-i4-g26": ('"BMW i4"', None), "bmw-ix1-gen1": ('"BMW iX1"', None),
    "bmw-ix3-gen1": ('"BMW iX3"', "g08|2020|2021|2022|2023|2024"), "bmw-ix3-gen2": ('"BMW iX3"', "nk1|neue klasse|2025|2026"),
    "bmw-ix-gen1": ('"BMW iX" xDrive', None), "bmw-i5-gen1": ('"BMW i5"', None),
    "peugeot-e-208-p21": ('"Peugeot e-208"', None), "peugeot-e-2008-p24": ('"Peugeot e-2008"', None),
    "peugeot-e-308-gen1": ('"Peugeot e-308"', None), "opel-corsa-e-f": ('"Opel Corsa-e"', None),
    "opel-mokka-gen1": ('"Opel Mokka-e"', None), "opel-astra-electric-gen1": ('"Opel Astra" Electric', "electric"),
    "opel-ampera-e-gen1": ('"Opel Ampera-e"', None), "fiat-500e-312": ('"Fiat 500e"', "2013|2014|2015|2016|2017|2018|2019"),
    "fiat-500e-332": ('"Fiat 500e"', "2020|2021|2022|2023|2024|2025|la prima|332"), "fiat-600e-gen1": ('"Fiat 600e"', None),
    "skoda-enyaq-gen1": ('"Enyaq"', None), "skoda-elroq-gen1": ('"Elroq"', None),
    "mg-mg4-gen1": ('"MG4"', None), "mg-zs-ev-gen1": ('"MG ZS EV"', None), "mg-mg5-gen1": ('"MG5" EV', None),
    "mg-s5-gen1": ('"MG S5"', None), "mg-marvel-r-gen1": ('"Marvel R"', None), "mg-im6-gen1": ('"IM6"', None),
    "polestar-2-gen1": ('"Polestar 2"', None), "polestar-4-gen1": ('"Polestar 4"', None),
    "audi-e-tron-ge": ('"Audi e-tron" 55', None), "audi-e-tron-q8": ('"Q8 e-tron"', None),
    "audi-q4-e-tron-gen1": ('"Audi Q4"', None), "audi-q6-e-tron-gen1": ('"Audi Q6"', None),
    "audi-a6-e-tron-gen1": ('"Audi A6" e-tron', None), "audi-a2-e-tron-gen1": ('"Audi A2 e-tron"', None),
    "mercedes-eqa-h243": ('"Mercedes-Benz EQA"', None), "mercedes-eqc-n293": ('"Mercedes-Benz EQC"', None),
    "mercedes-eqb-gen1": ('"Mercedes-Benz EQB"', None), "mercedes-eqb-glb": ('"Mercedes-Benz GLB" EQ', None),
    "mercedes-cla-gen1": ('"Mercedes-Benz CLA" EQ', "2025|2026|c178|electric|eq"),
    "jaguar-i-pace-x590": ('"Jaguar I-Pace"', None), "dacia-spring-gen1": ('"Dacia Spring"', None),
    "smart-eq-fortwo-451": ('"Smart fortwo electric drive"', None), "smart-eq-fortwo-453": ('"Smart EQ fortwo"', None),
    "smart-3-gen1": ('"Smart #3"', None), "honda-e-gen1": ('"Honda e"', None),
    "mini-cooper-se-f56": ('"Mini Cooper SE"', None), "mini-cooper-se-j01": ('"Mini Cooper" J01', None),
    "cupra-born-gen1": ('"Cupra Born"', None), "cupra-tavascan-gen1": ('"Cupra Tavascan"', None),
    "byd-atto-3-gen1": ('"BYD Atto 3"', None), "byd-sealion-7-gen1": ('"BYD Sealion 7"', None),
    "volvo-xc40-recharge-gen1": ('"XC40 Recharge"', None), "volvo-xc40-recharge-ex40": ('"Volvo EX40"', None),
    "volvo-ex30-gen1": ('"Volvo EX30"', None), "volvo-ec40-c40": ('"Volvo C40"', None), "volvo-ec40-ec40": ('"Volvo EC40"', None),
    "volvo-ex60-gen1": ('"Volvo EX60"', None), "volvo-ex50-gen1": ('"Volvo EX50"', None),
    "ford-mustang-mach-e-gen1": ('"Mustang Mach-E"', None), "ford-explorer-gen1": ('"Ford Explorer" EV', "ev|electric|2024|2025"),
    "ford-puma-gen-e-gen1": ('"Puma Gen-E"', None), "ford-capri-gen1": ('"Ford Capri" 2024', "2024|2025|ev|electric"),
    "citroen-e-c4-c41": ('"Citroen e-C4"', None), "porsche-taycan-gen1": ('"Porsche Taycan"', None),
    "porsche-macan-electric-gen1": ('"Porsche Macan" Electric', "electric|ev|2024|2025|4"), "toyota-bz4x-gen1": ('"Toyota bZ4X"', None),
    "xpeng-g6-gen1": ('"Xpeng G6"', None), "xpeng-g6-facelift": ('"Xpeng G6"', "2025|2026|facelift"),
    "xpeng-p7-gen1": ('"Xpeng P7"', None), "xpeng-p7-plus-gen1": ('"Xpeng P7+"', None),
    "xpeng-l03-gen1": ('"Xpeng" L03', None), "xpeng-l05-gen1": ('"Xpeng" L05', None),
    "zeekr-001-gen1": ('"Zeekr 001"', None), "zeekr-7x-gen1": ('"Zeekr 7X"', None), "zeekr-7gt-gen1": ('"Zeekr 7GT"', None),
    "zeekr-x-gen1": ('"Zeekr X"', None), "genesis-gv60-gen1": ('"Genesis GV60"', None), "leapmotor-b05-gen1": ('"Leapmotor B05"', None),
    "lynk-co-02-gen1": ('"Lynk & Co 02"', None), "geely-e5-gen1": ('"Geely" E5', None), "subaru-uncharted-gen1": ('"Subaru Uncharted"', None),
    "ds-3-e-tense-crossback": ('"DS 3 Crossback"', None), "ds-3-e-tense-facelift": ('"DS 3" E-Tense', "2023|2024|facelift"),
}


REQUIRE = {
    "volvo-xc40-recharge-gen1": r"twin|p8|p6|pure electric|single motor|\bev\b|\bbev\b|elektr|electric",
    "honda-e-gen1": r"honda[ _]e(?![:\-\u05c3a-z0-9])",
    "hyundai-ioniq-5-facelift": r"^(?!.*\bN\b)",
    "hyundai-kona-electric-sx2": r"electric|\bev\b",
    "tesla-model-s-gen1": r"\b(2012|2013|2014|2015|P85|P85D|85D|70D|90D|85)\b",
}


def score(row, gen):
    t = row["title"][5:]
    req = REQUIRE.get(gen["id"])
    if req and not re.search(req, t, re.I):
        return None, "require"
    if not ALLOWED.match((row["lic"] or "").strip()):
        return None, "licence"
    try:
        w, h = int(row["w"]), int(row["h"])
    except (TypeError, ValueError):
        return None, "size"
    if w < 1600 or not (1.2 <= w / h <= 2.2):
        return None, "shape"
    if BAD.search(t.replace("Lynk & Co", "Lynk Co")):
        return None, "bad-word"
    y0, y1 = gen["years"][0], gen["years"][1] or 2026
    s = 0.0
    # A leading year ("2022 Kia EV6 ...") is a model year; any other year is a photo or show date (lower bound only).
    clean = DATES.sub(" ", t)
    phrase = re.search(r'"([^"]+)"', Q.get(gen["id"], (f'"{gen["make"]} {gen["model"]}"', None))[0]).group(1)
    clean = re.sub(re.escape(phrase.split()[-1]), " ", clean, flags=re.I)
    lead = re.match(r"\s*(20[0-2][0-9])\b", clean)
    if lead:
        my = int(lead.group(1))
        if not (y0 - 1 <= my <= y1):
            return None, "model-year"
        s += 3
    for y in (int(x) for x in YEAR.findall(clean)):
        if y < y0 - 1:
            return None, "photo-year"
    for ex in gen["exclude"]:
        if re.search(ex, t, re.I):
            return None, "other-generation"
    dto = YEAR.search(row.get("dto") or "")
    if dto and int(dto.group(1)) < y0 - 1:
        return None, "taken-before"
    hint = Q.get(gen["id"], (None, None))[1]
    if hint:
        if re.search(hint, DATES.sub(" ", t), re.I):
            s += 3
        elif gen["needs_hint"]:
            return None, "no-hint"
    if FRONT.search(t):
        s += 2
    if w >= 3000:
        s += 1
    if (row["lic"] or "").startswith(("CC BY ", "CC0", "Public")):
        s += 0.5
    return s, "ok"


def main():
    global CACHE
    CACHE = json.load(open(str(__import__("pathlib").Path(__file__).parent / "search_cache.json")))
    seed = yaml.safe_load(open(SEED))
    gens = []
    for mk in seed["makes"]:
        for mo in mk["models"]:
            for g in mo.get("generations", []):
                gens.append({"id": g["id"], "make": mk["name"], "model": mo["name"], "years": g["years"],
                             "needs_hint": False, "exclude": []})
    # When one model has several generations, the hint becomes required for the later ones.
    by_model = {}
    for g in gens:
        by_model.setdefault((g["make"], g["model"]), []).append(g)
    for lst in by_model.values():
        if len(lst) > 1:
            for g in lst[1:]:
                if Q.get(g["id"], (None, None))[1]:
                    g["needs_hint"] = True
            for g in lst:
                for o in lst:
                    h = Q.get(o["id"], (None, None))[1]
                    if o is g or not h:
                        continue
                    words = [w for w in h.split("|") if not w.isdigit()]
                    g["exclude"] += [rf"\b{re.escape(w)}\b" for w in words]
    out = {}
    for g in gens:
        q = Q.get(g["id"], (f'"{g["make"]} {g["model"]}"', None))[0]
        rows = CACHE.get(f"intitle:{q}", [])
        scored = []
        for r in rows[:400]:
            s, why = score(r, g)
            if s is not None:
                scored.append((s, r))
        scored.sort(key=lambda x: -x[0])
        out[g["id"]] = {"query": q, "n_results": len(rows), "candidates": [dict(score=s, **r) for s, r in scored[:6]]}
        best = scored[0][1]["title"] if scored else "-"
        print(f"{g['id']:<34} {len(rows):>4} {len(scored):>3}  {best}", flush=True)
    json.dump(out, open(str(__import__("pathlib").Path(__file__).parent / "candidates.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
