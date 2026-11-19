"""T-149: generations[].popularity, used-price source licences, Commons licence templates.
No network: httpx.MockTransport and generated images only."""

from __future__ import annotations

import io
import json
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest
from PIL import Image

from ev_pipeline.derive.popularity import (
    PopularityConfigError,
    attach_popularity,
    build_popularity,
    parse_config,
    period_end,
    pick_scores,
)
from ev_pipeline.derive.used_price import attach_source_licences, source_licence
from ev_pipeline.images.photos import (
    ALLOWED_TEMPLATES,
    Photo,
    parse_photos,
    template_licences,
    template_matches,
)
from ev_pipeline.images.qa import image_problems
from ev_pipeline.images.store import (
    build_release_images,
    cache_key,
    licence_check,
    licence_templates,
    page_title,
    read_templates,
    template_path,
    warning_templates,
)
from ev_pipeline.release.gate import parse_registry

CFG = {
    "weights": {"registrations": 0.8, "owner_picks": 0.2},
    "pick_values": {"shortlist": 1.0, "consider": 0.6, "fallback": 0.3},
    "favourite_bonus": 0.2,
}
RANK = {"rdw": "NL", "dft-veh": "UK"}


def reg(sid: str, cc: str, n: int, period: str, level: str = "generation", kind: str = "fleet"):
    return (cc, {"count": n, "kind": kind, "period": period, "level": level, "source_id": sid})


def row(gid: str, mid: str, *entries: tuple[str, dict[str, Any]]) -> dict[str, Any]:
    regs: dict[str, list[dict[str, Any]]] = {}
    for cc, e in entries:
        regs.setdefault(cc, []).append(e)
    return {"generation_id": gid, "model_id": mid, "registrations": regs}


GENS = [
    {"id": "a-gen1", "model_id": "a"},
    {"id": "a-gen2", "model_id": "a"},
    {"id": "b-gen1", "model_id": "b"},
    {"id": "c-gen1", "model_id": "c"},
]


UK900 = reg("dft-veh", "UK", 900, "2026-Q2", "model")


def test_popularity_shares_split_rank_and_absent() -> None:
    rows = [
        row("a-gen1", "a", reg("rdw", "NL", 300, "2026-11-18"), UK900),
        row("a-gen2", "a", reg("rdw", "NL", 100, "2026-11-18"), UK900),
        row("b-gen1", "b", reg("rdw", "NL", 600, "2026-11-18")),
        # new registrations and non-ranking sources never count
        row("c-gen1", "c", reg("eea", "NL", 5000, "2025", kind="new_registrations"),
            reg("kba-fz10", "DE", 9000, "2025-01..12", kind="new_registrations")),
    ]  # fmt: skip
    f, log = build_popularity(rows, GENS, CFG, None, RANK)
    assert "c-gen1" not in f  # schema: absent when no registrations matched
    # UK model count 900 split by RDW counts 300:100 -> 675 / 225
    assert f["a-gen1"]["registrations"] == 300 + 675
    assert f["a-gen2"]["registrations"] == 100 + 225
    assert f["b-gen1"]["registrations"] == 600
    assert f["a-gen1"]["source_ids"] == ["dft-veh", "rdw"]
    assert f["b-gen1"]["source_ids"] == ["rdw"]
    # shares: NL total 1000, UK total 900. a1 = (0.3+0.75)/2, b = (0.6+0)/2, a2 = (0.1+0.25)/2
    assert [f[g]["rank"] for g in ("a-gen1", "b-gen1", "a-gen2")] == [1, 2, 3]
    assert f["a-gen1"]["score"] == 80.0  # 100 x 0.8 x 1 / 1
    assert f["b-gen1"]["score"] == round(80 * 0.3 / 0.525, 1)
    assert f["a-gen1"]["as_of"] == "2026-11-18" and f["b-gen1"]["as_of"] == "2026-11-18"
    assert log["totals"] == {"dft-veh": 900, "rdw": 1000}
    assert all(0 <= x["score"] <= 100 for x in f.values())


def test_popularity_model_count_split_evenly_without_rdw_and_as_of_quarter() -> None:
    rows = [
        row("a-gen1", "a", reg("dft-veh", "UK", 100, "2026-Q2", "model")),
        row("a-gen2", "a", reg("dft-veh", "UK", 100, "2026-Q2", "model")),
    ]
    f, _ = build_popularity(rows, GENS, CFG, None, RANK)
    assert f["a-gen1"]["registrations"] == 50 and f["a-gen2"]["registrations"] == 50
    assert f["a-gen1"]["as_of"] == "2026-06-30"
    assert f["a-gen1"]["score"] == f["a-gen2"]["score"]
    assert (f["a-gen1"]["rank"], f["a-gen2"]["rank"]) == (1, 2)  # ties: stable by id


