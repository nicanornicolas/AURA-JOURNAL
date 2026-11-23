"""Brain step 2: rank places against a needs profile."""

from __future__ import annotations

import math

from pydantic import BaseModel

from shared.mental_spectrum import FIELD_RANGES

from .places import Place
from .profile import Heuristics, NeedsProfile


class Recommendation(BaseModel):
    place: Place
    fit: float  # 0-1
    distance_km: float | None = None
    reasons: list[str]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _field_fit(value: float, target: float, field: str) -> float:
    lo, hi = FIELD_RANGES[field]
    return max(0.0, 1.0 - abs(value - target) / (hi - lo))


def _reason(field: str, value: float, h: Heuristics) -> str:
    lo, hi = FIELD_RANGES[field]
    labels = h.fields.get(field, {})
    side = "high" if value >= (lo + hi) / 2 else "low"
    return f"{labels.get(side, field)} ({field.replace('_', ' ')} {value:g}/{hi:g})"


def rank_places(
    places: list[Place],
    profile: NeedsProfile,
    h: Heuristics,
    avoid: set[str] | None = None,
    near: tuple[float, float] | None = None,
    max_km: float | None = None,
    limit: int = 5,
) -> list[Recommendation]:
    avoid = {a.lower() for a in (avoid or set())}
    total_imp = sum(profile.importance.values()) or 1.0
    recs: list[Recommendation] = []
    for p in places:
        if avoid & set(p.spectrum.trigger_warnings):
            continue
        dist = haversine_km(near[0], near[1], p.latitude, p.longitude) if near else None
        if dist is not None and max_km is not None and dist > max_km:
            continue
        contrib = {
            f: profile.importance[f] * _field_fit(getattr(p.spectrum, f), t, f)
            for f, t in profile.targets.items()
        }
        fit = sum(contrib.values()) / total_imp
        best = sorted(contrib, key=lambda f: contrib[f], reverse=True)[:2]
        recs.append(Recommendation(
            place=p, fit=round(fit, 3),
            distance_km=round(dist, 1) if dist is not None else None,
            reasons=[_reason(f, getattr(p.spectrum, f), h) for f in best],
        ))
    recs.sort(key=lambda r: (-r.fit, r.distance_km or 0.0))
    return recs[:limit]
