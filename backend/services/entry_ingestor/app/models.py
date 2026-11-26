"""Database models for the entry ingestor service."""

import uuid
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import JSON, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class JournalEntry(Base):
    """Journal entry model."""
    __tablename__ = "journal_entries"

    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)


class JournalInsight(Base):
    """AI analysis of a journal entry (replaces the MongoDB `insights` collection)."""
    __tablename__ = "journal_insights"

    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("journal_entries.entry_id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    # JSONB on Postgres, plain JSON elsewhere (lets tests run on in-memory SQLite)
    analysis: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
