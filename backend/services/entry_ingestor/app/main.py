"""Entry Ingestor FastAPI application (Aura Journal entries API).

Every endpoint except /health needs a Bearer access token from the auth
service. Entries are always scoped to the token's user.
"""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared import Entry, EntryCreate, EntryUpdate, HealthResponse
from shared.auth import INSECURE_DEFAULT, AuthSettings, CurrentUser

from .dependencies import (
    get_auth_settings,
    get_current_user,
    get_database_manager,
    get_db,
    get_entry_service,
)
from .models import Base
from .services import EntryService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    auth = get_auth_settings()
    if not auth.auth_required:
        logger.warning("AUTH_REQUIRED=false: entries API is open. Local development only.")
    elif auth.jwt_secret_key == INSECURE_DEFAULT:
        logger.error("JWT_SECRET_KEY is the insecure default. Set the same secret as the auth service.")
    db_manager = get_database_manager()
    Base.metadata.create_all(bind=db_manager.engine)
    logger.info("Entry Ingestor service started")
    yield
    db_manager.close_connections()
    logger.info("Entry Ingestor service stopped")


app = FastAPI(
    title="Aura Journal - Entry Ingestor Service",
    description="Create, read, edit and delete journal entries, and see mood trends.",
    version="1.1.0",
    lifespan=lifespan,
)


class EntryPage(BaseModel):
    items: list[Entry]
    total: int
    limit: int
    offset: int


class DailyMood(BaseModel):
    date: str
    entries: int
    mood: float | None  # average sentiment score, -1 to 1; None if no analysis that day


class NeedCount(BaseModel):
    state: str
    count: int


class EmotionCount(BaseModel):
    label: str
    count: int


class MoodTrends(BaseModel):
    days: int
    entries: int
    daily: list[DailyMood]
    top_needs: list[NeedCount]
    top_emotions: list[EmotionCount]


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, "Entry not found")


@app.post("/entries", response_model=Entry, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry: EntryCreate,
    user: CurrentUser = Depends(get_current_user),
    auth: AuthSettings = Depends(get_auth_settings),
    db: Session = Depends(get_db),
    entry_service: EntryService = Depends(get_entry_service),
) -> Entry:
    """Create an entry for the signed-in user and analyse it."""
    identified = auth.auth_required or user.user_id.int != 0  # token or X-User-Id given
    if identified:
        if entry.user_id is not None and entry.user_id != user.user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "user_id does not match the signed-in user")
        owner = user.user_id
    else:
        if entry.user_id is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "user_id is required when AUTH_REQUIRED=false")
        owner = entry.user_id
    try:
        db_entry = entry_service.create_entry(db, EntryCreate(user_id=owner, content=entry.content))
        return Entry.model_validate(db_entry)
    except Exception as e:
        logger.error(f"Failed to create entry: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create journal entry") from e


@app.get("/entries", response_model=EntryPage)
def list_entries(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    entry_service: EntryService = Depends(get_entry_service),
) -> EntryPage:
    """The signed-in user's entries, newest first, with their analysis."""
    rows, total = entry_service.list_entries(db, user.user_id, limit, offset)
    return EntryPage(items=[Entry.model_validate(r) for r in rows], total=total, limit=limit, offset=offset)


@app.get("/entries/{entry_id}", response_model=Entry)
def get_entry(
    entry_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    entry_service: EntryService = Depends(get_entry_service),
) -> Entry:
    row = entry_service.get_entry(db, user.user_id, entry_id)
    if not row:
        raise _not_found()
    return Entry.model_validate(row)


@app.patch("/entries/{entry_id}", response_model=Entry)
def update_entry(
    entry_id: uuid.UUID,
    update: EntryUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    entry_service: EntryService = Depends(get_entry_service),
) -> Entry:
    """Edit an entry's text. It is analysed again."""
    row = entry_service.update_entry(db, user.user_id, entry_id, update.content)
    if not row:
        raise _not_found()
    return Entry.model_validate(row)


@app.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    entry_service: EntryService = Depends(get_entry_service),
) -> Response:
    """Delete an entry and its analysis permanently."""
    if not entry_service.delete_entry(db, user.user_id, entry_id):
        raise _not_found()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/insights/trends", response_model=MoodTrends)
def mood_trends(
    days: int = Query(30, ge=1, le=365),
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    entry_service: EntryService = Depends(get_entry_service),
) -> MoodTrends:
    """Daily mood and the most common needs and emotions over the last N days."""
    return MoodTrends(**entry_service.mood_trends(db, user.user_id, days))


@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(service="entry-ingestor", version="1.1.0")
