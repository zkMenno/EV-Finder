"""normalise.key / tokens / slug rules."""

from __future__ import annotations

from ev_pipeline.match.normalise import key, slug, tokens

# --- '+' is the word 'plus' (WS3 ask, T-068 / T-140) -----------------------------------


def test_plus_is_a_token_for_matching() -> None:
    assert tokens("P7+") == ["p7", "plus"]
    assert key("P7+") == key("P7 Plus") == "p7plus"
    assert key("P7+") != key("P7")
    assert key("Leaf e+") == "leafeplus"


def test_slug_still_drops_plus_so_ids_never_change() -> None:
    assert slug("e+ 62 kWh") == "e-62-kwh"
    assert slug("P7+") == "p7"
    assert slug(None) == "" and slug("") == ""
