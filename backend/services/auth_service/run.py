#!/usr/bin/env python3
"""
Authentication Service Startup Script

This script starts the authentication service with proper configuration
and database initialization.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from services.auth_service.database import create_tables
from services.auth_service.config import get_settings

def main():
    """Start the authentication service"""
    print("🚀 Starting AURA Journal Authentication Service...")
    
    # Get configuration
    settings = get_settings()
    
    # Create database tables if they don't exist
    try:
        create_tables()
        print("✓ Database tables initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    # Start the server
    print(f"🌐 Starting server on {settings.host}:{settings.port}")
    print(f"📚 API documentation available at: http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        "services.auth_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()