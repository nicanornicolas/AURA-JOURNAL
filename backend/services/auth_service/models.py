"""
Authentication Service Pydantic Models

This module defines the request and response models for the authentication service
with comprehensive validation for user registration, login, and token management.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re

class UserCreate(BaseModel):
    """
    User registration request model
    
    Requirements: 1.1, 1.2
    - Email format validation
    - Password strength requirements
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    first_name: Optional[str] = Field(None, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User last name")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """
        Validate password strength requirements
        - At least 8 characters
        - Contains uppercase letter
        - Contains lowercase letter
        - Contains digit
        - Contains special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        """Validate name fields"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if not re.match(r'^[a-zA-Z\s\-\']+$', v):
                raise ValueError('Name can only contain letters, spaces, hyphens, and apostrophes')
        return v

class UserLogin(BaseModel):
    """
    User login request model
    
    Requirements: 1.3
    - Email and password validation for authentication
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")

class UserResponse(BaseModel):
    """
    User response model (excludes sensitive data)
    
    Requirements: 1.4
    - Safe user data representation
    """
    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    is_active: bool = Field(..., description="User account status")
    is_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    """
    JWT token response model
    
    Requirements: 1.3, 1.5
    - Access and refresh token delivery
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")

class TokenPayload(BaseModel):
    """
    JWT token payload model for internal use
    
    Requirements: 1.4, 1.5
    - Token validation and user identification
    """
    user_id: str = Field(..., description="User ID from token")
    email: str = Field(..., description="User email from token")
    session_id: str = Field(..., description="Session ID for token validation")
    exp: int = Field(..., description="Token expiration timestamp")
    iat: int = Field(..., description="Token issued at timestamp")
    jti: str = Field(..., description="Unique token identifier")
    token_type: str = Field(..., description="Token type (access or refresh)")

class PasswordChangeRequest(BaseModel):
    """
    Password change request model
    
    Future enhancement for password management
    """
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password_strength(cls, v):
        """Apply same password strength validation as registration"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v