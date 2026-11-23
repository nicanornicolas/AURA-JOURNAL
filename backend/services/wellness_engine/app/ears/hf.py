"""Hugging Face emotion provider (CPU, lazy-loaded).

Models are downloaded on first use into the Hugging Face cache (mount it as a
volume so restarts don't re-download). Approximate resident memory on CPU:
emotion model ~0.5 GB, Swahili->English translator ~0.3 GB.
"""

from __future__ import annotations

import threading
from typing import Any

from loguru import logger

from shared import EmotionScore


class HFEmotionProvider:
    name = "hf"

    def __init__(self, emotion_model: str, translation_model: str, device: int = -1,
                 min_score: float = 0.08) -> None:
        self.emotion_model = emotion_model
        self.translation_model = translation_model
        self.device = device
        self.min_score = min_score
        self._classifier: Any = None
        self._translator: Any = None
        self._lock = threading.Lock()

    @staticmethod
    def available() -> bool:
        try:
            import transformers  # noqa: F401
        except ImportError:
            return False
        return True

    def _load(self) -> None:
        from transformers import pipeline

        with self._lock:
            if self._classifier is None:
                logger.info(f"Loading emotion model {self.emotion_model}")
                self._classifier = pipeline(
                    "text-classification", model=self.emotion_model, top_k=None,
                    device=self.device, truncation=True,
                )
            if self._translator is None and self.translation_model:
                logger.info(f"Loading translator {self.translation_model}")
                self._translator = pipeline(
                    "translation", model=self.translation_model, device=self.device,
                    truncation=True,
                )

    def warm_up(self) -> None:
        self._load()

    def translate_to_english(self, text: str) -> str:
        self._load()
        if self._translator is None:
            return text
        out = self._translator(text, max_length=512)
        return str(out[0]["translation_text"])

    def classify(self, text: str, language: str) -> list[EmotionScore]:
        self._load()
        source = self.translate_to_english(text) if language == "sw" else text
        raw = self._classifier(source)
        rows = raw[0] if raw and isinstance(raw[0], list) else raw
        scores = [
            EmotionScore(label=r["label"], score=round(float(r["score"]), 4))
            for r in rows
            if float(r["score"]) >= self.min_score
        ]
        return sorted(scores, key=lambda e: e.score, reverse=True) or [
            EmotionScore(label="neutral", score=1.0)
        ]
