"""Tests for shared utilities and schemas."""

import pytest
from pydantic import ValidationError

from shared import (
    AnalysisPayload,
    Entry,
    EntryCreate,
    HealthResponse,
    SentimentResult,
    TextPayload,
)


class TestSharedSchemas:
    """Test shared Pydantic schemas."""
    
    def test_sentiment_result_valid(self):
        """Test valid SentimentResult creation."""
        sentiment = SentimentResult(label="POSITIVE", score=0.8)
        assert sentiment.label == "POSITIVE"
        assert sentiment.score == 0.8
    
    def test_analysis_payload_valid(self):
        """Test valid AnalysisPayload creation."""
        sentiment = SentimentResult(label="NEGATIVE", score=-0.5)
        analysis = AnalysisPayload(
            sentiment=sentiment,
            topics=["work", "stress"]
        )
        assert analysis.sentiment.label == "NEGATIVE"
        assert analysis.topics == ["work", "stress"]
    
    def test_text_payload_valid(self):
        """Test valid TextPayload creation."""
        payload = TextPayload(text="Hello world")
        assert payload.text == "Hello world"
    
    def test_text_payload_empty_text(self):
        """Test TextPayload with empty text fails validation."""
        with pytest.raises(ValidationError):
            TextPayload(text="")
    
    def test_entry_create_valid(self, sample_user_id):
        """Test valid EntryCreate creation."""
        entry = EntryCreate(
            user_id=sample_user_id,
            content="This is my journal entry"
        )
        assert entry.user_id == sample_user_id
        assert entry.content == "This is my journal entry"
    
    def test_entry_create_empty_content(self, sample_user_id):
        """Test EntryCreate with empty content fails validation."""
        with pytest.raises(ValidationError):
            EntryCreate(user_id=sample_user_id, content="")
    
    def test_health_response_default(self):
        """Test HealthResponse with defaults."""
        health = HealthResponse()
        assert health.status == "ok"
        assert health.service is None
        assert health.version is None
    
    def test_health_response_with_values(self):
        """Test HealthResponse with custom values."""
        health = HealthResponse(
            service="test-service",
            version="1.0.0"
        )
        assert health.status == "ok"
        assert health.service == "test-service"
        assert health.version == "1.0.0"
