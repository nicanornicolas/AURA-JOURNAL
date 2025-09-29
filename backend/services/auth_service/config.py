"""
Authentication Service Configuration

This module provides configuration settings for the authentication service
including JWT settings, database configuration, and security parameters.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class AuthSettings(BaseSettings):
    """
    Authentication service settings
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    - Configurable security parameters
    - Environment-based configuration
    """
    
    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Database Configuration
    database_url: str = "postgresql://postgres:password@localhost:5432/aura_journal"
    database_echo: bool = False
    
    # Password Security
    bcrypt_rounds: int = 12
    
    # Rate Limiting (for future implementation)
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # CORS Configuration
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    
    # Service Configuration
    service_name: str = "auth_service"
    service_version: str = "1.0.0"
    port: int = 8001
    host: str = "0.0.0.0"
    
    # Security Headers
    security_headers_enabled: bool = True
    
    class Config:
        env_file = ".env"
        env_prefix = "AUTH_"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

# Global settings instance
settings = AuthSettings()

def get_settings() -> AuthSettings:
    """Get authentication service settings"""
    return settings