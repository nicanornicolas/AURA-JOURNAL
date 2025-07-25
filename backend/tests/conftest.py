"""Global test configuration and fixtures."""

import pytest
import uuid
import sys
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock

# Mock Google Cloud modules globally for all tests
sys.modules['google'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.language_v2'] = MagicMock()


@pytest.fixture
def sample_user_id():
    """Sample user UUID for testing."""
    return uuid.uuid4()


@pytest.fixture
def sample_entry_id():
    """Sample entry UUID for testing."""
    return uuid.uuid4()


@pytest.fixture
def sample_timestamp():
    """Sample timestamp for testing."""
    return datetime.now(timezone.utc)


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_mongo_db():
    """Mock MongoDB database."""
    db = Mock()
    collection = Mock()
    db.__getitem__.return_value = collection
    return db
