"""Ears service: combines language detection, emotions, need states and safety."""

from __future__ import annotations

from typing import Protocol

from loguru import logger
from pydantic import BaseModel, Field

from shared import EmotionScore, NeedState, SafetySignal

from ..config import Settings
from .hf import HFEmotionProvider
from .language import detect_language
from .lexicon import LexiconEmotionProvider, detect_needs, merge_needs
from .safety import screen

# GoEmotions label -> [(need_state, weight)]
EMOTION_TO_NEEDS: dict[str, list[tuple[str, float]]] = {
    "nervousness": [("anxious", 1.0)],
    "fear": [("anxious", 0.9)],
    "embarrassment": [("anxious", 0.4)],
    "sadness": [("low", 1.0), ("drained", 0.3)],
    "grief": [("low", 1.0)],
    "remorse": [("low", 0.6)],
    "disappointment": [("low", 0.7), ("stuck", 0.3)],
    "annoyance": [("restless", 0.7)],
    "anger": [("restless", 0.9), ("overwhelmed", 0.3)],
    "disapproval": [("restless", 0.4)],
    "disgust": [("restless", 0.4)],
    "confusion": [("overwhelmed", 0.6), ("stuck", 0.4)],
    "curiosity": [("curious", 0.8)],
    "desire": [("curious", 0.4)],
    "joy": [("content", 1.0)],
    "amusement": [("content", 0.6)],
    "excitement": [("content", 0.6), ("curious", 0.3)],
    "gratitude": [("content", 0.9)],
    "love": [("content", 0.7)],
    "optimism": [("content", 0.7)],
    "pride": [("content", 0.6)],
    "relief": [("content", 0.6)],
    "admiration": [("content", 0.4)],
    "approval": [("content", 0.3)],
    "caring": [("content", 0.4)],
}
POSITIVE = {"joy", "amusement", "excitement", "gratitude", "love", "optimism", "pride",
            "relief", "admiration", "approval", "caring", "curiosity", "desire", "realization"}
NEGATIVE = {"sadness", "grief", "remorse", "disappointment", "annoyance", "anger",
            "disapproval", "disgust", "fear", "nervousness", "embarrassment", "confusion"}
HIGH_ENERGY = {"anger", "excitement", "fear", "nervousness", "amusement", "annoyance",
               "joy", "desire", "curiosity"}
LOW_ENERGY = {"sadness", "grief", "disappointment", "remorse", "relief", "caring"}


class EmotionProvider(Protocol):
    name: str

    def classify(self, text: str, language: str) -> list[EmotionScore]: ...


class EarsResult(BaseModel):
    language: str
    emotions: list[EmotionScore]
    needs: list[NeedState]
    valence: float = Field(description="-1 (negative) to 1 (positive)")
    energy: float = Field(description="-1 (low arousal) to 1 (high arousal)")
    safety: SafetySignal
    provider: str


def needs_from_emotions(emotions: list[EmotionScore]) -> list[NeedState]:
    acc: dict[str, float] = {}
    ev: dict[str, list[str]] = {}
    for e in emotions:
        for state, w in EMOTION_TO_NEEDS.get(e.label, []):
            acc[state] = max(acc.get(state, 0.0), e.score * w)
            ev.setdefault(state, []).append(e.label)
    return [NeedState(state=s, score=round(v, 3), evidence=sorted(set(ev[s])))
            for s, v in acc.items() if v >= 0.15]


def _balance(emotions: list[EmotionScore], plus: set[str], minus: set[str]) -> float:
    p = sum(e.score for e in emotions if e.label in plus)
    m = sum(e.score for e in emotions if e.label in minus)
    return 0.0 if p + m == 0 else round((p - m) / (p + m), 3)


class EarsService:
    def __init__(self, provider: EmotionProvider, safety_resources: list[str]) -> None:
        self.provider = provider
        self.safety_resources = safety_resources

    def analyze(self, text: str) -> EarsResult:
        language = detect_language(text)
        safety = screen(text, self.safety_resources)
        emotions = self.provider.classify(text, language)
        needs = merge_needs(detect_needs(text), needs_from_emotions(emotions))
        return EarsResult(
            language=language,
            emotions=emotions[:8],
            needs=needs,
            valence=_balance(emotions, POSITIVE, NEGATIVE),
            energy=_balance(emotions, HIGH_ENERGY, LOW_ENERGY),
            safety=safety,
            provider=self.provider.name,
        )


def build_ears_service(settings: Settings) -> EarsService:
    choice = settings.ears_provider.lower()
    provider: EmotionProvider
    if choice == "hf" or (choice == "auto" and HFEmotionProvider.available()):
        provider = HFEmotionProvider(
            settings.hf_emotion_model, settings.hf_translation_model_sw_en,
            settings.hf_device, settings.emotion_min_score,
        )
    else:
        provider = LexiconEmotionProvider()
    logger.info(f"Ears provider: {provider.name}")
    return EarsService(provider, settings.safety_resources)