def test_owner_picks_blend_and_bonus_cap() -> None:
    picks = {"primary_car_picks": [
        {"seed_generation_id": "b-gen1", "verdict": "shortlist", "favourite": True},
        {"seed_generation_id": "b-gen1", "verdict": "fallback"},
        {"seed_generation_id": "a-gen1", "verdict": "consider", "favourite": True},
        {"seed_generation_id": "c-gen1", "verdict": "nope"},
    ]}  # fmt: skip
    cfg = parse_config(CFG)
    assert pick_scores(picks, cfg) == {"b-gen1": 1.0, "a-gen1": pytest.approx(0.8)}
    rows = [row("a-gen1", "a", reg("rdw", "NL", 100, "2026-11-18")),
            row("b-gen1", "b", reg("rdw", "NL", 50, "2026-11-18"))]  # fmt: skip
    f, _ = build_popularity(rows, GENS, CFG, picks, RANK)
    # a: 0.8 x 1 + 0.2 x 0.8 = 0.96; b: 0.8 x 0.5 + 0.2 x 1 = 0.6
    assert (f["a-gen1"]["score"], f["b-gen1"]["score"]) == (96.0, 60.0)


@pytest.mark.parametrize(
    "bad",
    [
        {**CFG, "weights": {"registrations": 0, "owner_picks": 0}},
        {**CFG, "weights": {"registrations": -1, "owner_picks": 1}},
        {**CFG, "pick_values": {"shortlist": 2, "consider": 0.6, "fallback": 0.3}},
        {**CFG, "favourite_bonus": 3},
    ],
)
def test_popularity_config_errors(bad: dict[str, Any]) -> None:
    with pytest.raises(PopularityConfigError):
        parse_config(bad)


@pytest.mark.parametrize(
    ("period", "end"),
    [("2026-11-18", date(2026, 11, 18)), ("2026-Q2", date(2026, 6, 30)),
     ("2025-01..12", date(2025, 12, 31)), ("2026-01..10", date(2026, 10, 31)),
     ("2025", date(2025, 12, 31)), ("2024-02", date(2024, 2, 29)), ("soon", None)],
)  # fmt: skip
def test_period_end(period: str, end: date | None) -> None:
    assert period_end(period) == end


def test_attach_popularity_validates_against_schema(tmp_path: Path) -> None:
    from ev_pipeline.schema_models import GenerationPopularity

    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "popularity.yaml").write_text(json.dumps(CFG))
    data = tmp_path / "data"
    data.mkdir()
    cat = {
        "generations": [dict(g) for g in GENS],
        "rows": [{k: v for k, v in r.items() if k != "model_id"} for r in [
            row("a-gen1", "a", reg("rdw", "NL", 10, "2026-11-18")),
        ]],
    }  # fmt: skip
    log, inputs = attach_popularity(cat, tmp_path / "config", data)
    assert log["status"] == "attached" and log["generations"] == 1
    pop = cat["generations"][0]["popularity"]
    GenerationPopularity.model_validate(pop)
    assert "popularity" not in cat["generations"][1]
    assert inputs == [] and log["config"]["path"] == "config/popularity.yaml"
    assert len(log["config"]["sha256"]) == 64
    # no config: no field, logged
    log2, _ = attach_popularity(cat, tmp_path / "nope", data)
    assert log2["status"].startswith("skipped")


# --- used price source licences ----------------------------------------------------------------

REGISTRY = parse_registry({"sources": [
    {"id": "model-estimate", "name": "EV Finder estimate models", "licence": "CC-BY-4.0",
     "status": "active"},
    {"id": "marktplaats", "name": "Marktplaats", "licence": "none (site terms of service)",
     "status": "active", "use": "aggregates-only", "decision": "060"},
    {"id": "eafo", "name": "EAFO", "licence": "CC-BY-4.0 (EC legal notice)", "status": "active"},
]})  # fmt: skip


def test_source_licence_from_registry() -> None:
    assert source_licence(REGISTRY, None) == "CC-BY-4.0"  # our own estimate model
    assert source_licence(REGISTRY, "eafo") == "CC-BY-4.0"  # SPDX id, note dropped
    assert source_licence(REGISTRY, "marktplaats") == "none (site terms of service)"
    assert source_licence(REGISTRY, "unknown-site") is None


