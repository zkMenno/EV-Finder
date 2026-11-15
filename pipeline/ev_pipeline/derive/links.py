"""Platforms, battery packs, voltage and taxonomy (Decision 010, provisional).

Inputs (all optional; missing files are skipped):
  data/taxonomy/{voltage_classes,chemistries,cooling_types,glossary_terms}.yaml
  data/seed/platforms.yaml, data/seed/battery_packs.yaml
  data/seed/variant_links.yaml  (variant_id or generation_id -> platform_id, battery_pack_id,
                                  voltage {nominal_v, max_v, marketing_label, switchable},
                                  charger_400v {mode, kw})

Rules:
- A variant link beats a generation link, key by key.
- Pack facts are inherited by the variant (usable_kwh -> battery_kwh_net, gross_kwh ->
  battery_kwh_gross, nominal_v/max_v -> voltage, chemistry_id, cooling_id, cell_format) unless
  the variant has its own fact. Inherited provenance says `inherited from pack <id>`.
- voltage_class_id comes from nominal_v using voltage_classes min_v <= v < max_v (data, not
  code). Without a nominal voltage: the platform's class, else 'not-disclosed' when the label
  says so, else null.
- fast_on_400v = class 400v, or charger_400v mode booster/limited with kw >= 50, or mode
  native (an 800 V car that charges at full speed on 400 V; QUESTIONS.md Q-020). Unknown -> null.
- charge_100_daily comes from the chemistry row.
- Pack and link values are hand-entered seed data: source `seed-manual`, confidence low.
- T-060 rule links (`apply_rule_links`): a variant without a pack or platform from the file
  (typically an OpenEV/KilowattApp variant, keyed by its release id) gets
  * the platform when every link of its generation names the same platform;
  * the pack when exactly one pack linked in its generation fits its own usable kWh: within
    RULE_TOLERANCE of the pack's usable kWh (gross when usable is not disclosed), and never
    above the pack's gross. No fit or 2+ fits -> no pack, and the reason is reported.
  Links in variant_links.yaml always win; the rule only fills keys they leave empty.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

NOT_DISCLOSED = "not-disclosed"
SEED_SOURCE = {
    "id": "seed-manual",
    "name": "EV Finder seed (hand-entered, unchecked)",
    "licence": "CC-BY-4.0",
}
TAXONOMY_FILES = ("voltage_classes", "chemistries", "cooling_types", "glossary_terms")
FAST_ON_400V_MIN_KW = 50.0
# T-060: same 6 % as CAPACITY_TOLERANCE in data/taxonomy/validate_taxonomy.py (variant kWh vs
# pack kWh). Packs of one generation differ by far more (e.g. MEB 58 vs 77 kWh).
RULE_TOLERANCE = 0.06
RULE_ROUNDING_KWH = 0.05  # row values are rounded to 0.1 kWh (qa.checks.ROUNDING_KWH)
NUMERIC_FIELDS = {"battery_kwh_net", "battery_kwh_gross", "voltage_nominal_v", "voltage_max_v"}

# pack key -> (row/fact field, unit)
PACK_FIELDS = {
    "usable_kwh": ("battery_kwh_net", "kWh"),
    "gross_kwh": ("battery_kwh_gross", "kWh"),
    "nominal_v": ("voltage_nominal_v", "V"),
    "max_v": ("voltage_max_v", "V"),
    "chemistry_id": ("chemistry_id", "id"),
    "cooling_id": ("cooling_id", "id"),
    "cell_format": ("cell_format", "id"),
}


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _items(data: Any, key: str) -> list[dict[str, Any]]:
    if data is None:
        return []
    if isinstance(data, list):
        return data
    for k in (key, "packs", "items", "links", "variant_links"):
        if isinstance(data.get(k), list):
            return data[k]
    return []


def _mtime(path: Path) -> date:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).date()


def _number(v: Any) -> float | None:
    if isinstance(v, bool) or not isinstance(v, int | float):
        return None
    return float(v)


@dataclass
class Links:
    taxonomy: dict[str, list[dict[str, Any]]] | None = None
    platforms: dict[str, dict[str, Any]] = field(default_factory=dict)
    packs: dict[str, dict[str, Any]] = field(default_factory=dict)
    by_variant: dict[str, dict[str, Any]] = field(default_factory=dict)
    by_generation: dict[str, dict[str, Any]] = field(default_factory=dict)
    # T-060: links derived by rule (apply_rule_links); they only fill keys the file leaves empty.
    by_rule: dict[str, dict[str, Any]] = field(default_factory=dict)
    source: dict[str, Any] = field(default_factory=lambda: dict(SEED_SOURCE))
    retrieved_at: date | None = None
    inputs: list[str] = field(default_factory=list)

    def ids(self, kind: str) -> set[str]:
        return {x["id"] for x in (self.taxonomy or {}).get(kind, [])}

    def chemistry(self, cid: str | None) -> dict[str, Any] | None:
        return next(
            (c for c in (self.taxonomy or {}).get("chemistries", []) if c["id"] == cid), None
        )

    def voltage_class(self, nominal_v: float | None) -> str | None:
        if nominal_v is None:
            return None
        for vc in (self.taxonomy or {}).get("voltage_classes", []):
            if float(vc["min_v"]) <= nominal_v < float(vc["max_v"]):
                return vc["id"]
        return None

    def link_for(self, variant_id: str, generation_id: str) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for src in (self.by_generation.get(generation_id), self.by_variant.get(variant_id)):
            for k, v in (src or {}).items():
                if k in ("variant_id", "generation_id"):
                    continue
                if isinstance(v, dict) and isinstance(merged.get(k), dict):
                    merged[k] = {**merged[k], **v}
                else:
                    merged[k] = v
        for k, v in (self.by_rule.get(variant_id) or {}).items():
            if merged.get(k) is None:
                merged[k] = v
        return merged


def load_links(data_dir: Path) -> Links:
    out = Links()
    tax_dir = data_dir / "taxonomy"
    tax: dict[str, list[dict[str, Any]]] = {}
    found = False
    for name in TAXONOMY_FILES:
        path = tax_dir / f"{name}.yaml"
        data = _load_yaml(path)
        if data is not None:
            found = True
            out.inputs.append(str(path))
        tax[name] = _items(data, name)
    out.taxonomy = tax if found else None
    dates = []
    for name, attr, key in (
        ("platforms", "platforms", "platforms"),
        ("battery_packs", "packs", "battery_packs"),
    ):
        path = data_dir / "seed" / f"{name}.yaml"
        data = _load_yaml(path)
        if data is None:
            continue
        out.inputs.append(str(path))
        dates.append(_mtime(path))
        if isinstance(data, dict) and isinstance(data.get("source"), dict):
            out.source = {
                k: data["source"][k] for k in ("id", "name", "licence") if k in data["source"]
            }
        getattr(out, attr).update({x["id"]: x for x in _items(data, key)})
    path = data_dir / "seed" / "variant_links.yaml"
    data = _load_yaml(path)
    if data is not None:
        out.inputs.append(str(path))
        dates.append(_mtime(path))
        for link in _items(data, "links"):
            if link.get("variant_id"):
                out.by_variant[link["variant_id"]] = link
            elif link.get("generation_id"):
                out.by_generation[link["generation_id"]] = link
    out.retrieved_at = max(dates) if dates else None
    return out


def pack_facts(links: Links) -> list[dict[str, Any]]:
    """Schema Facts (as dicts) for every pack value, subject_type battery_pack."""
    if links.retrieved_at is None:
        return []
    facts = []
    for pid in sorted(links.packs):
        pack = links.packs[pid]
        items = list(PACK_FIELDS.items())
        warranty = pack.get("warranty") if isinstance(pack.get("warranty"), dict) else {}
        for key, value in [(k, pack.get(k)) for k, _ in items] + [
            ("warranty_years", warranty.get("years")),
            ("warranty_km", warranty.get("km")),
        ]:
            fname_guess = PACK_FIELDS.get(key, (key, ""))[0]
            if value is None or (value == NOT_DISCLOSED and fname_guess in NUMERIC_FIELDS):
                continue  # 'not-disclosed' ids are kept as facts; numbers are simply absent
            if key.startswith("warranty_") and value == NOT_DISCLOSED:
                continue
            fname, unit = PACK_FIELDS.get(key, (key, "years" if key == "warranty_years" else "km"))
            facts.append(
                {
                    "id": f"{links.source['id']}:battery_pack/{pid}:{fname}",
                    "subject_type": "battery_pack",
                    "subject_id": pid,
                    "field": fname,
                    "value": value,
                    "unit": unit,
                    "source": links.source,
                    "source_record": f"data/seed/battery_packs.yaml#{pid}",
                    "retrieved_at": links.retrieved_at.isoformat(),
                    "confidence": "low",
                }
            )
    return facts


def _prov(links: Links, note: str, fact_ids: list[str] | None = None) -> dict[str, Any]:
    p: dict[str, Any] = {
        "source_ids": [links.source["id"]],
        "confidence": "low",
        "agreeing_sources": 1,
        "note": note,
    }
    if fact_ids:
        p["fact_ids"] = fact_ids
    return p


def inherited_for(
    links: Links,
    variant_id: str,
    generation_id: str,
    own: dict[str, Any],
) -> dict[str, Any]:
    """Values a variant gets from its links and pack. `own` = the variant's merged values
    (field -> value) which always win. Returns {numbers, labels, label_provenance}."""
    link = links.link_for(variant_id, generation_id)
    numbers: dict[str, tuple[float, dict[str, Any]]] = {}
    labels: dict[str, Any] = {}
    lprov: dict[str, dict[str, Any]] = {}

    pack_id = link.get("battery_pack_id")
    pack = links.packs.get(pack_id) if pack_id else None
    platform_id = link.get("platform_id")
    platform = links.platforms.get(platform_id) if platform_id else None
    rule_notes = link.get("rule_notes") or {}
    if pack_id:
        labels["battery_pack_id"] = pack_id
        lprov["battery_pack_id"] = _prov(
            links, rule_notes.get("battery_pack_id") or "from data/seed/variant_links.yaml"
        )
    if platform_id:
        labels["platform_id"] = platform_id
        if platform:
            labels["platform_name"] = platform.get("name")
        if "platform_id" in rule_notes:
            lprov["platform_id"] = _prov(links, rule_notes["platform_id"])
        elif cited_note(link, "platform_id"):
            lprov["platform_id"] = _prov(links, cited_note(link, "platform_id") or "")

    def take(field: str, value: Any, prov: dict[str, Any]) -> None:
        if value is None or own.get(field) is not None or field in numbers or field in labels:
            return  # own facts win, then link, then pack, then platform
        n = _number(value)
        if n is not None:
            numbers[field] = (n, prov)
        elif field not in NUMERIC_FIELDS:
            labels[field] = value
            lprov[field] = prov
        # 'not-disclosed' (or any non-number) for a numeric field: leave the number empty.

    voltage = link.get("voltage") or {}
    take("voltage_nominal_v", voltage.get("nominal_v"), _prov(links, "from variant link"))
    take("voltage_max_v", voltage.get("max_v"), _prov(links, "from variant link"))
    if pack:
        for key, (fname, _unit) in PACK_FIELDS.items():
            fid = f"{links.source['id']}:battery_pack/{pack_id}:{fname}"
            take(fname, pack.get(key), _prov(links, f"inherited from pack {pack_id}", [fid]))
    if platform and platform.get("nominal_v") is not None:
        take(
            "voltage_nominal_v",
            platform["nominal_v"],
            _prov(links, f"inherited from platform {platform_id}"),
        )

    if voltage.get("class_id"):
        # Explicit class in the link (e.g. a small "800 V" pack below 550 V nominal) wins over
        # the derived one; see the note in data/taxonomy/voltage_classes.yaml.
        labels["voltage_class_id"] = voltage["class_id"]
        note = voltage.get("class_override_note") or link.get("class_override_note")
        lprov["voltage_class_id"] = _prov(
            links, "class set in variant link" + (f": {note}" if note else "")
        )
    if voltage.get("marketing_label"):
        labels["voltage_label"] = voltage["marketing_label"]
    if voltage.get("switchable") is not None:
        labels["voltage_switchable"] = bool(voltage["switchable"])
    ch = link.get("charger_400v") or {}
    if ch.get("mode"):
        labels["charger_400v_mode"] = ch["mode"]
    if _number(ch.get("kw")) is not None:
        numbers["charger_400v_kw"] = (float(ch["kw"]), _prov(links, "from variant link"))
    return {"numbers": numbers, "labels": labels, "label_provenance": lprov}


def cited_note(link: dict[str, Any], key: str) -> str | None:
    """Provenance note for a link value cited from a public page (data/seed/README.md)."""
    c = (link.get("cited") or {}).get(key)
    if not isinstance(c, dict) or c.get("value") != link.get(key):
        return None
    return (
        f"cited in data/seed/variant_links.yaml: {c.get('source_name')}, {c.get('source_url')}"
        f" (retrieved {c.get('retrieved')}, confidence {c.get('confidence')})"
    )


def _generation_evidence(
    links: Links, generation_of: dict[str, str]
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Packs and platforms named by the file's links, per generation (rule links excluded)."""
    packs: dict[str, set[str]] = {}
    platforms: dict[str, set[str]] = {}

    def add(gid: str | None, link: dict[str, Any]) -> None:
        if not gid:
            return
        for pid in [link.get("battery_pack_id"), *(link.get("battery_pack_options") or [])]:
            if pid and pid in links.packs:
                packs.setdefault(gid, set()).add(pid)
        if link.get("platform_id") in links.platforms:
            platforms.setdefault(gid, set()).add(link["platform_id"])

    for gid, link in links.by_generation.items():
        add(gid, link)
    for vid, link in links.by_variant.items():
        add(generation_of.get(vid), link)
    return packs, platforms


