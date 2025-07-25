"""Unit tests for entry ingestor services."""

import uuid  
from datetime import datetime, timezone
from unittest.mock import Mock, patch
import pytest
from sqlalchemy.orm import Session

from shared import AnalysisPayload, EntryCreate, SentimentResult
from services.entry_ingestor.app.services import EntryService, HTTPNLPClient, MongoInsightStorage
from services.entry_ingestor.app.models import JournalEntry


class TestHTTPNLPClient:
    """Test cases for HTTPNLPClient."""
    
    @pytest.fixture
    def nlp_client(self):
        return HTTPNLPClient("http://test-nlp:8000/analyze")
    
    def test_analyze_text_success(self, nlp_client):
        """Test successful text analysis."""
        mock_response_data = {
            "sentiment": {"label": "POSITIVE", "score": 0.8},
            "topics": ["work", "productivity"]
        }
        
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__enter__.return_value.post.return_value = mock_response
            
            result = nlp_client.analyze_text("I had a great day at work!")
            
            assert result is not None
            assert result.sentiment.label == "POSITIVE"
            assert result.sentiment.score == 0.8
            assert result.topics == ["work", "productivity"]
    
    def test_analyze_text_http_error(self, nlp_client):
        """Test handling of HTTP errors."""
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("HTTP 500")
            mock_client.return_value.__enter__.return_value.post.return_value = mock_response
            
            result = nlp_client.analyze_text("Some text")
            
            assert result is None
    
    def test_analyze_text_request_error(self, nlp_client):
        """Test handling of request errors."""
        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.post.side_effect = Exception("Connection failed")
            
            result = nlp_client.analyze_text("Some text")
            
            assert result is None


class TestMongoInsightStorage:
    """Test cases for MongoInsightStorage."""
    
    @pytest.fixture
    def mock_mongo_db(self):
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        return mock_db
    
    @pytest.fixture
    def storage(self, mock_mongo_db):
        return MongoInsightStorage(mock_mongo_db)
    
    def test_store_insight_success(self, storage, mock_mongo_db):
        """Test successful insight storage."""
        analysis = AnalysisPayload(
            sentiment=SentimentResult(label="POSITIVE", score=0.8),
            topics=["work", "productivity"]
        )
        
        storage.store_insight("entry-123", "user-456", analysis)
        
        # Verify collection was accessed and insert_one was called
        mock_mongo_db.__getitem__.assert_called_once_with("insights")
        mock_collection = mock_mongo_db.__getitem__.return_value
        mock_collection.insert_one.assert_called_once()
        
        # Check the document structure
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["entry_id"] == "entry-123"
        assert call_args["user_id"] == "user-456"
        assert call_args["sentiment"]["label"] == "POSITIVE"
    
    def test_store_insight_error_handling(self, storage, mock_mongo_db):
        """Test error handling in insight storage."""
        mock_collection = mock_mongo_db.__getitem__.return_value
        mock_collection.insert_one.side_effect = Exception("Database error")
        
        analysis = AnalysisPayload(
            sentiment=SentimentResult(label="POSITIVE", score=0.8),
            topics=["work"]
        )
        
        # Should not raise exception, just log error
        storage.store_insight("entry-123", "user-456", analysis)


class TestEntryService:
    """Test cases for EntryService."""
    
    @pytest.fixture
    def mock_nlp_client(self):
        return Mock()
    
    @pytest.fixture
    def mock_insight_storage(self):
        return Mock()
    
    @pytest.fixture
    def mock_db_session(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def entry_service(self, mock_nlp_client, mock_insight_storage):
        return EntryService(mock_nlp_client, mock_insight_storage)
    
    def test_create_entry_with_analysis(self, entry_service, mock_db_session, mock_nlp_client, mock_insight_storage):
        """Test creating an entry with successful analysis."""
        # Setup
        entry_data = EntryCreate(
            user_id=uuid.uuid4(),
            content="I had a great day at work!"
        )
        
        analysis = AnalysisPayload(
            sentiment=SentimentResult(label="POSITIVE", score=0.8),
            topics=["work", "productivity"]
        )
        mock_nlp_client.analyze_text.return_value = analysis
        
        # Mock database operations to simulate SQLAlchemy operations
        with patch('services.entry_ingestor.app.services.JournalEntry') as MockJournalEntry:
            mock_db_entry = Mock()
            mock_db_entry.entry_id = uuid.uuid4()
            mock_db_entry.user_id = entry_data.user_id
            mock_db_entry.content = entry_data.content
            mock_db_entry.timestamp = datetime.now(timezone.utc)
            MockJournalEntry.return_value = mock_db_entry
            
            result = entry_service.create_entry(mock_db_session, entry_data)
        
        # Assertions
        assert result == mock_db_entry
        assert hasattr(result, 'analysis')
        mock_nlp_client.analyze_text.assert_called_once_with(entry_data.content)
        mock_insight_storage.store_insight.assert_called_once_with(
            str(mock_db_entry.entry_id),
            str(mock_db_entry.user_id),
            analysis
        )
    
    def test_create_entry_without_analysis(self, entry_service, mock_db_session, mock_nlp_client, mock_insight_storage):
        """Test creating an entry when analysis fails."""
        # Setup
        entry_data = EntryCreate(
            user_id=uuid.uuid4(),
            content="Some content"
        )
        
        mock_nlp_client.analyze_text.return_value = None
        
        # Mock database operations to simulate SQLAlchemy operations
        with patch('services.entry_ingestor.app.services.JournalEntry') as MockJournalEntry:
            mock_db_entry = Mock()
            mock_db_entry.entry_id = uuid.uuid4()
            mock_db_entry.user_id = entry_data.user_id
            mock_db_entry.content = entry_data.content
            mock_db_entry.timestamp = datetime.now(timezone.utc)
            MockJournalEntry.return_value = mock_db_entry
            
            result = entry_service.create_entry(mock_db_session, entry_data)
        
        # Assertions
        assert result == mock_db_entry
        mock_nlp_client.analyze_text.assert_called_once_with(entry_data.content)
        mock_insight_storage.store_insight.assert_not_called()
