"""Shared configuration management for the Aura Journal backend.

This module centralizes environment-based configuration using Pydantic v2's
`BaseSettings` and `ConfigDict`. Each settings class corresponds to a specific
domain (database, service, or Google Cloud), ensuring that configuration values
are validated and loaded from environment variables or a `.env` file.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


# ---------------------------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------------------------
class DatabaseSettings(BaseSettings):
    """
    Configuration for database connections.

    Values are read automatically from environment variables or a `.env` file.
    Example `.env` entries:
        DATABASE_URL=postgresql+psycopg2://user:password@localhost/dbname
        MONGODB_URL=mongodb://localhost:27017/mydatabase
    """

    # Tell Pydantic to load environment variables from .env
    model_config = ConfigDict(env_file=".env")

    # Connection URLs for relational and NoSQL databases
    database_url: str
    mongodb_url: str


# ---------------------------------------------------------------------------
# Service-Level Configuration
# ---------------------------------------------------------------------------
class ServiceSettings(BaseSettings):
    """
    General application and service-level configuration.

    Defines application-wide parameters such as log levels, debugging flags,
    and external service endpoints (like NLP microservices).
    """

    model_config = ConfigDict(env_file=".env")

    # Default endpoint for the NLP microservice used by the backend
    nlp_agent_url: str = "http://localhost:8001/analyze"

    # Logging verbosity (e.g., "DEBUG", "INFO", "WARNING", "ERROR")
    log_level: str = "INFO"

    # Enable debug mode for development
    debug: bool = False


# ---------------------------------------------------------------------------
# Google Cloud Platform Configuration
# ---------------------------------------------------------------------------
class GCPSettings(BaseSettings):
    """
    Google Cloud Platform (GCP) configuration.

    Used for authentication and communication with Google Cloud services.
    """

    model_config = ConfigDict(env_file=".env")

    # Path to a service account JSON key file or the raw credentials string
    google_application_credentials: str = ""
