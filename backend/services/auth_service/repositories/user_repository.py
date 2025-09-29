"""
User repository implementation.

This module provides CRUD operations for User entities with additional
user-specific query methods for authentication and user management.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timezone
import uuid

try:
    # Try relative imports first (when used as package)
    from ..database import User
    from ..models import UserCreate, UserResponse
    from .base_repository import BaseRepository
except ImportError:
    # Fallback to absolute imports (when used directly)
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from database import User
    from models import UserCreate, UserResponse
    from .base_repository import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, Dict[str, Any]]):
    """
    User repository with CRUD operations and user-specific queries.
    
    Requirements: 1.1, 1.2, 1.5, 1.6
    - User account management
    - Email-based user lookup
    - User status management
    - User authentication support
    """
    
    def __init__(self, db: Session):
        """Initialize user repository."""
        super().__init__(User, db)
    
    def _get_id_field(self) -> str:
        """Get the ID field name for User model."""
        return "user_id"
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email address
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_active_users(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Get all active users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active user instances
        """
        return self.db.query(User).filter(
            User.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_verified_users(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Get all verified users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of verified user instances
        """
        return self.db.query(User).filter(
            and_(User.is_active == True, User.is_verified == True)
        ).offset(skip).limit(limit).all()
    
    def search_users(
        self, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Search users by email, first name, or last name.
        
        Args:
            search_term: Search term to match against user fields
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching user instances
        """
        search_pattern = f"%{search_term}%"
        return self.db.query(User).filter(
            and_(
                User.is_active == True,
                or_(
                    User.email.ilike(search_pattern),
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern)
                )
            )
        ).offset(skip).limit(limit).all()
    
    def create_user(self, user_data: UserCreate, password_hash: str) -> User:
        """
        Create new user with hashed password.
        
        Args:
            user_data: User creation data
            password_hash: Hashed password
            
        Returns:
            Created user instance
            
        Raises:
            IntegrityError: If user with email already exists
        """
        user_dict = user_data.model_dump(exclude={'password'})
        user_dict['password_hash'] = password_hash
        
        return self.create(user_dict)
    
    def update_last_login(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User UUID
            
        Returns:
            Updated user instance or None if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        user.last_login = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def activate_user(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Activate user account.
        
        Args:
            user_id: User UUID
            
        Returns:
            Updated user instance or None if not found
        """
        return self.update(user_id, {"is_active": True})
    
    def deactivate_user(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Deactivate user account.
        
        Args:
            user_id: User UUID
            
        Returns:
            Updated user instance or None if not found
        """
        return self.update(user_id, {"is_active": False})
    
    def verify_user(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Mark user as verified.
        
        Args:
            user_id: User UUID
            
        Returns:
            Updated user instance or None if not found
        """
        return self.update(user_id, {"is_verified": True})
    
    def update_password(self, user_id: uuid.UUID, password_hash: str) -> Optional[User]:
        """
        Update user password.
        
        Args:
            user_id: User UUID
            password_hash: New hashed password
            
        Returns:
            Updated user instance or None if not found
        """
        return self.update(user_id, {"password_hash": password_hash})
    
    def get_user_stats(self) -> Dict[str, int]:
        """
        Get user statistics.
        
        Returns:
            Dictionary with user statistics
        """
        total_users = self.count()
        active_users = self.count({"is_active": True})
        verified_users = self.count({"is_active": True, "is_verified": True})
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "inactive_users": total_users - active_users
        }
    
    def email_exists(self, email: str) -> bool:
        """
        Check if email already exists in the system.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email exists, False otherwise
        """
        return self.db.query(User).filter(User.email == email).first() is not None
    
    def get_users_created_after(
        self, 
        date: datetime, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Get users created after a specific date.
        
        Args:
            date: Date threshold
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of user instances created after the date
        """
        return self.db.query(User).filter(
            User.created_at > date
        ).offset(skip).limit(limit).all()