def pack_fit(pack: dict[str, Any], net_kwh: float) -> float | None:
    """Relative distance of a usable-kWh value to a pack, or None when it cannot be that pack
    (above its gross, no capacity to compare, or outside RULE_TOLERANCE)."""
    usable, gross = _number(pack.get("usable_kwh")), _number(pack.get("gross_kwh"))
    if gross is not None and net_kwh > gross + RULE_ROUNDING_KWH:
        return None
    ref = usable if usable is not None else gross
    if not ref:
        return None
    dist = abs(net_kwh - ref) / ref
    return dist if dist <= RULE_TOLERANCE + 1e-9 else None


def apply_rule_links(
    links: Links, generation_of: dict[str, str], net_kwh: dict[str, float | None]
) -> list[dict[str, Any]]:
    """Fill links.by_rule (T-060) and return one coverage line per variant:
    {variant_id, generation_id, battery_pack_id, pack_via, platform_id, platform_via, reason}.
    `via` is `file` (variant_links.yaml), `rule` or None (unlinked)."""
    links.by_rule = {}
    gen_packs, gen_platforms = _generation_evidence(links, generation_of)
    report: list[dict[str, Any]] = []
    for vid in sorted(generation_of):
        gid = generation_of[vid]
        link = links.link_for(vid, gid)
        rule: dict[str, Any] = {}
        notes: dict[str, str] = {}
        reasons: list[str] = []
        pack_id, pack_via = (
            link.get("battery_pack_id"),
            "file" if link.get("battery_pack_id") else None,
        )
        plat_id, plat_via = link.get("platform_id"), "file" if link.get("platform_id") else None
        if not plat_id:
            cands = sorted(gen_platforms.get(gid, ()))
            if len(cands) == 1:
                plat_id, plat_via = cands[0], "rule"
                rule["platform_id"] = plat_id
                notes["platform_id"] = (
                    f"rule T-060: every link of generation {gid} names platform {plat_id}"
                )
            elif cands:
                reasons.append(f"platform: generation links name {len(cands)} platforms")
            else:
                reasons.append("platform: no link in this generation")
        if not pack_id:
            cands = sorted(gen_packs.get(gid, ()))
            net = net_kwh.get(vid)
            fits = []
            if net is not None:
                fits = [
                    (d, pid) for pid in cands if (d := pack_fit(links.packs[pid], net)) is not None
                ]
            if not cands:
                reasons.append("pack: no pack linked in this generation")
            elif net is None:
                reasons.append("pack: variant has no usable kWh to compare")
            elif len(fits) == 1:
                d, pack_id = fits[0]
                pack_via = "rule"
                rule["battery_pack_id"] = pack_id
                notes["battery_pack_id"] = (
                    f"rule T-060: generation {gid}; usable {net:g} kWh fits pack {pack_id}"
                    f" ({100 * d:.1f}% off, tolerance {100 * RULE_TOLERANCE:g}%)"
                )
            elif fits:
                reasons.append(
                    f"pack: usable {net:g} kWh fits {len(fits)} packs "
                    + "/".join(p for _, p in sorted(fits))
                )
            else:
                reasons.append(f"pack: usable {net:g} kWh fits none of " + "/".join(cands))
        if rule:
            rule["rule_notes"] = notes
            links.by_rule[vid] = rule
        report.append(
            {
                "variant_id": vid,
                "generation_id": gid,
                "battery_pack_id": pack_id,
                "pack_via": pack_via,
                "platform_id": plat_id,
                "platform_via": plat_via,
                "reason": "; ".join(reasons) or None,
            }
        )
    return report


