"""Shared configuration management."""

from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    database_url: str
    mongodb_url: str

    class Config:
        env_file = ".env"


class ServiceSettings(BaseSettings):
    """Service-level configuration."""
    nlp_agent_url: str = "http://localhost:8001/analyze"
    log_level: str = "INFO"
    debug: bool = False

    class Config:
        env_file = ".env"


class GCPSettings(BaseSettings):
    """Google Cloud Platform settings."""
    google_application_credentials: str = ""

    class Config:
        env_file = ".env"
