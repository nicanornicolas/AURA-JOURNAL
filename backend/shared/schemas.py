"""Shared schemas used across services."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class SentimentResult(BaseModel):
    """Sentiment analysis result."""
    label: str
    score: float


class EmotionScore(BaseModel):
    """One detected emotion with its confidence (0-1)."""
    label: str
    score: float


class NeedState(BaseModel):
    """A wellness need state (e.g. overwhelmed, drained, stuck) with strength 0-1."""
    state: str
    score: float
    evidence: List[str] = Field(default_factory=list)


class SafetySignal(BaseModel):
    """Result of the crisis-language safety screen."""
    flagged: bool = False
    level: str = "none"  # none | concern | crisis
    matched: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)


class AnalysisPayload(BaseModel):
    """NLP analysis payload.

    ``sentiment`` and ``topics`` are the original contract used by the mobile app.
    The remaining fields are added by the Wellness Engine and are optional so
    older clients keep working.
    """
    sentiment: SentimentResult
    topics: List[str]
    language: Optional[str] = None
    emotions: List[EmotionScore] = Field(default_factory=list)
    needs: List[NeedState] = Field(default_factory=list)
    safety: Optional[SafetySignal] = None


class TextPayload(BaseModel):
    """Payload for text analysis requests."""
    text: str = Field(..., min_length=1)


class EntryCreate(BaseModel):
    """Schema for creating a journal entry.

    ``user_id`` comes from the access token. It is accepted in the body only for
    backwards compatibility and local development (AUTH_REQUIRED=false); when a
    token is present the two must match.
    """
    user_id: Optional[uuid.UUID] = None
    content: str = Field(..., min_length=1, max_length=20000)


class EntryUpdate(BaseModel):
    """Schema for editing a journal entry's text (triggers fresh analysis)."""
    content: str = Field(..., min_length=1, max_length=20000)


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
