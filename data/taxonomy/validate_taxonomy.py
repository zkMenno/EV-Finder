#!/usr/bin/env python3
"""Validate the taxonomy tables and the platform / battery-pack / variant-link seed files.

Usage:
    python3 -I data/taxonomy/validate_taxonomy.py            # validate the repo files
    python3 -I data/taxonomy/validate_taxonomy.py --self-test # check the validator itself

Checks (Decision 010):
- every row validates against its JSON Schema $def in packages/schema/schemas/ev.schema.json
- ids unique per table; glossary ids do not collide with other taxonomy ids
- voltage classes are contiguous and non-overlapping
- labels have `en` and `nl`; glossary `short` has `en` and `nl` and is at most 20 words
  (every language); glossary EN is complete (technical, long with 2-4 sentences, nerd_note, related)
- cross-references resolve: pack chemistry/cooling ids, platform voltage class ids, glossary
  `related`, pack notes, and every link's variant / generation / platform / pack ids
- every seed variant has exactly one link; generations without variants get a default
- voltage class derived from nominal_v matches a stated class_id unless class_override_note is set;
  400 V-class links are `native`, 800 V+ links are not; `kw` only with booster / limited

Needs PyYAML and jsonschema (>= 4.18, for `referencing`). Exit 0 = valid, 1 = errors.
"""

from __future__ import annotations

import copy
import itertools
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SCHEMA_PATH = ROOT / "packages" / "schema" / "schemas" / "ev.schema.json"
SEED = ROOT / "data" / "seed"

TAXONOMY_FILES = {
    "voltage_classes": ("voltage_classes.yaml", "VoltageClass"),
    "chemistries": ("chemistries.yaml", "Chemistry"),
    "cooling_types": ("cooling_types.yaml", "CoolingType"),
    "glossary_terms": ("glossary_terms.yaml", "GlossaryTerm"),
}
ND = "not-disclosed"
SHORT_MAX_WORDS = 20
LONG_SENTENCES = (2, 4)
LINK_KEYS = {
    "variant_id",
    "generation_id",
    "platform_id",
    "battery_pack_id",
    "battery_pack_options",
    "voltage",
    "charger_400v",
    "uncertain",
    "notes",
    "class_override_note",
}
SEED_FILE_KEYS = {
    "platforms": {"source", "confidence", "platforms"},
    "packs": {"source", "confidence", "packs", "notes"},
    "links": {"source", "confidence", "x-anchors", "links"},
}
CAPACITY_TOLERANCE = 0.06  # 6 %: variant kWh vs pack kWh, warning only

Data = dict[str, Any]


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_all() -> Data:
    data: Data = {"taxonomy": {}}
    for key, (fname, _) in TAXONOMY_FILES.items():
        doc = load_yaml(HERE / fname) or {}
        data["taxonomy"][key] = doc.get(key, [])
        data.setdefault("taxonomy_extra_keys", {})[key] = sorted(set(doc) - {key})
    data["platforms_doc"] = load_yaml(SEED / "platforms.yaml") or {}
    data["packs_doc"] = load_yaml(SEED / "battery_packs.yaml") or {}
    data["links_doc"] = load_yaml(SEED / "variant_links.yaml") or {}
    data["variants_doc"] = load_yaml(SEED / "variants.yaml") or {}
    data["models_doc"] = load_yaml(SEED / "models.yaml") or {}
    return data


def _is_id_or_nd(branches: Any) -> bool:
    if not isinstance(branches, list) or len(branches) != 2:
        return False
    has_id = any(b == {"$ref": "#/$defs/Id"} for b in branches)
    has_nd = any(isinstance(b, dict) and b.get("const") == ND for b in branches)
    return has_id and has_nd


