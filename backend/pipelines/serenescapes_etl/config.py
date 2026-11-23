"""Pipeline configuration. Reads env vars (or a .env file), or Kaggle secrets via kaggle.py."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Overpass bbox order is (south, west, north, east). Nairobi is ~1.3 S, ~36.8 E.
NAIROBI_BBOX = (-1.45, 36.65, -1.15, 37.00)


class PipelineSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    city: str = "nairobi"
    bbox: tuple[float, float, float, float] = NAIROBI_BBOX
    overpass_url: str = "https://overpass-api.de/api/interpreter"
    max_places: int = 300

    # Enrichment (optional). Leave blank to skip.
    foursquare_api_key: str = ""
    # Foursquare moved to a new Places API in 2025; both styles are supported.
    foursquare_url: str = "https://places-api.foursquare.com/places/search"
    foursquare_api_version: str = "2025-06-17"

    # Annotation: heuristic (free, offline) | gemini (free AI Studio key) | ollama (local)
    annotator: str = "heuristic"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"

    # Load / sync
    airtable_pat: str = ""
    airtable_base_id: str = ""
    airtable_table_name: str = "Places"
    database_url: str = ""

    data_dir: Path = Path("data/serenescapes")
