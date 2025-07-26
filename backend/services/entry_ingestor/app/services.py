"""Business logic for the entry ingestor service."""

from typing import Optional, Protocol

import httpx
from loguru import logger
from sqlalchemy.orm import Session

from shared import AnalysisPayload, EntryCreate, TextPayload
from .models import JournalEntry


class NLPClient(Protocol):
    """Protocol for NLP analysis clients."""
    
    def analyze_text(self, text: str) -> Optional[AnalysisPayload]:
        """Analyze text and return analysis payload."""
        ...


class InsightStorage(Protocol):
    """Protocol for storing insights."""
    
    def store_insight(self, entry_id: str, user_id: str, analysis: AnalysisPayload) -> None:
        """Store analysis insight."""
        ...


class HTTPNLPClient:
    """HTTP-based NLP client implementation."""
    
    def __init__(self, nlp_url: str, timeout: float = 5.0) -> None:
        self.nlp_url = nlp_url
        self.timeout = timeout
    
    def analyze_text(self, text: str) -> Optional[AnalysisPayload]:
        """Analyze text using HTTP NLP service."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.nlp_url,
                    json=TextPayload(text=text).model_dump()
                )
                response.raise_for_status()
                return AnalysisPayload(**response.json())
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.warning(f"NLP service unavailable: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling NLP service: {e}")
            return None


class MongoInsightStorage:
    """MongoDB-based insight storage implementation."""
    
    def __init__(self, mongo_db) -> None:
        self.mongo_db = mongo_db
    
    def store_insight(self, entry_id: str, user_id: str, analysis: AnalysisPayload) -> None:
        """Store analysis insight in MongoDB."""
        try:
            insights_collection = self.mongo_db["insights"]
            insight_doc = {
                "entry_id": entry_id,
                "user_id": user_id,
                **analysis.model_dump()
            }
            insights_collection.insert_one(insight_doc)
            logger.info(f"Stored insight for entry {entry_id}")
        except Exception as e:
            logger.error(f"Failed to store insight: {e}")


class EntryService:
    """Service for managing journal entries."""
    
    def __init__(
        self,
        nlp_client: NLPClient,
        insight_storage: InsightStorage
    ) -> None:
        self.nlp_client = nlp_client
        self.insight_storage = insight_storage
    
    def create_entry(self, db: Session, entry_data: EntryCreate) -> JournalEntry:
        """Create a new journal entry with optional analysis."""
        logger.info(f"Creating new journal entry for user {entry_data.user_id}")
        
        # Step 1: Save the entry to PostgreSQL
        db_entry = JournalEntry(
            user_id=entry_data.user_id,
            content=entry_data.content
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        # Step 2: Try to get analysis from NLP service
        logger.info(f"Requesting analysis from NLP Agent for entry {db_entry.entry_id}")
        analysis = self.nlp_client.analyze_text(entry_data.content)
        
        if analysis:
            logger.success(f"Successfully received analysis for entry {db_entry.entry_id}")
            # Step 3: Store analysis in MongoDB
            self.insight_storage.store_insight(
                str(db_entry.entry_id),
                str(db_entry.user_id),
                analysis
            )
            # Dynamically attach analysis to the entry for the response
            setattr(db_entry, 'analysis', analysis)
            logger.info(f"Created entry {db_entry.entry_id} with analysis")
        else:
            logger.warning(
                f"Could not get analysis from NLP Agent for entry {db_entry.entry_id}. "
                "Entry created without analysis."
            )
            # Set analysis to None for consistency
            setattr(db_entry, 'analysis', None)
            logger.info(f"Created entry {db_entry.entry_id} without analysis")
        
        return db_entry
