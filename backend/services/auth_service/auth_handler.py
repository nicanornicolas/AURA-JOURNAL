"""
Authentication Handler

This module provides the core authentication logic including JWT token management,
password hashing with bcrypt, user registration, login, and session management.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import hashlib
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import User, UserSession
from .models import UserCreate, UserLogin, TokenResponse, TokenPayload
from .repositories import UserRepository, SessionRepository

class AuthHandler:
    """
    Core authentication handler
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
    - JWT token generation and validation
    - Password hashing with bcrypt
    - User registration and authentication
    - Session management
    """
    
    def __init__(self):
        # JWT configuration
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        
        # Password hashing configuration
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Requirements: 1.2
        - Secure password hashing with salt
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Requirements: 1.3
        - Password verification for authentication
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: str, email: str, session_id: str) -> str:
        """
        Create JWT access token
        
        Requirements: 1.3, 1.4
        - JWT token generation for authenticated requests
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "user_id": user_id,
            "email": email,
            "session_id": session_id,
            "exp": expire,
            "iat": now,
            "jti": str(uuid.uuid4()),  # Unique token ID
            "token_type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str, email: str, session_id: str) -> str:
        """
        Create JWT refresh token
        
        Requirements: 1.5
        - Refresh token generation for token renewal
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "user_id": user_id,
            "email": email,
            "session_id": session_id,
            "exp": expire,
            "iat": now,
            "jti": str(uuid.uuid4()),  # Unique token ID
            "token_type": "refresh"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, expected_type: str = "access") -> TokenPayload:
        """
        Verify and decode JWT token
        
        Requirements: 1.4, 1.5
        - Token validation and payload extraction
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Validate token type
            if payload.get("token_type") != expected_type:
                raise ValueError(f"Invalid token type. Expected {expected_type}")
            
            # Validate expiration
            if datetime.now(timezone.utc) > datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc):
                raise ValueError("Token has expired")
            
            return TokenPayload(**payload)
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    def hash_refresh_token(self, refresh_token: str) -> str:
        """
        Hash refresh token for secure storage
        
        Requirements: 1.5
        - Secure refresh token storage
        """
        return hashlib.sha256(refresh_token.encode()).hexdigest()
    
    async def create_user(self, db: Session, user_data: UserCreate) -> User:
        """
        Create new user account
        
        Requirements: 1.1, 1.2
        - User registration with validation
        - Password hashing
        """
        user_repo = UserRepository(db)
        
        # Check if user already exists
        if user_repo.email_exists(user_data.email):
            raise ValueError("User with this email already exists")
        
        # Hash password
        password_hash = self.hash_password(user_data.password)
        
        try:
            return user_repo.create_user(user_data, password_hash)
        except IntegrityError:
            raise ValueError("User with this email already exists")
    
    async def authenticate_user(self, db: Session, credentials: UserLogin) -> TokenResponse:
        """
        Authenticate user and create session
        
        Requirements: 1.3, 1.4, 1.5
        - User authentication
        - JWT token generation
        - Session creation
        """
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)
        
        # Find user by email
        user = user_repo.get_by_email(credentials.email)
        if not user or not user.is_active:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not self.verify_password(credentials.password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        # Create new session
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        
        # Generate tokens first to get session_id
        temp_session_id = uuid.uuid4()
        access_token = self.create_access_token(str(user.user_id), user.email, str(temp_session_id))
        refresh_token = self.create_refresh_token(str(user.user_id), user.email, str(temp_session_id))
        
        # Create session with hashed refresh token
        refresh_token_hash = self.hash_refresh_token(refresh_token)
        session = session_repo.create_session(user.user_id, refresh_token_hash, expires_at)
        
        # Regenerate tokens with actual session ID
        access_token = self.create_access_token(str(user.user_id), user.email, str(session.session_id))
        refresh_token = self.create_refresh_token(str(user.user_id), user.email, str(session.session_id))
        
        # Update session with new refresh token hash
        session_repo.update_refresh_token(
            session.session_id, 
            self.hash_refresh_token(refresh_token), 
            expires_at
        )
        
        # Update last login
        user_repo.update_last_login(user.user_id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_expire_minutes * 60
        )
    
    async def refresh_tokens(self, db: Session, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token
        
        Requirements: 1.5
        - Token refresh functionality
        - Session validation
        """
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)
        
        # Verify refresh token
        try:
            payload = self.verify_token(refresh_token, "refresh")
        except ValueError:
            raise ValueError("Invalid refresh token")
        
        # Find and validate session
        session = session_repo.get_active_session(uuid.UUID(payload.session_id))
        if not session:
            raise ValueError("Invalid session")
        
        # Verify refresh token hash
        if session.refresh_token_hash != self.hash_refresh_token(refresh_token):
            raise ValueError("Invalid refresh token")
        
        # Check session expiration
        current_time = datetime.now(timezone.utc)
        if current_time > session.expires_at.replace(tzinfo=timezone.utc):
            session_repo.invalidate_session(session.session_id)
            raise ValueError("Session expired")
        
        # Get user
        user = user_repo.get_by_id(session.user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Generate new tokens
        access_token = self.create_access_token(str(user.user_id), user.email, str(session.session_id))
        new_refresh_token = self.create_refresh_token(str(user.user_id), user.email, str(session.session_id))
        
        # Update session with new refresh token hash
        new_expires_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        session_repo.update_refresh_token(
            session.session_id,
            self.hash_refresh_token(new_refresh_token),
            new_expires_at
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=self.access_token_expire_minutes * 60
        )
    
    async def get_current_user(self, db: Session, access_token: str) -> User:
        """
        Get current user from access token
        
        Requirements: 1.4
        - Token validation and user retrieval
        """
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)
        
        # Verify access token
        try:
            payload = self.verify_token(access_token, "access")
        except ValueError:
            raise ValueError("Invalid access token")
        
        # Validate session is still active
        session = session_repo.get_active_session(uuid.UUID(payload.session_id))
        if not session:
            raise ValueError("Invalid session")
        
        # Get user
        user = user_repo.get_by_id(uuid.UUID(payload.user_id))
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        return user
    
    async def logout_user(self, db: Session, refresh_token: str) -> None:
        """
        Logout user and invalidate session
        
        Requirements: 1.6
        - Session invalidation
        """
        session_repo = SessionRepository(db)
        
        try:
            # Verify refresh token to get session ID
            payload = self.verify_token(refresh_token, "refresh")
            
            # Invalidate session
            session_repo.invalidate_session(uuid.UUID(payload.session_id))
        except ValueError:
            # Even if token is invalid, we don't raise an error for logout
            pass