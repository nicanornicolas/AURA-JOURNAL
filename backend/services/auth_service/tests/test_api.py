"""
Tests for Authentication API Endpoints

This module tests the FastAPI endpoints for user authentication
including registration, login, token refresh, and profile access.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from ..main import app
from ..database import Base, get_db_session

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_auth_api.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db_session] = override_get_db

@pytest.fixture
def client():
    """Create test client"""
    Base.metadata.create_all(bind=test_engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }

class TestAuthAPI:
    """Test authentication API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_user_registration(self, client, sample_user):
        """Test user registration endpoint"""
        response = client.post("/auth/register", json=sample_user)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == sample_user["email"]
        assert data["first_name"] == sample_user["first_name"]
        assert data["last_name"] == sample_user["last_name"]
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert "user_id" in data
        assert "created_at" in data
    
    def test_duplicate_registration(self, client, sample_user):
        """Test duplicate user registration fails"""
        # Register user first time
        client.post("/auth/register", json=sample_user)
        
        # Try to register same user again
        response = client.post("/auth/register", json=sample_user)
        assert response.status_code == 400
    
    def test_invalid_registration_data(self, client):
        """Test registration with invalid data"""
        # Test weak password
        invalid_user = {
            "email": "test@example.com",
            "password": "weak",
            "first_name": "Test"
        }
        response = client.post("/auth/register", json=invalid_user)
        assert response.status_code == 422
        
        # Test invalid email
        invalid_user = {
            "email": "invalid-email",
            "password": "TestPass123!",
            "first_name": "Test"
        }
        response = client.post("/auth/register", json=invalid_user)
        assert response.status_code == 422
    
    def test_user_login(self, client, sample_user):
        """Test user login endpoint"""
        # Register user first
        client.post("/auth/register", json=sample_user)
        
        # Login
        login_data = {
            "email": sample_user["email"],
            "password": sample_user["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
    
    def test_invalid_login(self, client, sample_user):
        """Test login with invalid credentials"""
        # Register user first
        client.post("/auth/register", json=sample_user)
        
        # Try login with wrong password
        login_data = {
            "email": sample_user["email"],
            "password": "wrong_password"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
    
    def test_get_profile(self, client, sample_user):
        """Test getting user profile"""
        # Register and login user
        client.post("/auth/register", json=sample_user)
        login_response = client.post("/auth/login", json={
            "email": sample_user["email"],
            "password": sample_user["password"]
        })
        tokens = login_response.json()
        
        # Get profile
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.get("/auth/profile", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == sample_user["email"]
        assert data["first_name"] == sample_user["first_name"]
    
    def test_token_refresh(self, client, sample_user):
        """Test token refresh endpoint"""
        # Register and login user
        client.post("/auth/register", json=sample_user)
        login_response = client.post("/auth/login", json={
            "email": sample_user["email"],
            "password": sample_user["password"]
        })
        tokens = login_response.json()
        
        # Refresh token
        headers = {"Authorization": f"Bearer {tokens['refresh_token']}"}
        response = client.post("/auth/refresh", headers=headers)
        assert response.status_code == 200
        
        new_tokens = response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]
    
    def test_logout(self, client, sample_user):
        """Test user logout endpoint"""
        # Register and login user
        client.post("/auth/register", json=sample_user)
        login_response = client.post("/auth/login", json={
            "email": sample_user["email"],
            "password": sample_user["password"]
        })
        tokens = login_response.json()
        
        # Logout
        headers = {"Authorization": f"Bearer {tokens['refresh_token']}"}
        response = client.post("/auth/logout", headers=headers)
        assert response.status_code == 200
        
        # Verify refresh token is invalidated
        refresh_response = client.post("/auth/refresh", headers=headers)
        assert refresh_response.status_code == 401
    
    def test_unauthorized_access(self, client):
        """Test accessing protected endpoints without token"""
        response = client.get("/auth/profile")
        assert response.status_code == 403  # No Authorization header
        
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/profile", headers=headers)
        assert response.status_code == 401