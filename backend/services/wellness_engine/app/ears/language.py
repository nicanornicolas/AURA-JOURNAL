"""Lightweight English / Swahili language detection (no model download)."""

import re

_TOKEN = re.compile(r"[a-zA-Z']+")

# High-frequency Swahili function words and pronoun forms.
_SW_WORDS = frozenset(
    """
    na ya wa kwa ni la za cha vya katika sana leo jana kesho mimi wewe yeye sisi
    nina niko sina sijui lakini kwamba hii huu hiyo hilo hapa pale kuna hakuna
    kama bado tu pia sasa nini gani nani wapi lini kwa_nini vizuri mbaya kazi
    nyumbani rafiki marafiki maisha moyo akili mawazo siku usiku asubuhi jioni
    """.split()
)
# Swahili verb prefixes (subject + tense), e.g. nimechoka, ninahisi, sitaki.
_SW_PREFIX = re.compile(r"^(nime|nina|nili|nita|ume|una|ali|ana|tume|tuna|sija|sita|sina)[a-z]{2,}")


def detect_language(text: str) -> str:
    """Return "sw" or "en". Defaults to "en" for short or mixed text."""
    tokens = [t.lower() for t in _TOKEN.findall(text)]
    if not tokens:
        return "en"
    hits = sum(1 for t in tokens if t in _SW_WORDS or _SW_PREFIX.match(t))
    return "sw" if hits / len(tokens) >= 0.25 else "en"
