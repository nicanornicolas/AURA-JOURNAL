"""TRANSFORM: score each place on the Mental Spectrum sub-factors.

Three annotators, cheapest first:
- HeuristicAnnotator: rules over OSM tags and category. Free, offline, instant.
- GeminiAnnotator: Google AI Studio free-tier key, via REST (no SDK needed).
- OllamaAnnotator: a local open model on the homelab (no key, slower on CPU).

LLM annotators fall back to the heuristic result if the call or the JSON fails,
so a run always completes. Every record says which annotator produced it, and
a human confirms the final scores in Airtable.
"""

from __future__ import annotations

import json
from typing import Protocol

import httpx
from loguru import logger
from pydantic import ValidationError

from shared.mental_spectrum import TRIGGER_TAGS, SubFactors, compute_spectrum

from .models import POI, Annotation, GoldenRecord

# category -> baseline sub-factors (1-5; water_present 0/1) and social density
BASELINES: dict[str, dict] = {
    "forest": dict(navigational=2, sensory=1, rules=1, immersion=5, biodiversity=4, vastness=3,
                   stimulus_power=3, cultural=2, experiential=2, sensory_surprise=3, social=2),
    "nature_reserve": dict(navigational=3, sensory=2, rules=2, immersion=5, biodiversity=5, vastness=5,
                           stimulus_power=4, cultural=2, experiential=4, sensory_surprise=4, social=2),
    "garden": dict(navigational=1, sensory=2, rules=2, immersion=4, biodiversity=4, vastness=2,
                   stimulus_power=2, cultural=2, experiential=2, sensory_surprise=2, social=2.5),
    "park": dict(navigational=2, sensory=2, rules=2, immersion=3, biodiversity=3, vastness=2,
                 stimulus_power=2, cultural=1, experiential=2, sensory_surprise=2, social=3),
    "viewpoint": dict(navigational=2, sensory=2, rules=1, immersion=4, biodiversity=3, vastness=5,
                      stimulus_power=4, cultural=2, experiential=3, sensory_surprise=3, social=2),
    "waterfall": dict(navigational=3, sensory=3, rules=1, immersion=5, biodiversity=4, vastness=4,
                      stimulus_power=5, cultural=2, experiential=3, sensory_surprise=4, social=2),
    "lake": dict(navigational=2, sensory=2, rules=1, immersion=4, biodiversity=3, vastness=4,
                 stimulus_power=3, cultural=1, experiential=2, sensory_surprise=2, social=2.5),
    "trail": dict(navigational=3, sensory=1, rules=1, immersion=4, biodiversity=4, vastness=3,
                  stimulus_power=3, cultural=1, experiential=3, sensory_surprise=3, social=1.5),
    "museum": dict(navigational=3, sensory=2, rules=3, immersion=1, biodiversity=1, vastness=2,
                   stimulus_power=3, cultural=4, experiential=3, sensory_surprise=3, social=3),
    "gallery": dict(navigational=2, sensory=2, rules=3, immersion=1, biodiversity=1, vastness=1,
                    stimulus_power=3, cultural=4, experiential=3, sensory_surprise=3, social=2),
    "library": dict(navigational=2, sensory=1, rules=4, immersion=1, biodiversity=1, vastness=1,
                    stimulus_power=1, cultural=3, experiential=1, sensory_surprise=1, social=2),
    "cafe": dict(navigational=1, sensory=3, rules=2, immersion=1, biodiversity=1, vastness=1,
                 stimulus_power=1, cultural=2, experiential=2, sensory_surprise=2, social=3.5),
}

CATEGORY_TRIGGERS: dict[str, list[str]] = {
    "viewpoint": ["heights", "steep_terrain"],
    "waterfall": ["deep_water", "steep_terrain", "heights"],
    "lake": ["deep_water"],
    "nature_reserve": ["wildlife"],
    "trail": ["steep_terrain"],
}


class Annotator(Protocol):
    name: str

    def annotate(self, poi: POI) -> Annotation: ...


def _clamp(v: float) -> float:
    return float(min(5, max(1, v)))


class HeuristicAnnotator:
    name = "heuristic"

    def annotate(self, poi: POI) -> Annotation:
        b = dict(BASELINES.get(poi.category, BASELINES["park"]))
        social = b.pop("social")
        tags = poi.tags
        notes = [f"baseline for {poi.category}"]
        water = 0
        if tags.get("water") or tags.get("waterway") or poi.category in {"lake", "waterfall"} \
                or "river" in poi.name.lower() or "dam" in poi.name.lower():
            water = 1
            notes.append("water present")
        if tags.get("fee") == "yes" or tags.get("access") in {"private", "customers"}:
            social -= 0.5
            notes.append("paid or restricted access lowers crowding")
        if tags.get("wheelchair") == "yes":
            b["navigational"] = max(1, b["navigational"] - 1)
            notes.append("step-free access")
        if tags.get("lit") == "no":
            notes.append("unlit")
        pop = (poi.foursquare or {}).get("popularity")
        if isinstance(pop, int | float):
            social = 1 + 4 * float(pop)  # Foursquare popularity is 0-1
            notes.append(f"foursquare popularity {pop:.2f}")
        triggers = list(CATEGORY_TRIGGERS.get(poi.category, []))
        if social >= 4:
            triggers.append("crowds")
        if tags.get("lit") == "no":
            triggers.append("darkness")
        sub = SubFactors(**{k: _clamp(v) for k, v in b.items()}, water_present=water)
        return Annotation(sub_factors=sub, social_density=_clamp(social),
                          trigger_warnings=triggers, rationale="; ".join(notes), annotator=self.name)


