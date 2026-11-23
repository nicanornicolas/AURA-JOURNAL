"""Phrase lexicons for English and Swahili.

Two jobs:
1. Need-state detection from metaphors and everyday phrasing ("running on
   empty", "nimelemewa") that emotion classifiers miss. Used with every provider.
2. A zero-download fallback emotion detector (``LexiconEmotionProvider``) that
   emits GoEmotions-style labels, so outputs look the same as the HF provider.

Lexicons are deliberately small and editable. Grow them from real (consented,
anonymised) entries and from the Kaggle evaluation notebook.
"""

import re
from collections.abc import Iterable

from shared import EmotionScore, NeedState

NEED_STATES: tuple[str, ...] = (
    "overwhelmed",
    "drained",
    "stuck",
    "lonely",
    "anxious",
    "restless",
    "low",
    "curious",
    "content",
)

# need_state -> list of (pattern, weight)
NEED_PHRASES: dict[str, list[tuple[str, float]]] = {
    "overwhelmed": [
        (r"overwhelm(ed|ing)?", 1.0),
        (r"too much (going on|on my plate)", 0.9),
        (r"(drowning|buried) in", 0.8),
        (r"(my )?mind is (cluttered|racing|all over)", 0.8),
        (r"can'?t (keep up|cope)", 0.8),
        (r"stress(ed|ful)?", 0.6),
        (r"burn(ed|t)? ?out", 0.7),
        (r"nimelemewa", 1.0),
        (r"msongo wa mawazo", 0.9),
        (r"mambo (ni )?mengi", 0.7),
        (r"presha", 0.6),
    ],
    "drained": [
        (r"exhausted", 1.0),
        (r"(so |really )?tired", 0.7),
        (r"running on empty", 1.0),
        (r"(fried|drained|depleted|worn out|wiped out)", 0.9),
        (r"no energy", 0.9),
        (r"burn(ed|t)? ?out", 0.8),
        (r"nimechoka", 1.0),
        (r"uchovu", 0.9),
        (r"sina nguvu", 0.9),
    ],
    "stuck": [
        (r"stuck", 1.0),
        (r"in a rut", 1.0),
        (r"(uninspired|unmotivated|bored|stagnant)", 0.8),
        (r"same (old )?(thing|routine) every day", 0.8),
        (r"(going|running) in circles", 0.8),
        (r"(my )?mind is foggy|brain fog", 0.6),
        (r"nimekwama", 1.0),
        (r"sijui (la|nini) kufanya", 0.8),
        (r"nimeboeka|boring", 0.7),
    ],
    "lonely": [
        (r"lonely|loneliness", 1.0),
        (r"(all )?alone", 0.7),
        (r"no one (to talk to|understands)", 0.9),
        (r"isolated", 0.9),
        (r"miss (my )?(friends|family|people)", 0.6),
        (r"upweke|mpweke", 1.0),
        (r"(niko )?peke yangu", 0.8),
    ],
    "anxious": [
        (r"anxious|anxiety", 1.0),
        (r"(nervous|worried|panick?(ed|y)?|on edge|uneasy)", 0.8),
        (r"can'?t (stop overthinking|sleep)", 0.7),
        (r"overthink(ing)?", 0.7),
        (r"wasiwasi", 1.0),
        (r"hofu|naogopa", 0.8),
    ],
    "restless": [
        (r"restless", 1.0),
        (r"(frustrated|irritated|annoyed|angry|furious|fed up)", 0.8),
        (r"(cooped|cooped up|caged|trapped)", 0.7),
        (r"need to (get out|move|escape)", 0.8),
        (r"hasira|nimekasirika", 0.9),
        (r"kero|nimechukizwa", 0.7),
    ],
    "low": [
        (r"\bsad\b|sadness", 1.0),
        (r"(down|low|blue|heartbroken|grieving|hurt)", 0.6),
        (r"crying|cried|tears", 0.8),
        (r"empty inside", 0.9),
        (r"huzuni|nimehuzunika", 1.0),
        (r"(nalia|machozi)", 0.8),
        (r"moyo (unauma|umevunjika)", 0.9),
    ],
    "curious": [
        (r"curious", 0.9),
        (r"(want|wanna) to (explore|try something new|discover)", 0.9),
        (r"adventure", 0.7),
        (r"nataka kujaribu", 0.8),
        (r"kuzuru|kutembea", 0.5),
    ],
    "content": [
        (r"(happy|grateful|thankful|blessed|peaceful|calm|joy(ful)?|great day)", 0.8),
        (r"(relaxed|content|proud|excited)", 0.7),
        (r"furaha|nimefurahi", 0.9),
        (r"shukrani|nashukuru|baraka", 0.8),
        (r"amani|tulivu", 0.7),
    ],
}