def link_coverage(report: list[dict[str, Any]]) -> dict[str, Any]:
    """Counts per key (pack / platform): from the file, by rule, missing; plus unlinked rows."""
    out: dict[str, Any] = {"rows": len(report)}
    for key, via in (("battery_pack_id", "pack_via"), ("platform_id", "platform_via")):
        out[key] = {
            "file": sum(1 for r in report if r[via] == "file"),
            "rule": sum(1 for r in report if r[via] == "rule"),
            "missing": sum(1 for r in report if r[via] is None),
        }
    out["unlinked"] = [
        {k: r[k] for k in ("variant_id", "reason")}
        for r in report
        if r["pack_via"] is None or r["platform_via"] is None
    ]
    return out


def finish_voltage(links: Links, row: dict[str, Any], platform_id: str | None) -> None:
    """Derive voltage_class_id, fast_on_400v and charge_100_daily on a built row."""
    nominal = row.get("voltage_nominal_v")
    cls = row.get("voltage_class_id")  # explicit link override
    if cls is None and isinstance(nominal, int | float):
        cls = links.voltage_class(nominal)
    if cls is None:
        platform = links.platforms.get(platform_id or "")
        if platform and platform.get("voltage_class_id"):
            cls = platform["voltage_class_id"]
        elif row.get("voltage_label") == NOT_DISCLOSED:
            cls = NOT_DISCLOSED
    if cls is not None:
        row["voltage_class_id"] = cls
    mode = row.get("charger_400v_mode")
    kw = row.get("charger_400v_kw")
    fast = None
    if cls == "400v" or mode == "native":
        fast = True
    elif mode in ("booster", "limited") and kw is not None:
        fast = kw >= FAST_ON_400V_MIN_KW
    if row.get("dc_peak_kw") is None:
        # No DC figure (e.g. Zoe phase 1, smart, early 500e): never claim fast DC charging.
        fast = None
    if fast is not None:
        row["fast_on_400v"] = fast
    chem = links.chemistry(row.get("chemistry_id"))
    if chem is not None and chem.get("charge_100_daily") is not None:
        row["charge_100_daily"] = bool(chem["charge_100_daily"])


