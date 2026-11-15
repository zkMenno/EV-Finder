"""Wikidata adapter (CC0-1.0): model items, generation items, production years, body type for
the top-40 used models in `data/seed/top40.yaml` (ADDENDUM-6 P5).

**Corroboration only.** Wikidata is edited by anyone, so its years never set a value. Every
production start/end year becomes a `kind="corroboration"` SourceRecord with *no specs*:
the year sits in `year`; our model id, the item, the boundary and the property in
`record_key` (`wikidata:volkswagen-id3/Q63636478#production_start:P571`). The matcher
skips corroboration records of sources outside `CORROBORATION_SOURCES` (counted, never
merged), so nothing here reaches a release value; `qa/top40.py` compares the years with
the seed generation boundaries.

Two SPARQL queries on query.wikidata.org (WDQS), one at a time, SLEEP_S apart, with a
descriptive User-Agent that names the repo (WDQS User-Agent policy):

1. **search**: per top-40 model, the Wikidata full-text entity search (`wikibase:mwapi`
   EntitySearch, which runs on www.wikidata.org inside WDQS) for "<make> <model>"
   (SEARCH_OVERRIDES where the display name is not a good search). Hits must be
   `instance of` car model (Q3231690). `electric` = the hit is (a subclass of) electric car
   or battery electric vehicle. The model item is the first electric hit by search rank,
   else the hit whose label equals the search string (many EV items lack the electric
   class, e.g. Audi Q4 e-tron); no such hit -> the model is reported as not found.
2. **details**: for those model items, the items linked to them as generations or
   predecessors/successors: `subclass of` / `part of the series` / `part of` the model
   (children), or the model's `replaces` / `replaced by` / `follows` / `followed by`
   (chain; kept only when its label contains the model name, so Model Y's "follows Model 3"
   is dropped). Children must be car models too (drops motors and features). For every
   item: label, year properties (START_PROPS / END_PROPS) and the `subclass of` values
   that name a body style (BODY_QIDS).

Raw JSON responses go to data/raw/wikidata/ (git-ignored) with `_fetch.json`.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import yaml

from ev_pipeline import net
from ev_pipeline.match.normalise import key
from ev_pipeline.records import SourceRecord
from ev_pipeline.schema_models import Confidence, Source
from ev_pipeline.sources import _common as c

NAME = "wikidata"
SPARQL_URL = "https://query.wikidata.org/sparql"
REPO_URL = "https://github.com/zkMenno/EV-Finder"
USER_AGENT = f"ev-finder-pipeline/0.1 ({REPO_URL}; open-data importer, corroboration only)"
SLEEP_S = 2.0
"""Pause between SPARQL requests (WDQS fair use: one query at a time)."""

SEARCH_FILE = "search.json"
DETAILS_FILE = "details.json"
TARGETS_FILE = "targets.json"

CAR_MODEL = "Q3231690"
ELECTRIC_CLASSES = ("Q193692", "Q1076882")  # electric car, battery electric vehicle

START_PROPS = {
    "P571": "inception",
    "P5204": "commercialization date",
    "P729": "service entry",
    "P580": "start time",
    "P2031": "work period (start)",
}
END_PROPS = {
    "P2669": "discontinued date",
    "P730": "service retirement",
    "P582": "end time",
    "P576": "dissolved, abolished or demolished",
    "P2032": "work period (end)",
}
# Wikidata body-style classes (`subclass of` values) -> schema Body. Each QID's English label
# was checked live on WDQS on 2026-11-15 (label in the comment). Liftback (Q1580019) is left
# out on purpose: it is neither our hatchback nor our sedan.
BODY_QIDS = {
    "Q216762": "hatchback",  # hatchback
    "Q190578": "sedan",  # sedan
    "Q192152": "suv",  # sport utility vehicle
    "Q10863152": "suv",  # compact sport utility vehicle
    "Q875600": "crossover",  # crossover
    "Q188886": "estate",  # station wagon
    "Q223189": "mpv",  # minivan
    "Q55989": "cabrio",  # convertible
}

# Search strings where "<make> <model>" from top40.yaml is not what Wikidata calls the car.
SEARCH_OVERRIDES: dict[str, str] = {
    "polestar-2": "Polestar 2",
    "mg-mg4": "MG4 EV",
    "mg-zs-ev": "MG ZS EV",
    "cupra-born": "Cupra Born",
    "opel-mokka": "Opel Mokka-e",
    "opel-corsa-e": "Opel Corsa Electric",
    "mercedes-eqb": "Mercedes-Benz EQB",
    "mini-cooper-se": "Mini Electric",
    "volvo-xc40-recharge": "Volvo XC40 Recharge",
    "citroen-e-c4": "Citroen e-C4",
    "skoda-enyaq": "Skoda Enyaq",
    "renault-megane-e-tech": "Renault Megane E-Tech Electric",
    "hyundai-kona-electric": "Hyundai Kona Electric",
    "fiat-500e": "Fiat 500e",
}

SOURCE = Source(
    id="wikidata",
    name="Wikidata",
    url="https://www.wikidata.org/",
    licence="CC0-1.0",
    attribution="Wikidata (wikidata.org), CC0.",
)


# --- targets ----------------------------------------------------------------------------


def targets_from_top40(top40: dict[str, Any], seed: dict[str, Any] | None = None) -> list[dict]:
    """One target per top-40 model: id, make and model names (seed names when in seed)."""
    names: dict[str, tuple[str, str]] = {}
    for make in (seed or {}).get("makes", []):
        for m in make.get("models", []):
            names[m["id"]] = (make["name"], m["name"])
    out = []
    for m in top40.get("models", []):
        mid = m["model_id"]
        make, model = names.get(mid, (mid.split("-", 1)[0].title(), m["name"]))
        if model.lower().startswith(make.lower() + " "):
            model = model[len(make) + 1 :]
        search = SEARCH_OVERRIDES.get(mid) or (
            model if model.lower().startswith(make.lower()) else f"{make} {model}"
        )
        out.append({"model_id": mid, "make": make, "model": model, "search": search})
    return out


# --- queries ----------------------------------------------------------------------------


def _lit(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)  # a valid SPARQL string literal


def search_query(searches: Iterable[str]) -> str:
    values = " ".join(_lit(s) for s in sorted(set(searches)))
    electric = " ".join(f"wd:{q}" for q in ELECTRIC_CLASSES)
    return f"""SELECT ?search ?item ?itemLabel ?ord ?electric WHERE {{
  VALUES ?search {{ {values} }}
  SERVICE wikibase:mwapi {{
    bd:serviceParam wikibase:endpoint "www.wikidata.org"; wikibase:api "EntitySearch";
      mwapi:search ?search; mwapi:language "en".
    ?item wikibase:apiOutputItem mwapi:item. ?ord wikibase:apiOrdinal true.
  }}
  ?item wdt:P31 wd:{CAR_MODEL} .
  BIND(EXISTS {{ VALUES ?ev {{ {electric} }} ?item wdt:P279* ?ev }} AS ?electric)
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}} ORDER BY ?search ?ord"""


def details_query(qids: Iterable[str]) -> str:
    values = " ".join(f"wd:{q}" for q in sorted(set(qids)))
    props = " ".join(f"wdt:{p}" for p in [*START_PROPS, *END_PROPS])
    return f"""SELECT ?model ?item ?itemLabel ?rel ?prop ?when ?sub WHERE {{
  {{ VALUES ?model {{ {values} }} BIND(?model AS ?item) BIND("self" AS ?rel) }}
  UNION {{ VALUES ?model {{ {values} }} ?item wdt:P279|wdt:P179|wdt:P361 ?model .
           ?item wdt:P31 wd:{CAR_MODEL} . BIND("child" AS ?rel) }}
  UNION {{ VALUES ?model {{ {values} }} ?model wdt:P1365|wdt:P1366|wdt:P155|wdt:P156 ?item .
           ?item wdt:P31 wd:{CAR_MODEL} . BIND("chain" AS ?rel) }}
  OPTIONAL {{ VALUES ?prop {{ {props} }} ?item ?prop ?when . }}
  OPTIONAL {{ ?item wdt:P279 ?sub . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}} ORDER BY ?model ?item"""


def _qid(uri: str | None) -> str:
    return (uri or "").rsplit("/", 1)[-1]


def _val(b: dict[str, Any], k: str) -> str | None:
    v = b.get(k)
    return v.get("value") if isinstance(v, dict) else None


def pick_models(targets: list[dict], search_json: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """model_id -> {qid, label, electric}: the first electric car-model hit of its search."""
    by_search: dict[str, list[tuple[int, str, str, bool]]] = {}
    for b in search_json.get("results", {}).get("bindings", []):
        s = _val(b, "search") or ""
        by_search.setdefault(s, []).append(
            (
                int(_val(b, "ord") or 0),
                _qid(_val(b, "item")),
                _val(b, "itemLabel") or "",
                (_val(b, "electric") or "") == "true",
            )
        )
    out: dict[str, dict[str, Any]] = {}
    for t in targets:
        hits = sorted(by_search.get(t["search"], []))
        hit = next((h for h in hits if h[3]), None) or next(
            (h for h in hits if key(h[2]) == key(t["search"])), None
        )
        if hit is not None:
            out[t["model_id"]] = {"qid": hit[1], "label": hit[2], "search": t["search"]}
    return out


def _sparql(client: httpx.Client, query: str) -> dict[str, Any]:
    resp = client.post(
        SPARQL_URL,
        data={"query": query},
        headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"},
    )
    resp.raise_for_status()
    return resp.json()


def fetch(client: httpx.Client, target: Path, targets: list[dict], sleep_s: float = SLEEP_S) -> int:
    """Run both queries; write targets, raw responses and `_fetch.json`. Returns detail rows."""
    target.mkdir(parents=True, exist_ok=True)
    q1 = search_query(t["search"] for t in targets)
    search_json = _sparql(client, q1)
    picked = pick_models(targets, search_json)
    if sleep_s:
        time.sleep(sleep_s)
    q2 = details_query(p["qid"] for p in picked.values())
    details_json = _sparql(client, q2) if picked else {"results": {"bindings": []}}
    for name, payload in (
        (TARGETS_FILE, {"targets": targets, "picked": picked}),
        (SEARCH_FILE, search_json),
        (DETAILS_FILE, details_json),
    ):
        (target / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    rows = len(details_json.get("results", {}).get("bindings", []))
    c.write_fetch_meta(
        target,
        {
            "url": SPARQL_URL,
            "user_agent": USER_AGENT,
            "queries": {"search": q1, "details": q2},
            "licence_seen": "CC0-1.0 (Wikidata structured data, wikidata.org/wiki/"
            "Wikidata:Licensing)",
            "targets": len(targets),
            "models_found": len(picked),
            "search_rows": len(search_json.get("results", {}).get("bindings", [])),
            "detail_rows": rows,
        },
    )
    return rows


# --- normalise --------------------------------------------------------------------------


def _year(when: str | None) -> int | None:
    if not when:
        return None
    try:
        y = int(when.lstrip("+")[:4])
    except ValueError:
        return None
    return y if 1990 <= y <= 2100 else None


def items(raw_dir: Path) -> list[dict[str, Any]]:
    """Per (model, item): label, relation, start/end years per property, body styles."""
    meta = json.loads((raw_dir / TARGETS_FILE).read_text(encoding="utf-8"))
    details = json.loads((raw_dir / DETAILS_FILE).read_text(encoding="utf-8"))
    by_qid = {p["qid"]: mid for mid, p in meta.get("picked", {}).items()}
    names = {t["model_id"]: t["model"] for t in meta.get("targets", [])}
    found: dict[tuple[str, str], dict[str, Any]] = {}
    for b in details.get("results", {}).get("bindings", []):
        model_q, item_q = _qid(_val(b, "model")), _qid(_val(b, "item"))
        mid = by_qid.get(model_q)
        if mid is None or not item_q:
            continue
        if (
            _val(b, "rel") == "chain"
            and names.get(mid)
            and key(names[mid]) not in key(_val(b, "itemLabel"))
        ):
            continue  # a neighbour in the maker's line-up, not a generation of this model
        it = found.setdefault(
            (mid, item_q),
            {
                "model_id": mid,
                "model_qid": model_q,
                "qid": item_q,
                "label": _val(b, "itemLabel") or item_q,
                "rel": _val(b, "rel") or "self",
                "start": {},
                "end": {},
                "body": set(),
            },
        )
        prop, y = _qid(_val(b, "prop")), _year(_val(b, "when"))
        if y is not None and prop in START_PROPS:
            it["start"][prop] = min(y, it["start"].get(prop, y))
        if y is not None and prop in END_PROPS:
            it["end"][prop] = max(y, it["end"].get(prop, y))
        body = BODY_QIDS.get(_qid(_val(b, "sub")))
        if body:
            it["body"].add(body)
    return sorted(found.values(), key=lambda i: (i["model_id"], i["rel"] != "self", i["qid"]))


def normalise(raw_dir: Path, retrieved_at: date) -> list[SourceRecord]:
    meta = json.loads((raw_dir / TARGETS_FILE).read_text(encoding="utf-8"))
    names = {t["model_id"]: t for t in meta.get("targets", [])}
    out: list[SourceRecord] = []
    for it in items(raw_dir):
        t = names[it["model_id"]]
        body = sorted(it["body"])[0] if len(it["body"]) == 1 else None
        for boundary, years in (("production_start", it["start"]), ("production_end", it["end"])):
            for prop, y in sorted(years.items()):
                out.append(
                    SourceRecord(
                        source=SOURCE,
                        record_key=f"wikidata:{it['model_id']}/{it['qid']}#{boundary}:{prop}",
                        kind="corroboration",
                        make=t["make"],
                        model=t["model"],
                        variant_name=it["label"],
                        year=y,
                        body=body,
                        retrieved_at=retrieved_at,
                        confidence=Confidence.low,
                    )
                )
    return out


# --- commands ---------------------------------------------------------------------------


def _load_targets() -> list[dict]:
    d = c.data_dir()
    top40 = yaml.safe_load((d / "seed" / "top40.yaml").read_text(encoding="utf-8")) or {}
    seed = yaml.safe_load((d / "seed" / "models.yaml").read_text(encoding="utf-8")) or {}
    return targets_from_top40(top40, seed)


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(NAME)
    own = client is None
    client = client or net.safe_client(NAME, timeout=90)
    try:
        targets = _load_targets()
        rows = fetch(client, target, targets)
    except (httpx.HTTPError, FileNotFoundError) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    meta = c.read_fetch_meta(target)
    c.log_step(
        step="fetch",
        source=NAME,
        input_=f"{SPARQL_URL} (2 SPARQL queries: entity search + details)",
        output=c.rel(target),
        rows_out=rows,
        targets=meta.get("targets"),
        models_found=meta.get("models_found"),
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / NAME if from_fixtures else c.raw_dir(NAME)
    if not (src / DETAILS_FILE).exists():
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    records = normalise(src, c.retrieved_at_for(src))
    out = c.staging_dir() / f"{NAME}.records.jsonl"
    rows = c.write_records(records, out)
    its = items(src)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(src),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
        items=len(its),
        items_with_years=sum(1 for i in its if i["start"] or i["end"]),
        models=len({i["model_id"] for i in its}),
        kind="corroboration (generation years; never a value)",
    )
    return 0
