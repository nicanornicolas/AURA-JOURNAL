"""Business logic for the entry ingestor service."""

import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Optional, Protocol

import httpx
from loguru import logger
from sqlalchemy.orm import Session

from shared import AnalysisPayload, EntryCreate, TextPayload
from .models import JournalEntry, JournalInsight


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
    
    def __init__(self, nlp_url: str, timeout: float = 15.0) -> None:
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


class PostgresInsightStorage:
    """Stores insights in Postgres (JSONB). Default: one database to run on the homelab."""

    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def store_insight(self, entry_id: str, user_id: str, analysis: AnalysisPayload) -> None:
        session = self.session_factory()
        try:
            session.merge(JournalInsight(
                entry_id=uuid.UUID(entry_id),
                user_id=uuid.UUID(user_id),
                analysis=analysis.model_dump(mode="json"),
            ))
            session.commit()
            logger.info(f"Stored insight for entry {entry_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to store insight: {e}")
        finally:
            session.close()


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

    # ------------------------------------------------------------------
    # Reads and edits. Every query is scoped to the owner's user_id, and an
    # entry that belongs to someone else is reported as "not found".
    # ------------------------------------------------------------------

    @staticmethod
    def _attach_analysis(db: Session, entries: list[JournalEntry]) -> list[JournalEntry]:
        ids = [e.entry_id for e in entries]
        found = {}
        if ids:
            rows = db.query(JournalInsight).filter(JournalInsight.entry_id.in_(ids)).all()
            found = {r.entry_id: r.analysis for r in rows}
        for e in entries:
            raw = found.get(e.entry_id)
            setattr(e, "analysis", AnalysisPayload(**raw) if raw else None)
        return entries

    def list_entries(
        self, db: Session, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[JournalEntry], int]:
        q = db.query(JournalEntry).filter(JournalEntry.user_id == user_id)
        total = q.count()
        rows = (
            q.order_by(JournalEntry.timestamp.desc(), JournalEntry.entry_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return self._attach_analysis(db, rows), total

    def get_entry(self, db: Session, user_id: uuid.UUID, entry_id: uuid.UUID) -> Optional[JournalEntry]:
        row = (
            db.query(JournalEntry)
            .filter(JournalEntry.entry_id == entry_id, JournalEntry.user_id == user_id)
            .first()
        )
        return self._attach_analysis(db, [row])[0] if row else None

    def update_entry(
        self, db: Session, user_id: uuid.UUID, entry_id: uuid.UUID, content: str
    ) -> Optional[JournalEntry]:
        row = (
            db.query(JournalEntry)
            .filter(JournalEntry.entry_id == entry_id, JournalEntry.user_id == user_id)
            .first()
        )
        if not row:
            return None
        row.content = content
        db.commit()
        db.refresh(row)
        analysis = self.nlp_client.analyze_text(content)
        if analysis:
            self.insight_storage.store_insight(str(row.entry_id), str(row.user_id), analysis)
            setattr(row, "analysis", analysis)
            return row
        # Analysis failed: drop the stale insight rather than show one for old text.
        db.query(JournalInsight).filter(JournalInsight.entry_id == entry_id).delete()
        db.commit()
        setattr(row, "analysis", None)
        return row

    def delete_entry(self, db: Session, user_id: uuid.UUID, entry_id: uuid.UUID) -> bool:
        row = (
            db.query(JournalEntry)
            .filter(JournalEntry.entry_id == entry_id, JournalEntry.user_id == user_id)
            .first()
        )
        if not row:
            return False
        db.query(JournalInsight).filter(JournalInsight.entry_id == entry_id).delete()
        db.delete(row)
        db.commit()
        return True

    def mood_trends(self, db: Session, user_id: uuid.UUID, days: int = 30) -> dict:
        """Daily mood (average sentiment score) plus the most frequent needs and emotions."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = (
            db.query(JournalEntry.timestamp, JournalInsight.analysis)
            .join(JournalInsight, JournalInsight.entry_id == JournalEntry.entry_id, isouter=True)
            .filter(JournalEntry.user_id == user_id, JournalEntry.timestamp >= since)
            .order_by(JournalEntry.timestamp)
            .all()
        )
        daily: dict[str, list[float]] = {}
        counts: dict[str, int] = {}
        needs: Counter[str] = Counter()
        emotions: Counter[str] = Counter()
        for ts, analysis in rows:
            day = ts.date().isoformat()
            counts[day] = counts.get(day, 0) + 1
            if not analysis:
                continue
            daily.setdefault(day, []).append(float(analysis["sentiment"]["score"]))
            needs.update(n["state"] for n in analysis.get("needs", []) if n.get("score", 0) >= 0.4)
            emotions.update(e["label"] for e in analysis.get("emotions", [])[:3] if e["label"] != "neutral")
        return {
            "days": days,
            "entries": sum(counts.values()),
            "daily": [
                {
                    "date": d,
                    "entries": counts[d],
                    "mood": round(sum(daily[d]) / len(daily[d]), 3) if d in daily else None,
                }
                for d in sorted(counts)
            ],
            "top_needs": [{"state": s, "count": c} for s, c in needs.most_common(5)],
            "top_emotions": [{"label": s, "count": c} for s, c in emotions.most_common(5)],
        }
