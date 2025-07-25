"""Entry Ingestor FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared import Entry, EntryCreate, HealthResponse
from .dependencies import get_entry_service, get_db
from .services import EntryService
from .models import Base
from .dependencies import get_database_manager


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    db_manager = get_database_manager()
    Base.metadata.create_all(bind=db_manager.engine)
    logger.info("Entry Ingestor service started")
    
    yield
    
    # Shutdown
    db_manager.close_connections()
    logger.info("Entry Ingestor service stopped")


app = FastAPI(
    title="Aura Journal - Entry Ingestor Service",
    description="Service for creating and managing journal entries.",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/entries", response_model=Entry, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry: EntryCreate,
    db: Session = Depends(get_db),
    entry_service: EntryService = Depends(get_entry_service)
) -> Entry:
    """
    Creates a new journal entry.
    - Receives user_id and content.
    - Saves to the database.
    - Returns the full entry object with its generated ID and timestamp.
    """
    try:
        db_entry = entry_service.create_entry(db, entry)
        return Entry.model_validate(db_entry)
    except Exception as e:
        logger.error(f"Failed to create entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create journal entry"
        )


@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(service="entry-ingestor", version="1.0.0")
