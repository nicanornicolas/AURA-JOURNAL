"""
Tests for Authentication Handler

This module tests the core authentication functionality including
user registration, login, token management, and password hashing.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock

from ..auth_handler import AuthHandler
from ..database import Base, User, UserSession
from ..models import UserCreate, UserLogin

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_auth.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def auth_handler():
    """Create auth handler instance"""
    return AuthHandler()

@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return UserCreate(
        email="test@example.com",
        password="TestPass123!",
        first_name="Test",
        last_name="User"
    )

class TestAuthHandler:
    """Test authentication handler functionality"""
    
    def test_password_hashing(self, auth_handler):
        """Test password hashing and verification"""
        password = "TestPass123!"
        hashed = auth_handler.hash_password(password)
        
        assert hashed != password
        assert auth_handler.verify_password(password, hashed)
        assert not auth_handler.verify_password("wrong_password", hashed)
    
    def test_jwt_token_creation_and_verification(self, auth_handler):
        """Test JWT token creation and verification"""
        user_id = "test-user-id"
        email = "test@example.com"
        session_id = "test-session-id"
        
        # Test access token
        access_token = auth_handler.create_access_token(user_id, email, session_id)
        payload = auth_handler.verify_token(access_token, "access")
        
        assert payload.user_id == user_id
        assert payload.email == email
        assert payload.session_id == session_id
        assert payload.token_type == "access"
        
        # Test refresh token
        refresh_token = auth_handler.create_refresh_token(user_id, email, session_id)
        payload = auth_handler.verify_token(refresh_token, "refresh")
        
        assert payload.user_id == user_id
        assert payload.token_type == "refresh"
    
    @pytest.mark.asyncio
    async def test_user_creation(self, auth_handler, db_session, sample_user_data):
        """Test user registration"""
        user = await auth_handler.create_user(db_session, sample_user_data)
        
        assert user.email == sample_user_data.email
        assert user.first_name == sample_user_data.first_name
        assert user.last_name == sample_user_data.last_name
        assert user.is_active is True
        assert user.is_verified is False
        assert auth_handler.verify_password(sample_user_data.password, user.password_hash)
    
    @pytest.mark.asyncio
    async def test_duplicate_user_creation(self, auth_handler, db_session, sample_user_data):
        """Test duplicate user registration fails"""
        await auth_handler.create_user(db_session, sample_user_data)
        
        with pytest.raises(ValueError, match="User with this email already exists"):
            await auth_handler.create_user(db_session, sample_user_data)
    
    @pytest.mark.asyncio
    async def test_user_authentication(self, auth_handler, db_session, sample_user_data):
        """Test user login and authentication"""
        # Create user first
        await auth_handler.create_user(db_session, sample_user_data)
        
        # Test successful login
        login_data = UserLogin(
            email=sample_user_data.email,
            password=sample_user_data.password
        )
        tokens = await auth_handler.authenticate_user(db_session, login_data)
        
        assert tokens.access_token
        assert tokens.refresh_token
        assert tokens.token_type == "bearer"
        assert tokens.expires_in > 0
        
        # Verify tokens are valid
        access_payload = auth_handler.verify_token(tokens.access_token, "access")
        refresh_payload = auth_handler.verify_token(tokens.refresh_token, "refresh")
        
        assert access_payload.email == sample_user_data.email
        assert refresh_payload.email == sample_user_data.email
    
    @pytest.mark.asyncio
    async def test_invalid_authentication(self, auth_handler, db_session, sample_user_data):
        """Test authentication with invalid credentials"""
        # Create user first
        await auth_handler.create_user(db_session, sample_user_data)
        
        # Test with wrong password
        login_data = UserLogin(
            email=sample_user_data.email,
            password="wrong_password"
        )
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_handler.authenticate_user(db_session, login_data)
        
        # Test with non-existent email
        login_data = UserLogin(
            email="nonexistent@example.com",
            password=sample_user_data.password
        )
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_handler.authenticate_user(db_session, login_data)
    
    @pytest.mark.asyncio
    async def test_token_refresh(self, auth_handler, db_session, sample_user_data):
        """Test token refresh functionality"""
        # Create user and authenticate
        await auth_handler.create_user(db_session, sample_user_data)
        login_data = UserLogin(
            email=sample_user_data.email,
            password=sample_user_data.password
        )
        initial_tokens = await auth_handler.authenticate_user(db_session, login_data)
        
        # Refresh tokens
        new_tokens = await auth_handler.refresh_tokens(db_session, initial_tokens.refresh_token)
        
        assert new_tokens.access_token != initial_tokens.access_token
        assert new_tokens.refresh_token != initial_tokens.refresh_token
        
        # Verify new tokens are valid
        access_payload = auth_handler.verify_token(new_tokens.access_token, "access")
        assert access_payload.email == sample_user_data.email
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, auth_handler, db_session, sample_user_data):
        """Test getting current user from token"""
        # Create user and authenticate
        user = await auth_handler.create_user(db_session, sample_user_data)
        login_data = UserLogin(
            email=sample_user_data.email,
            password=sample_user_data.password
        )
        tokens = await auth_handler.authenticate_user(db_session, login_data)
        
        # Get current user
        current_user = await auth_handler.get_current_user(db_session, tokens.access_token)
        
        assert current_user.user_id == user.user_id
        assert current_user.email == user.email
    
    @pytest.mark.asyncio
    async def test_logout_user(self, auth_handler, db_session, sample_user_data):
        """Test user logout functionality"""
        # Create user and authenticate
        await auth_handler.create_user(db_session, sample_user_data)
        login_data = UserLogin(
            email=sample_user_data.email,
            password=sample_user_data.password
        )
        tokens = await auth_handler.authenticate_user(db_session, login_data)
        
        # Logout user
        await auth_handler.logout_user(db_session, tokens.refresh_token)
        
        # Verify refresh token is no longer valid
        with pytest.raises(ValueError):
            await auth_handler.refresh_tokens(db_session, tokens.refresh_token)