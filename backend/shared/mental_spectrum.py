"""SereneScapes "Mental Spectrum" rubric.

Single source of truth for how a place's psychological profile is scored.
Used by the data pipeline (to compute composites from annotated sub-factors)
and by the Wellness Engine (to rank places against a user's needs profile).

Sub-factors are scored 1-5 by an annotator (heuristic, LLM or human), except
``water_present`` which is 0 or 1. Composite formulas come from the
SereneScapes rubric definition:

    cognitive_load = 0.4 * navigational + 0.4 * sensory + 0.2 * rules      (1-5)
    biophilia      = 0.6 * immersion + 0.4 * biodiversity + water_present (1-6)
    awe            = 0.6 * vastness + 0.4 * stimulus_power                (1-5)
    novelty        = max(cultural, experiential, sensory_surprise)         (1-5)

``social_density`` (1-5) is scored directly (crowd level), and
``trigger_warnings`` is a free list of tags drawn from ``TRIGGER_TAGS``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

# Scale bounds for each composite field, used to normalise distances.
FIELD_RANGES: dict[str, tuple[float, float]] = {
    "cognitive_load": (1.0, 5.0),
    "biophilia": (1.0, 6.0),
    "awe": (1.0, 5.0),
    "novelty": (1.0, 5.0),
    "social_density": (1.0, 5.0),
}

SPECTRUM_FIELDS: tuple[str, ...] = tuple(FIELD_RANGES)

TRIGGER_TAGS: frozenset[str] = frozenset(
    {
        "heights",
        "crowds",
        "deep_water",
        "enclosed_spaces",
        "loud_noise",
        "wildlife",
        "darkness",
        "steep_terrain",
        "traffic",
        "alcohol",
    }
)


def _score(v: float) -> float:
    if not 1 <= v <= 5:
        raise ValueError(f"sub-factor scores must be between 1 and 5, got {v}")
    return float(v)


class SubFactors(BaseModel):
    """Annotated sub-factors for one place (1-5 unless noted)."""

    navigational: float = Field(3, description="How hard it is to find your way")
    sensory: float = Field(3, description="Noise, brightness, smells, movement")
    rules: float = Field(2, description="Explicit and implicit social rules")
    immersion: float = Field(1, description="How surrounded by nature you are")
    biodiversity: float = Field(1, description="Variety of plants and wildlife")
    water_present: int = Field(0, ge=0, le=1, description="1 if water is present")
    vastness: float = Field(1, description="Physical or conceptual vastness")
    stimulus_power: float = Field(1, description="Raw power of the experience")
    cultural: float = Field(1, description="Cultural uniqueness")
    experiential: float = Field(1, description="Uniqueness of the activity")
    sensory_surprise: float = Field(1, description="Unexpected sights and sounds")

    @field_validator(
        "navigational",
        "sensory",
        "rules",
        "immersion",
        "biodiversity",
        "vastness",
        "stimulus_power",
        "cultural",
        "experiential",
        "sensory_surprise",
    )
    @classmethod
    def _in_range(cls, v: float) -> float:
        return _score(v)


class Spectrum(BaseModel):
    """Composite Mental Spectrum scores for one place."""

    cognitive_load: float
    biophilia: float
    awe: float
    novelty: float
    social_density: float = 3.0
    trigger_warnings: list[str] = Field(default_factory=list)

    @field_validator("trigger_warnings")
    @classmethod
    def _known_tags(cls, v: list[str]) -> list[str]:
        return sorted({t.strip().lower() for t in v if t.strip().lower() in TRIGGER_TAGS})


def compute_spectrum(
    sub: SubFactors,
    social_density: float = 3.0,
    trigger_warnings: list[str] | None = None,
) -> Spectrum:
    """Compute composite scores from sub-factors using the rubric formulas."""
    return Spectrum(
        cognitive_load=round(0.4 * sub.navigational + 0.4 * sub.sensory + 0.2 * sub.rules, 2),
        biophilia=round(0.6 * sub.immersion + 0.4 * sub.biodiversity + sub.water_present, 2),
        awe=round(0.6 * sub.vastness + 0.4 * sub.stimulus_power, 2),
        novelty=round(max(sub.cultural, sub.experiential, sub.sensory_surprise), 2),
        social_density=_score(social_density),
        trigger_warnings=trigger_warnings or [],
    )
