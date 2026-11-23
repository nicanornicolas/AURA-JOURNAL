"""Crisis-language safety screen (English and Swahili).

Rules-first by design: a missed crisis is worse than a false alarm, and rules
are auditable. When ``level == "crisis"`` the engine returns support resources
instead of recommendations.
"""

import re

from shared import SafetySignal

_CRISIS = [
    r"\bkill(ing)? myself\b",
    r"\bend(ing)? (my|it all|my life)\b",
    r"\b(want|wanna|going) to die\b",
    r"\bsuicid(e|al)\b",
    r"\bself[- ]?harm\b",
    r"\bhurt(ing)? myself\b",
    r"\bno reason to live\b",
    r"\bbetter off dead\b",
    # Swahili
    r"\bkujiua\b",
    r"\bnijiue\b",
    r"\bnataka kufa\b",
    r"\bsitaki kuishi\b",
    r"\bkujidhuru\b",
    r"\bkujikata\b",
]
_CONCERN = [
    r"\bhopeless\b",
    r"\bno point\b",
    r"\bworthless\b",
    r"\bcan'?t go on\b",
    r"\bgive up on (everything|life)\b",
    # Swahili
    r"\bsina matumaini\b",
    r"\bhakuna maana\b",
    r"\bsiwezi tena\b",
    r"\bnimekata tamaa\b",
]
_CRISIS_RE = [re.compile(p, re.IGNORECASE) for p in _CRISIS]
_CONCERN_RE = [re.compile(p, re.IGNORECASE) for p in _CONCERN]


def screen(text: str, resources: list[str]) -> SafetySignal:
    crisis = [m.group(0) for r in _CRISIS_RE if (m := r.search(text))]
    if crisis:
        return SafetySignal(flagged=True, level="crisis", matched=crisis, resources=resources)
    concern = [m.group(0) for r in _CONCERN_RE if (m := r.search(text))]
    if concern:
        return SafetySignal(flagged=False, level="concern", matched=concern, resources=resources)
    return SafetySignal()
