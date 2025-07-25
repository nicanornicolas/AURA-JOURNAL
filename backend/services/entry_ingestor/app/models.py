"""Database models for the entry ingestor service."""

import uuid
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
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