def patch_id_or_nd(node: Any) -> int:
    """Rewrite `oneOf: [Id, const not-disclosed]` to `anyOf` in place; return the count.

    Workaround for a schema bug: 'not-disclosed' also matches the Id pattern, so the oneOf
    matches both branches and always rejects 'not-disclosed'. Only the in-memory copy used
    here is changed; the fix belongs in packages/schema (coordinator lane).
    """
    count = 0
    if isinstance(node, dict):
        if _is_id_or_nd(node.get("oneOf")):
            node["anyOf"] = node.pop("oneOf")
            count += 1
        for v in node.values():
            count += patch_id_or_nd(v)
    elif isinstance(node, list):
        for v in node:
            count += patch_id_or_nd(v)
    return count


class Schema:
    def __init__(self, schema: dict[str, Any]) -> None:
        schema = copy.deepcopy(schema)
        self.patched = patch_id_or_nd(schema)
        self.id = schema["$id"]
        self.registry = Registry().with_resource(self.id, Resource.from_contents(schema))
        self._cache: dict[str, Draft202012Validator] = {}

    def errors(self, def_name: str, value: Any) -> list[str]:
        if def_name not in self._cache:
            self._cache[def_name] = Draft202012Validator(
                {"$ref": f"{self.id}#/$defs/{def_name}"}, registry=self.registry
            )
        out = []
        for err in self._cache[def_name].iter_errors(value):
            loc = "/".join(str(p) for p in err.absolute_path) or "(row)"
            out.append(f"{loc}: {err.message}")
        return out


def word_count(text: str) -> int:
    return len(text.split())


def sentence_count(text: str) -> int:
    # A sentence ends with . ! ? followed by whitespace + capital/quote/digit, or end of text.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(0-9])", text.strip())
    return len([p for p in parts if p.strip()])


