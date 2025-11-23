"""Dependency injection setup for the entry ingestor service."""

from functools import lru_cache

from shared import DatabaseSettings, ServiceSettings, DatabaseManager
from .services import EntryService, HTTPNLPClient, MongoInsightStorage


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """Get database settings (cached)."""
    return DatabaseSettings()


@lru_cache()
def get_service_settings() -> ServiceSettings:
    """Get service settings (cached)."""
    return ServiceSettings()


@lru_cache()
def get_database_manager() -> DatabaseManager:
    """Get database manager (cached)."""
    return DatabaseManager(get_database_settings())


def get_entry_service() -> EntryService:
    """Get entry service with dependencies."""
    db_manager = get_database_manager()
    service_settings = get_service_settings()
    
    nlp_client = HTTPNLPClient(service_settings.nlp_agent_url)
    insight_storage = MongoInsightStorage(db_manager.mongo_db)
    
    return EntryService(nlp_client, insight_storage)


def get_db():
    """Get database session."""
    yield from get_database_manager().get_db()
