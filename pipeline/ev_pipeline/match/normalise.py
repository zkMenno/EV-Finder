"""String normalisation for matching source make/model names to the seed (T-005).

Rules, in order:
1. Strip accents (NFKD, drop combining marks), so "ë-C4" == "e-C4" and "Zoé" == "Zoe".
2. Lower-case.
3. A "+" is the word "plus" ("P7+" -> ["p7", "plus"], so "P7+" != "P7" and "P7+" == "P7 Plus").
   Matching only: slug() keeps the old rule (drops "+"), so stable ids never change.
4. Split on anything that is not a letter or digit ("ID.3", "ID 3", "id-3" -> ["id", "3"]).

A *key* is the tokens joined without separators ("Mustang Mach-E" -> "mustangmache"), so
punctuation and spacing never matter. Matching compares keys of token prefixes, which keeps
token boundaries: "MODEL 3 LONG RANGE" starts with the key "model3" after two tokens, but
"IONIQ 5" never matches "IONIQ" + "Electric".
"""

from __future__ import annotations

import re
import unicodedata

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _split(text: str) -> list[str]:
    return [t for t in _NON_ALNUM.split(strip_accents(text).lower()) if t]


def tokens(text: str | None) -> list[str]:
    """Matching tokens: '+' counts as the word 'plus' (WS3 ask, T-068 / T-140)."""
    if not text:
        return []
    return _split(text.replace("+", " plus "))


def key(text: str | None) -> str:
    return "".join(tokens(text))


def slug(text: str | None) -> str:
    """Stable-id slug: lowercase, hyphen-separated, matches the schema Id pattern.

    Drops '+' (no 'plus' token): ids minted before the '+' rule must not change.
    """
    return "-".join(_split(text)) if text else ""


def prefix_keys(toks: list[str]) -> list[str]:
    """Keys of every token prefix, longest first: [a, b, c] -> [abc, ab, a]."""
    return ["".join(toks[:k]) for k in range(len(toks), 0, -1)]
