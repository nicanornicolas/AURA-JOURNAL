"""Shared schemas used across services."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class SentimentResult(BaseModel):
    """Sentiment analysis result."""
    label: str
    score: float


class AnalysisPayload(BaseModel):
    """NLP analysis payload containing sentiment and topics."""
    sentiment: SentimentResult
    topics: List[str]


class TextPayload(BaseModel):
    """Payload for text analysis requests."""
    text: str = Field(..., min_length=1)


class EntryCreate(BaseModel):
    """Schema for creating a journal entry."""
    user_id: uuid.UUID
    content: str = Field(..., min_length=1)


class Entry(BaseModel):
    """Schema for journal entry response."""
    model_config = ConfigDict(from_attributes=True)
    
    entry_id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime
    content: str
    analysis: Optional[AnalysisPayload] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    service: Optional[str] = None
    version: Optional[str] = None
