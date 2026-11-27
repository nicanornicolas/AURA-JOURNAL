"""Dependency injection setup for the entry ingestor service."""

import uuid
from functools import lru_cache

from fastapi import Depends, Header, HTTPException, status

from shared.auth import AuthError, AuthSettings, CurrentUser, verify_access_token

from shared import DatabaseSettings, ServiceSettings, DatabaseManager
from .services import (
    EntryService,
    HTTPNLPClient,
    InsightStorage,
    MongoInsightStorage,
    PostgresInsightStorage,
)


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
    insight_storage: InsightStorage
    if get_database_settings().insight_store == "mongo":
        insight_storage = MongoInsightStorage(db_manager.mongo_db)
    else:
        insight_storage = PostgresInsightStorage(db_manager.session_local)
    
    return EntryService(nlp_client, insight_storage)


def get_db():
    """Get database session."""
    yield from get_database_manager().get_db()


# ---------------- authentication ----------------


@lru_cache()
def get_auth_settings() -> AuthSettings:
    return AuthSettings()


def get_current_user(
    authorization: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
    settings: AuthSettings = Depends(get_auth_settings),
) -> CurrentUser:
    """Resolve the caller from a Bearer access token issued by the auth service.

    With AUTH_REQUIRED=false (local development only) an ``X-User-Id`` header is
    accepted instead, so the app can be exercised before login screens exist.
    """
    if authorization and authorization.lower().startswith("bearer "):
        try:
            return verify_access_token(
                authorization[7:].strip(), settings.jwt_secret_key, settings.clock_skew_seconds
            )
        except AuthError as e:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, f"Invalid token: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
    if not settings.auth_required and x_user_id:
        try:
            return CurrentUser(user_id=uuid.UUID(x_user_id))
        except ValueError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "X-User-Id must be a UUID") from e
    if not settings.auth_required:
        # Dev mode with no identity yet: nil UUID. POST /entries then uses the body's user_id.
        return CurrentUser(user_id=uuid.UUID(int=0))
    raise HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Not authenticated", headers={"WWW-Authenticate": "Bearer"}
    )