def check(data: Data, schema: Schema) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    err = errors.append
    warn = warnings.append
    tax = data["taxonomy"]

    # --- taxonomy tables ---------------------------------------------------------------
    ids_by_table: dict[str, set[str]] = {}
    for key, (fname, def_name) in TAXONOMY_FILES.items():
        rows = tax.get(key)
        extra = data.get("taxonomy_extra_keys", {}).get(key, [])
        if extra:
            err(f"{fname}: unexpected top-level keys {extra}")
        if not isinstance(rows, list) or not rows:
            err(f"{fname}: missing or empty `{key}` list")
            ids_by_table[key] = set()
            continue
        seen: set[str] = set()
        for i, row in enumerate(rows):
            rid = row.get("id", f"#{i}") if isinstance(row, dict) else f"#{i}"
            for e in schema.errors(def_name, row):
                err(f"{fname} [{rid}] {e}")
            if not isinstance(row, dict):
                continue
            if rid in seen:
                err(f"{fname}: duplicate id {rid}")
            seen.add(rid)
            label = row.get("label", {})
            if isinstance(label, dict) and not label.get("nl"):
                err(f"{fname} [{rid}] label.nl missing")
        ids_by_table[key] = seen
    for e in schema.errors("Taxonomy", tax):
        err(f"taxonomy (combined) {e}")

    # voltage classes: contiguous, ordered, non-overlapping
    vcs = [r for r in tax.get("voltage_classes", []) if isinstance(r, dict)]
    ordered = sorted(vcs, key=lambda r: r.get("min_v", 0))
    for r in ordered:
        if r.get("min_v", 0) >= r.get("max_v", 0):
            err(f"voltage_classes.yaml [{r.get('id')}] min_v must be < max_v")
    for a, b in itertools.pairwise(ordered):
        if a.get("max_v") != b.get("min_v"):
            err(f"voltage_classes.yaml: gap or overlap between {a.get('id')} and {b.get('id')}")

    def derive_class(v: Any) -> str | None:
        if not isinstance(v, (int, float)):
            return None
        for r in ordered:
            if r["min_v"] <= v < r["max_v"]:
                return r["id"]
        return None

    # glossary specifics
    other_tax_ids = (
        ids_by_table["voltage_classes"]
        | ids_by_table["chemistries"]
        | ids_by_table["cooling_types"]
    )
    glossary_ids = ids_by_table["glossary_terms"]
    for gid in sorted(glossary_ids & other_tax_ids):
        err(f"glossary_terms.yaml: id {gid} collides with a voltage/chemistry/cooling id")
    related_ok = glossary_ids | other_tax_ids
    for row in tax.get("glossary_terms", []):
        if not isinstance(row, dict):
            continue
        gid = row.get("id")
        short = row.get("short", {})
        if isinstance(short, dict):
            if not short.get("nl"):
                err(f"glossary_terms.yaml [{gid}] short.nl missing")
            for lang, text in short.items():
                if isinstance(text, str) and word_count(text) > SHORT_MAX_WORDS:
                    err(
                        f"glossary_terms.yaml [{gid}] short.{lang} has {word_count(text)} words (max {SHORT_MAX_WORDS})"
                    )
        for field in ("technical", "long", "nerd_note"):
            if not isinstance(row.get(field), dict) or not row[field].get("en"):
                err(f"glossary_terms.yaml [{gid}] {field}.en missing (EN must be complete)")
        long_en = (row.get("long") or {}).get("en") if isinstance(row.get("long"), dict) else None
        if isinstance(long_en, str):
            n = sentence_count(long_en)
            if not LONG_SENTENCES[0] <= n <= LONG_SENTENCES[1]:
                err(
                    f"glossary_terms.yaml [{gid}] long.en has {n} sentences (want {LONG_SENTENCES[0]}-{LONG_SENTENCES[1]})"
                )
        related = row.get("related")
        if not related:
            err(f"glossary_terms.yaml [{gid}] related missing or empty")
        for rel in related or []:
            if rel == gid:
                err(f"glossary_terms.yaml [{gid}] related points to itself")
            elif rel not in related_ok:
                err(f"glossary_terms.yaml [{gid}] related id {rel!r} does not exist")

    # --- seed wrappers -------------------------------------------------------------------
    def check_wrapper(doc: Any, fname: str, kind: str) -> None:
        if not isinstance(doc, dict):
            err(f"{fname}: not a mapping")
            return
        extra = set(doc) - SEED_FILE_KEYS[kind]
        if extra:
            err(f"{fname}: unexpected top-level keys {sorted(extra)}")
        src = doc.get("source")
        if src is None:
            err(f"{fname}: missing top-level source")
        else:
            for e in schema.errors("Source", src):
                err(f"{fname} source {e}")
        if doc.get("confidence") != "low":
            err(f"{fname}: top-level confidence must be 'low' for hand-entered seed data")

    pdoc, kdoc, ldoc = data["platforms_doc"], data["packs_doc"], data["links_doc"]
    check_wrapper(pdoc, "platforms.yaml", "platforms")
    check_wrapper(kdoc, "battery_packs.yaml", "packs")
    check_wrapper(ldoc, "variant_links.yaml", "links")

    # --- platforms -----------------------------------------------------------------------
    platforms: dict[str, dict[str, Any]] = {}
    for i, row in enumerate(pdoc.get("platforms") or []):
        rid = row.get("id", f"#{i}") if isinstance(row, dict) else f"#{i}"
        for e in schema.errors("Platform", row):
            err(f"platforms.yaml [{rid}] {e}")
        if not isinstance(row, dict):
            continue
        if rid in platforms:
            err(f"platforms.yaml: duplicate id {rid}")
        platforms[rid] = row
        vc = row.get("voltage_class_id")
        if vc is not None and vc != ND and vc not in ids_by_table["voltage_classes"]:
            err(f"platforms.yaml [{rid}] voltage_class_id {vc!r} does not exist")
        derived = derive_class(row.get("nominal_v"))
        if derived and vc not in (None, ND, derived):
            err(f"platforms.yaml [{rid}] nominal_v {row['nominal_v']} implies {derived}, not {vc}")
    if not platforms:
        err("platforms.yaml: no platforms")

    # --- packs ---------------------------------------------------------------------------
    packs: dict[str, dict[str, Any]] = {}
    for i, row in enumerate(kdoc.get("packs") or []):
        rid = row.get("id", f"#{i}") if isinstance(row, dict) else f"#{i}"
        for e in schema.errors("BatteryPack", row):
            err(f"battery_packs.yaml [{rid}] {e}")
        if not isinstance(row, dict):
            continue
        if rid in packs:
            err(f"battery_packs.yaml: duplicate id {rid}")
        packs[rid] = row
        chem = row.get("chemistry_id")
        if chem is not None and chem != ND and chem not in ids_by_table["chemistries"]:
            err(f"battery_packs.yaml [{rid}] chemistry_id {chem!r} does not exist")
        cool = row.get("cooling_id")
        if cool is not None and cool != ND and cool not in ids_by_table["cooling_types"]:
            err(f"battery_packs.yaml [{rid}] cooling_id {cool!r} does not exist")
        g, u = row.get("gross_kwh"), row.get("usable_kwh")
        if isinstance(g, (int, float)) and isinstance(u, (int, float)) and u > g:
            err(f"battery_packs.yaml [{rid}] usable_kwh {u} > gross_kwh {g}")
        nv, mv = row.get("nominal_v"), row.get("max_v")
        if isinstance(nv, (int, float)) and isinstance(mv, (int, float)) and mv < nv:
            err(f"battery_packs.yaml [{rid}] max_v {mv} < nominal_v {nv}")
    notes = kdoc.get("notes") or {}
    if not isinstance(notes, dict):
        err("battery_packs.yaml: notes must be a mapping of pack id -> text")
        notes = {}
    for nid, text in notes.items():
        if nid not in packs:
            err(f"battery_packs.yaml notes: unknown pack id {nid!r}")
        if not isinstance(text, str) or not text.strip():
            err(f"battery_packs.yaml notes [{nid}] must be non-empty text")
    if not packs:
        err("battery_packs.yaml: no packs")

    # --- links ---------------------------------------------------------------------------
    variants = {
        v["id"]: v
        for v in (data["variants_doc"].get("variants") or [])
        if isinstance(v, dict) and "id" in v
    }
    generations: set[str] = set()
    for mk in data["models_doc"].get("makes") or []:
        for md in mk.get("models") or []:
            for gen in md.get("generations") or []:
                generations.add(gen["id"])
    gens_with_variants = {v.get("generation_id") for v in variants.values()}

    linked_variants: dict[str, int] = {}
    linked_gens: set[str] = set()
    used_platforms: set[str] = set()
    used_packs: set[str] = set()
    for i, link in enumerate(ldoc.get("links") or []):
        if not isinstance(link, dict):
            err(f"variant_links.yaml link #{i}: not a mapping")
            continue
        vid, gid = link.get("variant_id"), link.get("generation_id")
        tag = f"variant_links.yaml [{vid or gid or '#' + str(i)}]"
        extra = set(link) - LINK_KEYS
        if extra:
            err(f"{tag} unexpected keys {sorted(extra)}")
        if bool(vid) == bool(gid):
            err(f"{tag} needs exactly one of variant_id / generation_id")
        if vid:
            if vid not in variants:
                err(f"{tag} variant_id does not exist in variants.yaml")
            linked_variants[vid] = linked_variants.get(vid, 0) + 1
            if "battery_pack_options" in link:
                err(f"{tag} battery_pack_options is only for generation-level defaults")
            if "battery_pack_id" not in link:
                err(f"{tag} battery_pack_id missing")
        if gid:
            if gid not in generations:
                err(f"{tag} generation_id does not exist in models.yaml")
            elif gid in gens_with_variants:
                warn(
                    f"{tag} generation has seed variants; a generation default is usually not needed"
                )
            if gid in linked_gens:
                err(f"{tag} duplicate generation-level link")
            linked_gens.add(gid)
            if "battery_pack_id" not in link and not link.get("battery_pack_options"):
                err(f"{tag} needs battery_pack_id or battery_pack_options")
        pid = link.get("platform_id")
        if pid not in platforms:
            err(f"{tag} platform_id {pid!r} does not exist")
        else:
            used_platforms.add(pid)
        pack_ids = ([link["battery_pack_id"]] if "battery_pack_id" in link else []) + list(
            link.get("battery_pack_options") or []
        )
        for pk in pack_ids:
            if pk not in packs:
                err(f"{tag} battery pack {pk!r} does not exist")
            else:
                used_packs.add(pk)
        if "uncertain" in link and not isinstance(link["uncertain"], bool):
            err(f"{tag} uncertain must be true/false")
        for key in ("notes", "class_override_note"):
            if key in link and (not isinstance(link[key], str) or not link[key].strip()):
                err(f"{tag} {key} must be non-empty text")
        if link.get("uncertain") and not link.get("notes") and not link.get("class_override_note"):
            err(f"{tag} uncertain: true needs a note saying what is in doubt")

        volt = link.get("voltage")
        if volt is None:
            err(f"{tag} voltage missing")
            volt = {}
        for e in schema.errors("VariantVoltage", volt):
            err(f"{tag} voltage {e}")
        ch = link.get("charger_400v")
        if ch is None:
            err(f"{tag} charger_400v missing")
            ch = {}
        for e in schema.errors("Charger400vBehaviour", ch):
            err(f"{tag} charger_400v {e}")
        if not isinstance(volt, dict) or not isinstance(ch, dict):
            continue

        stated = volt.get("class_id")
        if stated not in (None, ND) and stated not in ids_by_table["voltage_classes"]:
            err(f"{tag} voltage.class_id {stated!r} does not exist")
        derived = derive_class(volt.get("nominal_v"))
        if isinstance(volt.get("nominal_v"), (int, float)) and derived is None:
            err(f"{tag} nominal_v {volt['nominal_v']} is outside every voltage class")
        if (
            derived
            and stated not in (None, ND)
            and stated != derived
            and not link.get("class_override_note")
        ):
            err(
                f"{tag} nominal_v {volt['nominal_v']} implies {derived}, stated {stated}; add class_override_note if intended"
            )
        if derived and stated == derived and link.get("class_override_note"):
            err(f"{tag} class_override_note set but stated class matches the derived class")
        effective = stated if stated not in (None, ND) else derived
        if (
            effective is None
            and pid in platforms
            and platforms[pid].get("voltage_class_id") not in (None, ND)
        ):
            effective = platforms[pid]["voltage_class_id"]

        pack = packs.get(link.get("battery_pack_id", ""), {})
        pv = pack.get("nominal_v")
        if (
            isinstance(pv, (int, float))
            and isinstance(volt.get("nominal_v"), (int, float))
            and pv != volt["nominal_v"]
        ):
            err(f"{tag} voltage.nominal_v {volt['nominal_v']} differs from pack nominal_v {pv}")

        mode = ch.get("mode")
        if effective == "400v" and mode != "native":
            err(f"{tag} 400 V-class car must have charger_400v.mode native (got {mode})")
        if effective in ("800v", "900v-plus") and mode == "native":
            err(f"{tag} {effective} car cannot be native on 400 V chargers")
        if "kw" in ch and ch["kw"] is not None and mode not in ("booster", "limited"):
            err(f"{tag} charger_400v.kw only applies to booster / limited")
        if mode in ("booster", "limited") and ch.get("kw") is None:
            warn(f"{tag} {mode} without kw")
        if mode in ("booster", "limited") and not link.get("uncertain"):
            warn(f"{tag} {mode} kW figures change with software; consider uncertain: true")

        # capacity sanity (warning only)
        spec = (variants.get(vid) or {}).get("specs") or {}
        for vkey, pkey in (("battery_kwh_net", "usable_kwh"), ("battery_kwh_gross", "gross_kwh")):
            a, b = spec.get(vkey), pack.get(pkey)
            if (
                isinstance(a, (int, float))
                and isinstance(b, (int, float))
                and abs(a - b) > CAPACITY_TOLERANCE * b
            ):
                warn(f"{tag} variant {vkey} {a} vs pack {pkey} {b}")

    for vid in sorted(set(variants) - set(linked_variants)):
        err(f"variant_links.yaml: variant {vid} has no link")
    for vid, n in sorted(linked_variants.items()):
        if n > 1:
            err(f"variant_links.yaml: variant {vid} linked {n} times")
    for gid in sorted(generations - gens_with_variants - linked_gens):
        err(f"variant_links.yaml: generation {gid} has no variants and no generation-level default")
    for pk in sorted(set(packs) - used_packs):
        warn(f"battery_packs.yaml: pack {pk} is not used by any link")
    for pid in sorted(set(platforms) - used_platforms):
        warn(f"platforms.yaml: platform {pid} is not used by any link")

    return errors, warnings


