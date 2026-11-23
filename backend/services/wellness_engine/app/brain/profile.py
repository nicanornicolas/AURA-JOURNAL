"""Brain step 1: turn need states into a target Mental Spectrum profile."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel

from shared import NeedState
from shared.mental_spectrum import SPECTRUM_FIELDS


class FieldTarget(BaseModel):
    target: float
    weight: float


class StateRule(BaseModel):
    why: str
    targets: dict[str, FieldTarget]


class Heuristics(BaseModel):
    version: int
    fields: dict[str, dict[str, str]]
    need_states: dict[str, StateRule]
    default: StateRule

    @classmethod
    def load(cls, path: Path) -> Heuristics:
        data = yaml.safe_load(path.read_text())
        h = cls.model_validate(data)
        for name, rule in [*h.need_states.items(), ("default", h.default)]:
            unknown = set(rule.targets) - set(SPECTRUM_FIELDS)
            if unknown:
                raise ValueError(f"heuristics rule '{name}' uses unknown fields {unknown}")
        return h


class NeedsProfile(BaseModel):
    """Target score and importance (0-1) per Mental Spectrum field."""

    targets: dict[str, float]
    importance: dict[str, float]
    drivers: list[NeedState]
    rationale: list[str]


def build_profile(needs: list[NeedState], h: Heuristics, min_score: float = 0.2) -> NeedsProfile:
    active = [n for n in needs if n.score >= min_score and n.state in h.need_states]
    rules = [(n.score, h.need_states[n.state]) for n in active] or [(1.0, h.default)]

    num: dict[str, float] = {}
    den: dict[str, float] = {}
    for strength, rule in rules:
        for field, ft in rule.targets.items():
            w = strength * ft.weight
            num[field] = num.get(field, 0.0) + w * ft.target
            den[field] = den.get(field, 0.0) + w

    targets = {f: round(num[f] / den[f], 2) for f in den}
    peak = max(den.values())
    importance = {f: round(den[f] / peak, 3) for f in den}
    rationale = [h.need_states[n.state].why for n in active] or [h.default.why]
    return NeedsProfile(targets=targets, importance=importance, drivers=active, rationale=rationale)
