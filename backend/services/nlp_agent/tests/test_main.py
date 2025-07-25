"""Tests for NLP agent FastAPI endpoints."""

import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Mock Google Cloud modules before importing app modules
sys.modules['google'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.language_v2'] = MagicMock()

from shared import AnalysisPayload, SentimentResult


class TestNLPEndpoints:
    """Test cases for NLP endpoints."""
    
    @patch('services.nlp_agent.app.gcp_client.analyze_text')
    def test_analyze_endpoint_success(self, mock_analyze_text):
        """Test successful text analysis."""
        # Import here after mocking
        from services.nlp_agent.app.main import app
        
        # Configure the mock to return predictable result
        mock_analyze_text.return_value = AnalysisPayload(
            sentiment=SentimentResult(label="POSITIVE", score=0.8),
            topics=["testing", "mocking"]
        )

        # Call the API
        client = TestClient(app)
        response = client.post("/analyze", json={"text": "This is a test"})

        # Assert the results
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"]["label"] == "POSITIVE"
        assert data["sentiment"]["score"] == 0.8
        assert data["topics"] == ["testing", "mocking"]
        
        # Verify the mock was called with correct argument
        mock_analyze_text.assert_called_once_with("This is a test")
    
    def test_analyze_endpoint_validation_error(self):
        """Test analysis with invalid input."""
        from services.nlp_agent.app.main import app
        
        client = TestClient(app)
        response = client.post(
            "/analyze",
            json={"text": ""}  # Empty text should fail validation
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('services.nlp_agent.app.main.analyze_text')
    def test_analyze_endpoint_gcp_error(self, mock_analyze_text):
        """Test handling of GCP client errors."""
        from services.nlp_agent.app.main import app
        
        # Mock the GCP client to raise an exception
        mock_analyze_text.side_effect = Exception("GCP error")
        
        client = TestClient(app)
        response = client.post(
            "/analyze",
            json={"text": "This should fail"}
        )
        
        assert response.status_code == 500
        assert "Error during text analysis" in response.json()["detail"]
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        from services.nlp_agent.app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "nlp-agent"
        assert data["version"] == "1.0.0"
