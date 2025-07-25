"""Shared database utilities and connection management."""

from typing import Generator

import pymongo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import DatabaseSettings


class DatabaseManager:
    """Manages database connections for PostgreSQL and MongoDB."""
    
    def __init__(self, settings: DatabaseSettings) -> None:
        self.settings = settings
        self._engine = None
        self._session_local = None
        self._mongo_client = None
        self._mongo_db = None
    
    @property
    def engine(self):
        """Get or create SQLAlchemy engine."""
        if self._engine is None:
            self._engine = create_engine(self.settings.database_url)
        return self._engine
    
    @property
    def session_local(self):
        """Get or create SQLAlchemy session factory."""
        if self._session_local is None:
            self._session_local = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
        return self._session_local
    
    def get_db(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        db = self.session_local()
        try:
            yield db
        finally:
            db.close()
    
    @property
    def mongo_client(self):
        """Get or create MongoDB client."""
        if self._mongo_client is None:
            self._mongo_client = pymongo.MongoClient(self.settings.mongodb_url)
        return self._mongo_client
    
    @property
    def mongo_db(self):
        """Get MongoDB database."""
        if self._mongo_db is None:
            self._mongo_db = self.mongo_client["aura_journal_insight"]
        return self._mongo_db
    
    def close_connections(self) -> None:
        """Close all database connections."""
        if self._engine:
            self._engine.dispose()
        if self._mongo_client:
            self._mongo_client.close()
