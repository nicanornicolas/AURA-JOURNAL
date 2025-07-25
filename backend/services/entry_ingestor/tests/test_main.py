"""Integration tests for entry ingestor FastAPI endpoints."""

import uuid
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from shared import Entry, AnalysisPayload, SentimentResult
from services.entry_ingestor.app.main import app
from services.entry_ingestor.app.dependencies import get_db, get_entry_service
from services.entry_ingestor.app.models import JournalEntry


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    return Mock()


@pytest.fixture
def mock_entry_service():
    """Mock entry service."""
    return Mock()


@pytest.fixture
def test_client(mock_db_session, mock_entry_service):
    """Test client with overridden dependencies."""
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_entry_service] = lambda: mock_entry_service
    
    yield TestClient(app)
    
    # Cleanup
    app.dependency_overrides.clear()


class TestEntryEndpoints:
    """Test cases for entry endpoints."""
    
    def test_create_entry_successfully(self, test_client, mock_entry_service):
        """Test successful entry creation."""
        test_user_id = uuid.uuid4()
        test_entry_id = uuid.uuid4()
        
        # Mock the service response
        mock_db_entry = Mock(spec=JournalEntry)
        mock_db_entry.entry_id = test_entry_id
        mock_db_entry.user_id = test_user_id
        mock_db_entry.content = "My test entry"
        mock_db_entry.timestamp = datetime.now(timezone.utc)
        mock_db_entry.analysis = None
        
        mock_entry_service.create_entry.return_value = mock_db_entry
        
        # Make the request
        response = test_client.post(
            "/entries",
            json={"user_id": str(test_user_id), "content": "My test entry"},
        )
        
        # Assert the results
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "My test entry"
        assert data["user_id"] == str(test_user_id)
        assert "entry_id" in data
        assert "timestamp" in data
    
    def test_create_entry_with_analysis(self, test_client, mock_entry_service):
        """Test entry creation with analysis."""
        test_user_id = uuid.uuid4()
        test_entry_id = uuid.uuid4()
        
        # Mock the service response with analysis
        analysis = AnalysisPayload(
            sentiment=SentimentResult(label="POSITIVE", score=0.8),
            topics=["work", "productivity"]
        )
        
        mock_db_entry = Mock(spec=JournalEntry)
        mock_db_entry.entry_id = test_entry_id
        mock_db_entry.user_id = test_user_id
        mock_db_entry.content = "I had a great day at work!"
        mock_db_entry.timestamp = datetime.now(timezone.utc)
        mock_db_entry.analysis = analysis
        
        mock_entry_service.create_entry.return_value = mock_db_entry
        
        # Make the request
        response = test_client.post(
            "/entries",
            json={"user_id": str(test_user_id), "content": "I had a great day at work!"},
        )
        
        # Assert the results
        assert response.status_code == 201
        data = response.json()
        assert data["analysis"] is not None
        assert data["analysis"]["sentiment"]["label"] == "POSITIVE"
        assert data["analysis"]["topics"] == ["work", "productivity"]
    
    def test_create_entry_validation_error(self, test_client):
        """Test entry creation with invalid data."""
        response = test_client.post(
            "/entries",
            json={"user_id": "invalid-uuid", "content": ""},  # Empty content
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_entry_service_error(self, test_client, mock_entry_service):
        """Test handling of service errors."""
        test_user_id = uuid.uuid4()
        
        # Mock service to raise an exception
        mock_entry_service.create_entry.side_effect = Exception("Database error")
        
        response = test_client.post(
            "/entries",
            json={"user_id": str(test_user_id), "content": "Test content"},
        )
        
        assert response.status_code == 500
        assert "Failed to create journal entry" in response.json()["detail"]
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "entry-ingestor"
        assert data["version"] == "1.0.0"
