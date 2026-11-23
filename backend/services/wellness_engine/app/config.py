"""Wellness Engine configuration (environment variables or .env)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Ears ---
    # auto: use Hugging Face models when `transformers` is installed, else lexicon.
    # lexicon: rules only (no downloads, ~50 MB RAM). hf: always use models.
    ears_provider: str = "auto"
    hf_emotion_model: str = "SamLowe/roberta-base-go_emotions"
    # Swahili entries are translated to English before emotion classification.
    hf_translation_model_sw_en: str = "Helsinki-NLP/opus-mt-sw-en"
    hf_device: int = -1  # -1 = CPU
    emotion_min_score: float = 0.08

    # --- Brain ---
    heuristics_file: Path = APP_DIR / "brain" / "heuristics.yaml"
    places_source: str = "file"  # file | postgres
    places_file: Path = APP_DIR / "data" / "seed_places.json"
    database_url: str = ""

    # --- Safety ---
    # Shown instead of recommendations when crisis language is detected.
    # VERIFY these numbers before any real users see them.
    safety_resources: list[str] = [
        "Emergency services in Kenya: 999 or 112",
        "Kenya Red Cross (toll-free): 1199",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
