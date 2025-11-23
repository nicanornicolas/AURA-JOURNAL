"""
User session repository implementation.

This module provides CRUD operations for UserSession entities with additional
session-specific query methods for JWT token management and session validation.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
import uuid

try:
    # Try relative imports first (when used as package)
    from ..database import UserSession
    from .base_repository import BaseRepository
except ImportError:
    # Fallback to absolute imports (when used directly)
    from database import UserSession
    from repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository[UserSession, Dict[str, Any], Dict[str, Any]]):
    """
    User session repository with CRUD operations and session-specific queries.
    
    Requirements: 1.5, 1.6
    - Session tracking for token validation
    - Refresh token management
    - Session invalidation for logout
    """
    
    def __init__(self, db: Session):
        """Initialize session repository."""
        super().__init__(UserSession, db)
    
    def _get_id_field(self) -> str:
        """Get the ID field name for UserSession model."""
        return "session_id"
    
    def get_active_session(self, session_id: uuid.UUID) -> Optional[UserSession]:
        """
        Get active session by ID.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Active session instance or None if not found/inactive
        """
        return self.db.query(UserSession).filter(
            and_(
                UserSession.session_id == session_id,
                UserSession.is_active == True
            )
        ).first()
    
    def get_user_sessions(
        self, 
        user_id: uuid.UUID, 
        active_only: bool = True
    ) -> List[UserSession]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User UUID
            active_only: If True, return only active sessions
            
        Returns:
            List of user session instances
        """
        query = self.db.query(UserSession).filter(UserSession.user_id == user_id)
        
        if active_only:
            query = query.filter(UserSession.is_active == True)
        
        return query.order_by(UserSession.created_at.desc()).all()
    
    def create_session(
        self, 
        user_id: uuid.UUID, 
        refresh_token_hash: str, 
        expires_at: datetime
    ) -> UserSession:
        """
        Create new user session.
        
        Args:
            user_id: User UUID
            refresh_token_hash: Hashed refresh token
            expires_at: Session expiration datetime
            
        Returns:
            Created session instance
        """
        session_data = {
            "user_id": user_id,
            "refresh_token_hash": refresh_token_hash,
            "expires_at": expires_at
        }
        
        return self.create(session_data)
    
    def update_refresh_token(
        self, 
        session_id: uuid.UUID, 
        refresh_token_hash: str, 
        expires_at: datetime
    ) -> Optional[UserSession]:
        """
        Update session refresh token and expiration.
        
        Args:
            session_id: Session UUID
            refresh_token_hash: New hashed refresh token
            expires_at: New expiration datetime
            
        Returns:
            Updated session instance or None if not found
        """
        return self.update(session_id, {
            "refresh_token_hash": refresh_token_hash,
            "expires_at": expires_at
        })
    
    def invalidate_session(self, session_id: uuid.UUID) -> bool:
        """
        Invalidate a session (mark as inactive).
        
        Args:
            session_id: Session UUID
            
        Returns:
            True if session was invalidated, False if not found
        """
        session = self.get_by_id(session_id)
        if not session:
            return False
        
        session.is_active = False
        self.db.commit()
        return True
    
    def invalidate_user_sessions(self, user_id: uuid.UUID) -> int:
        """
        Invalidate all sessions for a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            Number of sessions invalidated
        """
        sessions = self.get_user_sessions(user_id, active_only=True)
        count = 0
        
        for session in sessions:
            session.is_active = False
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions by marking them as inactive.
        
        Returns:
            Number of sessions cleaned up
        """
        current_time = datetime.now(timezone.utc)
        
        expired_sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.is_active == True,
                UserSession.expires_at < current_time
            )
        ).all()
        
        count = 0
        for session in expired_sessions:
            session.is_active = False
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def get_session_by_token_hash(self, refresh_token_hash: str) -> Optional[UserSession]:
        """
        Get session by refresh token hash.
        
        Args:
            refresh_token_hash: Hashed refresh token
            
        Returns:
            Session instance or None if not found
        """
        return self.db.query(UserSession).filter(
            and_(
                UserSession.refresh_token_hash == refresh_token_hash,
                UserSession.is_active == True
            )
        ).first()
    
    def get_session_stats(self) -> Dict[str, int]:
        """
        Get session statistics.
        
        Returns:
            Dictionary with session statistics
        """
        total_sessions = self.count()
        active_sessions = self.count({"is_active": True})
        
        # Count expired but still marked as active
        current_time = datetime.now(timezone.utc)
        expired_active_sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.is_active == True,
                UserSession.expires_at < current_time
            )
        ).count()
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "inactive_sessions": total_sessions - active_sessions,
            "expired_active_sessions": expired_active_sessions
        }
    
    def get_recent_sessions(
        self, 
        hours: int = 24, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[UserSession]:
        """
        Get sessions created within the last N hours.
        
        Args:
            hours: Number of hours to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recent session instances
        """
        cutoff_time = datetime.now(timezone.utc) - timezone.timedelta(hours=hours)
        
        return self.db.query(UserSession).filter(
            UserSession.created_at > cutoff_time
        ).order_by(UserSession.created_at.desc()).offset(skip).limit(limit).all()