def _ship(obj: dict[str, Any], kind: str) -> dict[str, Any]:
    # Q-017 fixed: the schema now uses anyOf, so 'not-disclosed' ships as-is.
    return dict(obj)


def catalogue_parts(links: Links) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if links.taxonomy is not None:
        out["taxonomy"] = links.taxonomy
    if links.platforms:
        out["platforms"] = [_ship(links.platforms[k], "platforms") for k in sorted(links.platforms)]
    if links.packs:
        out["battery_packs"] = [_ship(links.packs[k], "battery_packs") for k in sorted(links.packs)]
    return out


def id_errors(links: Links, catalogue: dict[str, Any]) -> list[str]:
    """Every taxonomy, platform and pack id used must exist ('not-disclosed' allowed)."""
    errs: list[str] = []
    if links.taxonomy is None:
        return errs
    chem, cool, vcls = (
        links.ids("chemistries"),
        links.ids("cooling_types"),
        links.ids("voltage_classes"),
    )

    def check(where: str, value: Any, valid: set[str], kind: str) -> None:
        if value is None or value == NOT_DISCLOSED:
            return
        if value not in valid:
            errs.append(f"{where}: unknown {kind} id {value!r}")

    for p in catalogue.get("platforms", []):
        check(f"platform {p['id']}", p.get("voltage_class_id"), vcls, "voltage class")
    for p in catalogue.get("battery_packs", []):
        check(f"pack {p['id']}", p.get("chemistry_id"), chem, "chemistry")
        check(f"pack {p['id']}", p.get("cooling_id"), cool, "cooling")
    for r in catalogue.get("rows", []):
        w = f"row {r['variant_id']}"
        check(w, r.get("chemistry_id"), chem, "chemistry")
        check(w, r.get("cooling_id"), cool, "cooling")
        check(w, r.get("voltage_class_id"), vcls, "voltage class")
        check(w, r.get("platform_id"), set(links.platforms), "platform")
        check(w, r.get("battery_pack_id"), set(links.packs), "battery pack")
    return errs