def test_attach_source_licences_every_band() -> None:
    variants = [{"variant_id": "v1", "bands": {"NL": [
        {"build_year": 2021, "method": "model", "source": {"name": "curve"}},
        {"build_year": 2022, "method": "samples", "source_id": "marktplaats",
         "source": {"name": "Marktplaats", "url": "https://www.marktplaats.nl/x"}},
    ]}}]  # fmt: skip
    gen = [{"generation_id": "g", "country": "NL", "build_year": 2021, "source_id": "nobody",
            "source": {"name": "?"}}]  # fmt: skip
    log = attach_source_licences(variants, gen, REGISTRY)
    b = variants[0]["bands"]["NL"]
    assert b[0]["source"]["licence"] == "CC-BY-4.0"
    assert b[1]["source"]["licence"] == "none (site terms of service)"
    assert "licence" not in gen[0]["source"] and log["missing"] == ["g/NL/2021"]
    assert log["by_licence"] == {"CC-BY-4.0": 1, "none (site terms of service)": 1}


# --- Commons licence templates -----------------------------------------------------------------

PAGE = """=={{int:filedesc}}==
{{Information |description={{en|1=Car}} |author=[[User:X|X]] }}
=={{int:license-header}}==
{{self|GFDL|cc-by-sa-4.0|migration=redundant}}
{{Cc-by-sa-3.0,2.5,2.0,1.0}}
[[Category:Cars]]
"""


def test_licence_templates_from_wikitext() -> None:
    assert licence_templates(PAGE) == ["self|GFDL|cc-by-sa-4.0|migration=redundant",
                                       "Cc-by-sa-3.0,2.5,2.0,1.0"]  # fmt: skip
    assert warning_templates(PAGE) == []
    assert warning_templates("{{copyvio|reason}}{{cc-by-4.0}}") == ["copyvio"]
    yt = "{{From YouTube|1=x}}\n{{YouTube CC-BY |1= [https://www.youtube.com/watch?v=x Y]}}"
    assert licence_templates(yt) == ["YouTubeCC-BY|1=[https://www.youtube.com/watch?v=xY]"]
    assert licence_templates("{{User:Someone/CC-BY-photos}}") == []  # user wrapper: review


@pytest.mark.parametrize(
    ("licence", "template", "ok"),
    [
        ("CC-BY-SA-4.0", "self|GFDL|cc-by-sa-4.0|migration=redundant", True),
        ("CC-BY-SA-2.0", "Cc-by-sa-3.0,2.5,2.0,1.0", True),
        ("CC-BY-SA-3.0-DE", "cc-by-sa-3.0-de", True),
        ("CC-BY-2.0", "cc-by-2.0", True),
        ("CC-BY-4.0", "self|cc-by-sa-4.0", False),  # stray: SA template on a CC BY photo
        ("CC-BY-SA-4.0", "cc-zero", False),
        ("CC0-1.0", "self|cc-zero", True),
        ("CC0-1.0", "cc-by-4.0", False),
        ("public-domain", "PD-self", True),
        ("public-domain", "PD-old-70", True),
        ("public-domain", "PD-US", False),
        ("public-domain", "PD-old-70-1923", False),  # US-only variant
        ("CC-BY-SA-4.0", "self|Cc-by-sa-2.0+|GFDL|migration=redundant", True),  # "or later"
        ("CC-BY-SA-1.0", "Cc-by-sa-2.0+", False),
        ("CC-BY-3.0", "YouTubeCC-BY|1=[https://youtube.com/x]", True),
        ("CC-BY-4.0", "YouTubeCC-BY", False),
    ],
)
def test_template_matches(licence: str, template: str, ok: bool) -> None:
    assert template_matches(licence, template) is ok


def test_pd_old_allowlist() -> None:
    assert {"pd-old", "pd-old-70", "pd-old-100"} <= ALLOWED_TEMPLATES
    assert "pd-old-70-1923" not in ALLOWED_TEMPLATES
    assert template_licences("PD-old") == {"pd-old"}


def test_photos_yaml_stray_template_is_dropped() -> None:
    e = {
        "generation_id": "g1", "source": "commons",
        "page_url": "https://commons.wikimedia.org/wiki/File:A.jpg",
        "file_url": "https://upload.wikimedia.org/a.jpg", "licence": "CC-BY-4.0",
        "credit": "X, CC BY 4.0, via Wikimedia Commons", "retrieved_at": "2026-11-17",
        "licence_template": "cc-zero", "licence_checked_at": "2026-11-18",
    }  # fmt: skip
    photos, problems = parse_photos({"photos": [e]}, None, {"g1"}, date(2026, 11, 19))
    assert not photos and "does not grant CC-BY-4.0" in problems[0].reason


def photo(licence: str = "CC-BY-SA-4.0", **kw: Any) -> Photo:
    base: dict[str, Any] = {
        "generation_id": "g1",
        "source": "commons",
        "page_url": "https://commons.wikimedia.org/wiki/File:Kia%20EV6%202022.jpg",
        "file_url": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Kia_EV6.jpg",
        "licence": licence,
        "author": "X",
        "credit": "X, CC BY-SA 4.0, via Wikimedia Commons",
        "retrieved_at": date(2026, 11, 17),
    }
    base.update(kw)
    return Photo(**base)