def summary(data: Data) -> str:
    tax = data["taxonomy"]
    links = data["links_doc"].get("links") or []
    return (
        f"voltage_classes={len(tax['voltage_classes'])} chemistries={len(tax['chemistries'])} "
        f"cooling_types={len(tax['cooling_types'])} glossary_terms={len(tax['glossary_terms'])} "
        f"platforms={len(data['platforms_doc'].get('platforms') or [])} "
        f"packs={len(data['packs_doc'].get('packs') or [])} links={len(links)} "
        f"(uncertain={sum(1 for x in links if isinstance(x, dict) and x.get('uncertain'))})"
    )


def self_test(base: Data, schema: Schema) -> int:
    """Each mutation must produce at least one error containing the expected text."""
    errs, _ = check(base, schema)
    if errs:
        print("self-test: repo data must be valid first:")
        for e in errs:
            print("  " + e)
        return 1

    def m_short(d: Data) -> None:
        d["taxonomy"]["glossary_terms"][0]["short"]["en"] = " ".join(["word"] * 21)

    def m_related(d: Data) -> None:
        d["taxonomy"]["glossary_terms"][0]["related"].append("no-such-term")

    def m_dup(d: Data) -> None:
        d["taxonomy"]["chemistries"].append(copy.deepcopy(d["taxonomy"]["chemistries"][0]))

    def m_chem(d: Data) -> None:
        d["packs_doc"]["packs"][0]["chemistry_id"] = "unobtainium"

    def m_cell(d: Data) -> None:
        d["packs_doc"]["packs"][0]["cell_format"] = "hexagonal"

    def m_platform(d: Data) -> None:
        d["links_doc"]["links"][0]["platform_id"] = "no-such-platform"

    def m_variant(d: Data) -> None:
        d["links_doc"]["links"].pop(0)

    def m_native(d: Data) -> None:
        d["links_doc"]["links"][0]["charger_400v"] = {"mode": "booster", "kw": 50}

    def m_override(d: Data) -> None:
        for link in d["links_doc"]["links"]:
            link.pop("class_override_note", None)

    def m_gap(d: Data) -> None:
        d["taxonomy"]["voltage_classes"][0]["max_v"] = 540

    def m_nl(d: Data) -> None:
        d["taxonomy"]["cooling_types"][0]["label"].pop("nl")

    cases: list[tuple[str, Callable[[Data], None], str]] = [
        ("short > 20 words", m_short, "words (max"),
        ("dangling related", m_related, "related id"),
        ("duplicate chemistry", m_dup, "duplicate id"),
        ("unknown chemistry", m_chem, "chemistry_id"),
        ("bad cell format (schema)", m_cell, "hexagonal"),
        ("unknown platform", m_platform, "platform_id"),
        ("variant without link", m_variant, "has no link"),
        ("400 V car not native", m_native, "must have charger_400v.mode native"),
        ("class mismatch without override", m_override, "add class_override_note"),
        ("voltage class gap", m_gap, "gap or overlap"),
        ("missing nl label", m_nl, "label.nl missing"),
    ]
    failed = 0
    for name, mutate, expect in cases:
        d = copy.deepcopy(base)
        mutate(d)
        errs, _ = check(d, schema)
        ok = any(expect in e for e in errs)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
        failed += 0 if ok else 1
    print(f"self-test: {len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    schema = Schema(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    data = load_all()
    if "--self-test" in argv:
        return self_test(data, schema)
    errors, warnings = check(data, schema)
    if schema.patched:
        warnings.insert(
            0,
            (
                f"schema: {schema.patched} `oneOf: [Id, const not-disclosed]` treated as anyOf "
                "('not-disclosed' matches the Id pattern, so oneOf always rejects it); fix in packages/schema"
            ),
        )
    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print(summary(data))
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
