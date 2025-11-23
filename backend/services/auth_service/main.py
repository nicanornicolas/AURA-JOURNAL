"""
Authentication Service Main Module

This module provides the FastAPI application for user authentication
with JWT token management, user registration, login, and token refresh.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Optional
import os

from auth_handler import AuthHandler
from models import UserCreate, UserLogin, UserResponse, TokenResponse
from database import get_db_session
from sqlalchemy.orm import Session

# Initialize FastAPI app
app = FastAPI(
    title="AURA Journal Authentication Service",
    description="User authentication and authorization service with JWT tokens",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize auth handler
auth_handler = AuthHandler()
security = HTTPBearer()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth_service"}

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db_session)
):
    """
    Register a new user
    
    Requirements: 1.1, 1.2
    - Validates email format and password strength
    - Creates new user account with hashed password
    """
    try:
        user = await auth_handler.create_user(db, user_data)
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.post("/auth/login", response_model=TokenResponse)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db_session)
):
    """
    Authenticate user and return JWT tokens
    
    Requirements: 1.3, 1.4
    - Validates user credentials
    - Returns JWT access and refresh tokens
    """
    try:
        tokens = await auth_handler.authenticate_user(db, user_credentials)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Refresh JWT access token using refresh token
    
    Requirements: 1.3, 1.5
    - Validates refresh token
    - Returns new access and refresh tokens
    """
    try:
        refresh_token = credentials.credentials
        tokens = await auth_handler.refresh_tokens(db, refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@app.post("/auth/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Logout user and invalidate session
    
    Requirements: 1.6
    - Invalidates current session token
    """
    try:
        refresh_token = credentials.credentials
        await auth_handler.logout_user(db, refresh_token)
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@app.get("/auth/profile", response_model=UserResponse)
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Get current user profile
    
    Requirements: 1.4
    - Validates JWT token and returns user data
    """
    try:
        access_token = credentials.credentials
        user = await auth_handler.get_current_user(db, access_token)
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)