PROMPT = """You are a wellness data analyst for SereneScapes, scoring outdoor and cultural places in {city}
for how they affect mental state. Score each sub-factor from 1 (very low) to 5 (very high) using the rubric:
- navigational: how hard to find your way (1 single path, 5 chaotic and unmarked)
- sensory: noise, brightness, smells, movement (1 quiet library, 5 loud food court)
- rules: explicit/implicit social rules (1 park bench, 5 formal event or security checks)
- immersion: surrounded by nature (1 one tree on a pavement, 5 dense forest, city out of sight)
- biodiversity: variety of plants and wildlife (2 manicured lawn, 5 nature reserve)
- water_present: 1 if a river, lake, dam or waterfall is part of the visit, else 0
- vastness: physical sense of scale (1 small room, 5 panoramic view)
- stimulus_power: raw power of the experience (2 quiet painting, 5 huge waterfall)
- cultural, experiential, sensory_surprise: uniqueness vs everyday urban life (1 ordinary, 5 unique)
Also give social_density (1 nearly empty, 5 packed) and trigger_warnings chosen only from:
{triggers}.
Reply with JSON only:
{{"sub_factors": {{...all 11 keys...}}, "social_density": n, "trigger_warnings": [...], "rationale": "one sentence"}}

Place: {name}
Category: {category}
OSM tags: {tags}
Foursquare: {fsq}
"""


def build_prompt(poi: POI, city: str) -> str:
    useful = {k: v for k, v in poi.tags.items() if not k.startswith(("addr:", "name:", "source", "wiki"))}
    return PROMPT.format(city=city, triggers=", ".join(sorted(TRIGGER_TAGS)), name=poi.name,
                         category=poi.category, tags=json.dumps(useful)[:1500],
                         fsq=json.dumps(poi.foursquare or {}))


def parse_llm_json(text: str, annotator: str) -> Annotation:
    """Parse and validate the model's JSON. Raises ValueError on anything off-rubric."""
    s = text.strip()
    if s.startswith("```"):
        s = s.strip("`").removeprefix("json").strip()
    data = json.loads(s)
    try:
        sub = SubFactors(**{k: (int(v) if k == "water_present" else _clamp(float(v)))
                            for k, v in data["sub_factors"].items()})
        return Annotation(
            sub_factors=sub,
            social_density=_clamp(float(data.get("social_density", 3))),
            trigger_warnings=[t for t in data.get("trigger_warnings", []) if t in TRIGGER_TAGS],
            rationale=str(data.get("rationale", ""))[:500],
            annotator=annotator,
        )
    except (KeyError, TypeError, ValidationError) as e:
        raise ValueError(f"LLM JSON did not match the rubric: {e}") from e


class _LLMAnnotator:
    name = "llm"

    def __init__(self, city: str, client: httpx.Client | None = None) -> None:
        self.city = city
        self.client = client or httpx.Client(timeout=120)
        self.fallback = HeuristicAnnotator()

    def _call(self, prompt: str) -> str:
        raise NotImplementedError

    def annotate(self, poi: POI) -> Annotation:
        try:
            return parse_llm_json(self._call(build_prompt(poi, self.city)), self.name)
        except (httpx.HTTPError, ValueError, KeyError, IndexError) as e:
            logger.warning(f"{self.name} annotation failed for {poi.name}, using heuristic: {e}")
            a = self.fallback.annotate(poi)
            a.rationale = f"[{self.name} failed, heuristic fallback] {a.rationale}"
            return a


class GeminiAnnotator(_LLMAnnotator):
    name = "gemini"

    def __init__(self, api_key: str, model: str, city: str, client: httpx.Client | None = None) -> None:
        super().__init__(city, client)
        self.api_key, self.model = api_key, model

    def _call(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        r = self.client.post(url, params={"key": self.api_key}, json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
        })
        r.raise_for_status()
        # Gemini's shape (NOT OpenAI's choices[0].message.content):
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]


class OllamaAnnotator(_LLMAnnotator):
    name = "ollama"

    def __init__(self, url: str, model: str, city: str, client: httpx.Client | None = None) -> None:
        super().__init__(city, client)
        self.url, self.model = url.rstrip("/"), model

    def _call(self, prompt: str) -> str:
        r = self.client.post(f"{self.url}/api/generate", json={
            "model": self.model, "prompt": prompt, "format": "json", "stream": False,
            "options": {"temperature": 0.2}})
        r.raise_for_status()
        return r.json()["response"]


def make_annotator(kind: str, settings) -> Annotator:
    if kind == "gemini":
        if not settings.gemini_api_key:
            raise ValueError("ANNOTATOR=gemini needs GEMINI_API_KEY")
        return GeminiAnnotator(settings.gemini_api_key, settings.gemini_model, settings.city)
    if kind == "ollama":
        return OllamaAnnotator(settings.ollama_url, settings.ollama_model, settings.city)
    return HeuristicAnnotator()


def to_golden(poi: POI, a: Annotation) -> GoldenRecord:
    return GoldenRecord(poi=poi, annotation=a,
                        spectrum=compute_spectrum(a.sub_factors, a.social_density, a.trigger_warnings))