# Fallback emotion detection: GoEmotions label -> phrases.
EMOTION_PHRASES: dict[str, list[str]] = {
    "sadness": [r"\bsad\b", r"huzuni", r"crying|nalia|machozi", r"heartbroken"],
    "grief": [r"griev(e|ing)|loss of|msiba"],
    "nervousness": [r"nervous|anxious|anxiety|wasiwasi|on edge|overthink"],
    "fear": [r"afraid|scared|terrified|hofu|naogopa"],
    "anger": [r"angry|furious|hasira|nimekasirika"],
    "annoyance": [r"annoyed|irritated|frustrated|fed up|kero"],
    "disappointment": [r"disappoint|let down|nimevunjika moyo"],
    "confusion": [r"confused|don'?t know what to do|sijui (la|nini) kufanya|foggy"],
    "joy": [r"happy|joy|furaha|nimefurahi|great day"],
    "gratitude": [r"grateful|thankful|blessed|shukrani|nashukuru|asante"],
    "optimism": [r"hopeful|looking forward|optimistic|natumaini"],
    "relief": [r"relieved|finally over|nimepumzika"],
    "excitement": [r"excited|can'?t wait|thrilled"],
    "curiosity": [r"curious|wonder(ing)? (what|if)|explore"],
    "love": [r"\blove\b|napenda|mapenzi"],
    "pride": [r"proud|najivunia"],
}

_NEED_RE = {
    state: [(re.compile(rf"\b(?:{p})\b", re.IGNORECASE), w) for p, w in phrases]
    for state, phrases in NEED_PHRASES.items()
}
_EMO_RE = {
    label: [re.compile(p, re.IGNORECASE) for p in phrases]
    for label, phrases in EMOTION_PHRASES.items()
}


def detect_needs(text: str) -> list[NeedState]:
    """Score each need state by its strongest matching phrase, plus 0.1 per extra match."""
    out: list[NeedState] = []
    for state, patterns in _NEED_RE.items():
        hits = [(m.group(0), w) for r, w in patterns if (m := r.search(text))]
        if not hits:
            continue
        score = min(1.0, max(w for _, w in hits) + 0.1 * (len(hits) - 1))
        out.append(NeedState(state=state, score=round(score, 3), evidence=[h for h, _ in hits]))
    return sorted(out, key=lambda n: n.score, reverse=True)


class LexiconEmotionProvider:
    """Zero-download emotion detector emitting GoEmotions-style labels."""

    name = "lexicon"

    def classify(self, text: str, language: str) -> list[EmotionScore]:
        scores: list[EmotionScore] = []
        for label, patterns in _EMO_RE.items():
            n = sum(1 for r in patterns if r.search(text))
            if n:
                scores.append(EmotionScore(label=label, score=round(min(1.0, 0.6 + 0.2 * (n - 1)), 3)))
        if not scores:
            scores.append(EmotionScore(label="neutral", score=0.6))
        return sorted(scores, key=lambda e: e.score, reverse=True)


def merge_needs(*groups: Iterable[NeedState]) -> list[NeedState]:
    """Merge need lists, keeping the max score and union of evidence per state."""
    merged: dict[str, NeedState] = {}
    for group in groups:
        for n in group:
            if n.state in merged:
                cur = merged[n.state]
                merged[n.state] = NeedState(
                    state=n.state,
                    score=max(cur.score, n.score),
                    evidence=sorted(set(cur.evidence) | set(n.evidence)),
                )
            else:
                merged[n.state] = n
    return sorted(merged.values(), key=lambda n: n.score, reverse=True)
