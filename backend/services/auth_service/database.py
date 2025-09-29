"""
Authentication Service Database Models and Configuration

This module defines the SQLAlchemy models for user authentication
and session management with proper database schema.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
import os
from typing import Generator

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/aura_journal"
)

Base = declarative_base()

class User(Base):
    """
    User model for authentication
    
    Requirements: 1.1, 1.2, 1.5, 1.6
    - User account management
    - Password storage with hashing
    - Account status tracking
    """
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship to user sessions
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_active', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<User(user_id='{self.user_id}', email='{self.email}')>"

class UserSession(Base):
    """
    User session model for JWT refresh token management
    
    Requirements: 1.5, 1.6
    - Session tracking for token validation
    - Refresh token management
    - Session invalidation for logout
    """
    __tablename__ = "user_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    refresh_token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="sessions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_sessions_user_id', 'user_id'),
        Index('idx_user_sessions_active', 'is_active'),
        Index('idx_user_sessions_expires_at', 'expires_at'),
        Index('idx_user_sessions_user_active', 'user_id', 'is_active'),
    )
    
    def __repr__(self):
        return f"<UserSession(session_id='{self.session_id}', user_id='{self.user_id}')>"

# Database engine and session configuration
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Generator:
    """
    Dependency to get database session
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
    - Provides database session for all auth operations
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database tables
if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully")