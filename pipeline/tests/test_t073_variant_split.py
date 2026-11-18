"""T-073: candidate variants from RDW TGK versions; EEA counts per version (Decision 049).

Uses the 17 real rdw-tgk records of fixtures/rdw_tgk/match_pre2020.jsonl (and the seed of
test_tgk_attach.py) through the real matcher, and 11 real grouped EEA rows of 2015
(fixtures/eea_versions, CC BY 4.0). No network.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import httpx
import yaml
from test_tgk_attach import SEED, VARIANTS, R, _run

from ev_pipeline.match.seed import parse_seed
from ev_pipeline.sources.eea import versions as ev
from ev_pipeline.variants import propose as vp

FIX = Path(__file__).parent / "fixtures"
EEA = ev.load(FIX / "eea_versions")


def _proposal(variants=None, eea=EEA, nl=None):
    recs = list(R.values())
    res = _run(recs, variants)
    return vp.place_versions(recs, parse_seed(SEED), res, nl or {}, eea)


def _group(p: vp.Proposal, rec) -> vp.Group:
    [g] = [g for g in p.groups if any(v.rec is rec for v in g.members)]
    return g


def test_tgk_key_and_tan_base() -> None:
    key = (
        "gr7t-qfnb+byxc-wwua[typegoedkeuringsnummer|variant|uitvoering|revisie]:"
        "e2*2007/46*0251*06|AGV|AGVYB0|0"
    )
    assert vp.tgk_key(key) == ("e2*2007/46*0251*06", "AGV", "AGVYB0")
    assert ev.tan_base("E2*2007/46*0251*07") == "e2*2007/46*0251"
    assert ev.tan_base("e11*2007/46*0230") == "e11*2007/46*0230"  # no extension: unchanged
    assert ev.tan_base(":e4*2007/46*0667*03") == "e4*2007/46*0667"
    assert ev.version_key("E2*2007/46*0251*05", "agv", "agvyb0") == (
        "e2*2007/46*0251",
        "AGV",
        "AGVYB0",
    )


def test_fingerprint_prefers_wltp_then_nedc() -> None:
    i3_wltp = R["e1*2007/46*1213*09|8P21|0AW40000"]
    assert vp.fingerprint(i3_wltp) == ("wltp", 47.1, 310.0)  # 310 km x 15.2 kWh/100 km
    golf = R["e1*2007/46*0623*10|GAC4EAGAX0|FA1FA1CZ003E0GAON1ML01VR0"]
    assert vp.fingerprint(golf) == ("nedc", 24.1, 190.0)


def test_split_by_energy_keeps_one_pack_and_splits_packs() -> None:
    p = _proposal()
    zoe = [v for v in p.versions if v.generation_id == "renault-zoe-ph1"]
    parts = vp.split_by_energy(zoe)
    energies = [sorted(v.energy for v in part) for part in parts]
    # 22 kWh versions (30.7-31.9 kWh drawn) stay together; the 41 kWh Z.E. 40 (53.6) is apart.
    assert energies == [[30.7, 31.3, 31.9, 31.9], [53.6]]


def test_verdicts_have_tie_nofit_novariant() -> None:
    p = _proposal()
    golf14 = _group(p, R["e1*2007/46*0623*10|GAC4EAGAX0|FA1FA1CZ003E0GAON1ML01VR0"])
    assert golf14.verdict == "have"
    assert golf14.row()["seed_variants"] == "volkswagen-e-golf-mk7-24kwh"
    # Z.E. 40 fits Q90, R90 and R110: the variant exists, the evidence to choose is missing.
    ze40 = _group(p, R["e2*2007/46*0251*10|V|YE0"])
    assert ze40.verdict == "tie"
    assert {"renault-zoe-ph1-q90", "renault-zoe-ph1-r90"} <= ze40.tied
    assert "attach-only" not in ze40.row()["seed_variants"]  # only known variant ids

    # Without the 30 kWh Leaf the 2016 Leaf 30KWH version fits nothing: a candidate.
    no30 = [v for v in VARIANTS if v["id"] != "nissan-leaf-ze0-30kwh"]
    p2 = _proposal(no30)
    leaf30 = _group(p2, R["e11*2007/46*0230*10|A|A03"])
    assert leaf30.verdict == "no-fit"
    assert leaf30.row()["reason"] == "battery contradicts the seed variant (30 vs 21/24 kWh) (1x)"

    # A generation with no variant at all (new seed generation): no-variant.
    no_golf75 = [v for v in VARIANTS if v["generation_id"] != "volkswagen-e-golf-mk75"]
    p3 = _proposal(no_golf75)
    golf17 = _group(p3, R["e1*2007/46*0623*26|GAC4EAZAX0|FA1FA1MD001E0GAON1ML01VR0"])
    assert golf17.verdict == "no-variant"


def test_several_when_one_fingerprint_holds_two_seed_variants() -> None:
    p = _proposal()
    g = _group(p, R["e2*2007/46*0251*00|AGV|AGVYA0"])  # Q210 and R240 share the 22 kWh pack
    assert g.verdict == "several"
    assert g.row()["seed_variants"] == "renault-zoe-ph1-q210, renault-zoe-ph1-r240"


def test_eea_counts_only_and_shared_never_double_counted() -> None:
    assert EEA is not None
    assert EEA.total == 10080  # every 2015 fixture row, incl. one without version codes
    assert EEA.by_version[("e2*2007/46*0251", "AGV", "AGVYB0")] == 808 + 2339 + 5896 + 244
    p = _proposal()
    # Two TGK records carry the AGVYB0 key (approval extensions *06 and *08): half each.
    yb0 = [
        v
        for v in p.versions
        if vp.tgk_key(v.rec.record_key) and vp.tgk_key(v.rec.record_key)[2] in ("AGVYB0", "YB0")
    ]
    shared = [v for v in yb0 if vp.tgk_key(v.rec.record_key)[1] == "AGV"]
    assert len(shared) == 1 and shared[0].eu_cars == 9287
    total = sum(v.eu_cars for v in p.versions)
    assert total <= EEA.total
    cov = vp.coverage(p, parse_seed(SEED), 15)
    assert 0 < cov["eea"]["pct_eu_registrations_seed_generations_via_tgk"] <= 100
    assert cov["candidate_groups"] == cov["groups_no_fit"] + cov["groups_no_variant"]


def test_eea_share_split_evenly() -> None:
    counts = ev.from_rows(
        [{"Year": 2020, "Mk": "X", "TAN": "e1*1*2*01", "Va": "A", "Ve": "B", "registrations": 10}]
    )
    p = _proposal(eea=counts)
    assert sum(v.eu_cars for v in p.versions) == 0  # no fixture TGK key matches
    recs = [R["e2*2007/46*0251*06|AGV|AGVYB0"], R["e2*2007/46*0251*06|AGV|AGVYB1"]]
    k1, k2 = (vp.tgk_key(r.record_key) for r in recs)
    rows = [
        {
            "Year": 2015,
            "Mk": "RENAULT",
            "TAN": k1[0],
            "Va": k1[1],
            "Ve": k1[2],
            "registrations": 10,
        },
        {
            "Year": 2015,
            "Mk": "RENAULT",
            "TAN": "e2*2007/46*0251*99",
            "Va": k2[1],
            "Ve": k2[2],
            "registrations": 4,
        },
    ]
    p2 = _proposal(eea=ev.from_rows(rows))
    by = {v.rec.record_key: v.eu_cars for v in p2.versions}
    assert by[recs[0].record_key] == 10 and by[recs[1].record_key] == 4


def test_query_selects_counts_only() -> None:
    q = ev.query_for(ev.VERSION_TABLES[0])
    head = q.split("FROM")[0]
    for spec in ("Zr", "[Z", "[M", "Ep", "[W"):
        assert spec not in head  # Decision 049: no spec column, nothing to become a fact
    assert "SUM(R) AS registrations" in head and "Ft = 'electric'" in q
    years = [t.year for t in ev.VERSION_TABLES]
    assert years == sorted(years) and years[0] == 2010 and len(set(years)) == len(years)


def test_fetch_checks_licence_and_writes_one_file_per_year(tmp_path: Path) -> None:
    tables = ev.VERSION_TABLES[:2]
    seen: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        if "sdi.eea" in str(req.url):
            lic = "Licence: CC-BY 4.0, DG CLIMA"
            body = {
                "hits": {
                    "hits": [{"_source": {"MD_ConstraintsUseLimitationObject": [{"default": lic}]}}]
                }
            }
            return httpx.Response(200, json=body)
        form = dict(x.split("=", 1) for x in req.content.decode().split("&"))
        seen.append(form["p"])
        row = {
            "Year": 0,
            "Mk": "RENAULT",
            "TAN": "e2*2007/46*0251*00",
            "Va": "AGV",
            "Ve": "AGVYA0",
            "registrations": 5,
        }
        return httpx.Response(200, json={"results": [row]})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        n = ev.fetch(client, tmp_path, tables=tables, sleep_s=0)
    assert n == 2 and seen == ["1", "1"]
    loaded = ev.load(tmp_path)
    assert loaded is not None and loaded.years == [2010, 2011] and loaded.total == 10


def test_fetch_refuses_without_cc_by(tmp_path: Path) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"hits": {"hits": []}})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        try:
            ev.fetch(client, tmp_path, tables=ev.VERSION_TABLES[:1], sleep_s=0)
        except RuntimeError as exc:
            assert "licence not confirmed" in str(exc)
        else:
            raise AssertionError("fetch must refuse an unconfirmed licence")
    assert not list(tmp_path.glob("versions-*.json"))


def test_propose_end_to_end_writes_review_queue(tmp_path: Path) -> None:
    from ev_pipeline.commands.variants import run_propose

    data = tmp_path / "data"
    (data / "seed").mkdir(parents=True)
    (data / "seed" / "models.yaml").write_text(yaml.safe_dump(SEED), encoding="utf-8")
    src = {"id": "seed-manual", "name": "seed", "licence": "CC-BY-4.0", "attribution": "x"}
    (data / "seed" / "variants.yaml").write_text(
        yaml.safe_dump({"source": src, "variants": VARIANTS}), encoding="utf-8"
    )
    (data / "staging").mkdir()
    lines = "\n".join(r.model_dump_json() for r in R.values()) + "\n"
    (data / "staging" / "rdw-tgk.records.jsonl").write_text(lines, encoding="utf-8")
    raw = data / "raw" / "rdw_tgk"
    raw.mkdir(parents=True)
    plates = [
        {
            "typegoedkeuringsnummer": "e2*2007/46*0251*10",
            "variant": "V",
            "uitvoering": "YE0",
            "n": "7",
        }
    ]
    (raw / "versions.json").write_text(json.dumps(plates), encoding="utf-8")
    eea_dir = data / "raw" / ev.DIR
    eea_dir.mkdir(parents=True)
    for f in (FIX / "eea_versions").iterdir():
        (eea_dir / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")

    cov = run_propose(data)
    with (data / "review" / vp.CSV_NAME).open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and list(rows[0])[:4] == ["review_id", "status", "record_key", "source_id"]
    assert all(r["review_id"].startswith("vc-") for r in rows)
    assert {r["status"] for r in rows} == {"open"}
    assert {r["verdict"] for r in rows} <= {"have", "several", "tie", "no-fit", "no-variant"}
    ze40 = [r for r in rows if "e2*2007/46*0251*10" in r["record_keys"]]
    assert ze40 and ze40[0]["nl_cars"] == "7" and ze40[0]["verdict"] == "tie"
    assert all(r["record_keys"] for r in rows)  # every group cites its TGK records
    saved = json.loads((data / "review" / vp.COVERAGE_NAME).read_text(encoding="utf-8"))
    assert saved["fingerprint_groups"] == cov["fingerprint_groups"] == len(rows)
    assert saved["tgk_versions_in_seed_generations"] == 17
    # Re-running gives the same file (idempotent step).
    before = (data / "review" / vp.CSV_NAME).read_text(encoding="utf-8")
    run_propose(data)
    assert (data / "review" / vp.CSV_NAME).read_text(encoding="utf-8") == before


def test_split_is_at_gaps_not_at_a_fixed_distance_from_the_lowest() -> None:
    p = _proposal()
    base = p.versions[0]

    def at(e: float) -> vp.Version:
        return vp.Version(**{**base.__dict__, "energy": e})

    # A dense run 99..109 (one pack, steps under 4 %) stays one group; 120 is a new pack.
    run = [at(x) for x in (99.1, 102.0, 104.5, 106.2, 107.1, 108.9, 120.0)]
    parts = vp.split_by_energy(run)
    assert [[v.energy for v in g] for g in parts] == [
        [99.1, 102.0, 104.5, 106.2, 107.1, 108.9],
        [120.0],
    ]