def test_page_title() -> None:
    assert page_title(photo().page_url) == "File:Kia EV6 2022.jpg"
    assert page_title("https://example.org/wiki/File:A.jpg") is None


def _client(handler: Any) -> Any:
    return lambda _sid: httpx.Client(transport=httpx.MockTransport(handler))


def test_read_templates_once_and_licence_check(tmp_path: Path) -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, text="{{self|cc-by-sa-4.0}}")

    ph = photo()
    press = photo(source="press", licence="press-terms", generation_id="g2")
    cc0 = photo(licence="CC0-1.0", generation_id="g3", licence_template="cc-zero",
                licence_checked_at=date(2026, 11, 18))  # fmt: skip
    rep = read_templates([ph, press, cc0], tmp_path, _client(handler), sleep=lambda _s: None,
                         today=lambda: "2026-11-19")  # fmt: skip
    assert rep.fetched == ["g1"] and len(seen) == 1
    assert seen[0].url.host == "commons.wikimedia.org"
    assert seen[0].url.params["action"] == "raw"
    assert seen[0].url.params["title"] == "File:Kia EV6 2022.jpg"
    rep2 = read_templates([ph], tmp_path, _client(handler), sleep=lambda _s: None)
    assert rep2.cached == ["g1"] and len(seen) == 1  # never read twice: stable date + field
    assert licence_check(ph, tmp_path) == (
        {"licence_template": "self|cc-by-sa-4.0", "licence_checked_at": "2026-11-19"},
        "",
    )
    assert licence_check(press, tmp_path) == ({}, "")
    assert licence_check(cc0, tmp_path)[0]["licence_template"] == "cc-zero"


@pytest.mark.parametrize(
    ("page", "reason"),
    [
        ("{{cc-by-4.0}}", "does not grant CC-BY-SA-4.0"),
        ("no template here", "no licence template"),
        ("{{self|cc-by-sa-4.0}}{{delete|reason=x}}", "carries delete"),
    ],
)
def test_licence_check_refuses(tmp_path: Path, page: str, reason: str) -> None:
    ph = photo()
    read_templates([ph], tmp_path, _client(lambda _r: httpx.Response(200, text=page)),
                   sleep=lambda _s: None)  # fmt: skip
    lic, why = licence_check(ph, tmp_path)
    assert lic == {} and reason in why


def test_read_templates_429_stops(tmp_path: Path) -> None:
    a, b = photo(), photo(generation_id="g2", file_url="https://upload.wikimedia.org/b.jpg")
    rep = read_templates([a, b], tmp_path, _client(lambda _r: httpx.Response(429)),
                         sleep=lambda _s: None)  # fmt: skip
    assert rep.stopped and set(rep.failed) == {"g1", "g2"}
    assert not template_path(tmp_path, a).exists()


def _jpeg() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (900, 600), (10, 120, 200)).save(buf, format="JPEG")
    return buf.getvalue()


def test_build_drops_untemplated_commons_photo_and_qa_blocks(tmp_path: Path) -> None:
    ph = photo()
    (tmp_path / f"{cache_key(ph.file_url)}.bin").write_bytes(_jpeg())
    res = build_release_images([ph], tmp_path)
    assert res.fields == {} and "not read yet" in res.missing["g1"]
    template_path(tmp_path, ph).write_text(
        json.dumps({"wikitext": "{{self|cc-by-sa-4.0}}", "checked_at": "2026-11-19"})
    )
    res = build_release_images([ph], tmp_path)
    img = res.fields["g1"]
    assert img["licence_template"] == "self|cc-by-sa-4.0"
    assert img["licence_checked_at"] == "2026-11-19"
    cat = {"generations": [{"id": "g1", "image": img}]}
    assert image_problems(cat) == []
    # blocking in QA when the field slips through without or with a stray template
    for broken, why in (
        ({k: v for k, v in img.items() if k != "licence_template"}, "without licence_template"),
        ({**img, "licence_template": "cc-zero"}, "does not grant"),
    ):
        probs = image_problems({"generations": [{"id": "g1", "image": broken}]})
        assert any(why in p for p in probs), probs


def test_scratch_data_dir_uses_the_repo_config(tmp_path: Path) -> None:
    """ev verify builds in a scratch data dir: popularity must still find config/."""
    from ev_pipeline.release.build import config_dir

    assert (config_dir(tmp_path / "data") / "popularity.yaml").exists()
    (tmp_path / "config").mkdir()
    assert config_dir(tmp_path / "data") == tmp_path / "config"
