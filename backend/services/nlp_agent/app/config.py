"""
NLP Agent Configuration

Updated for Pydantic v2 compatibility.
Allows extra environment variables (to prevent validation errors)
and loads settings from a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Configuration for NLP sentiment thresholds."""

    # Thresholds for sentiment classification
    sentiment_positive_threshold: float = Field(default=0.25)
    sentiment_negative_threshold: float = Field(default=-0.25)
    sentiment_mixed_magnitude_threshold: float = Field(default=1.5)

    # ✅ Pydantic v2 settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",               # Load from .env file
        env_file_encoding="utf-8",     # Ensure correct encoding
        extra="allow"                  # <-- Ignore extra env vars like postgres_user, mongo_root_user, etc.
    )


# Global instance
settings = Settings()

