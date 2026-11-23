"""Curated places (Dataset 1, "the What") repositories.

``file``: a JSON list, used for development and tests (seed data).
``postgres``: the ``places`` table filled by the pipeline's Airtable sync.
Only places whose status is ``approved`` (or ``seed`` from the file) are served.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from shared.mental_spectrum import Spectrum


class Place(BaseModel):
    place_id: str
    name: str
    category: str
    latitude: float
    longitude: float
    spectrum: Spectrum
    status: str = "approved"
    summary: str | None = None


class PlaceRepository(Protocol):
    def list_servable(self) -> list[Place]: ...


SERVABLE = {"approved", "seed"}


class FilePlaceRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._cache: list[Place] | None = None

    def list_servable(self) -> list[Place]:
        if self._cache is None:
            rows = json.loads(self.path.read_text())
            self._cache = [p for p in (Place.model_validate(r) for r in rows) if p.status in SERVABLE]
        return self._cache


class PostgresPlaceRepository:
    """Reads the ``places`` table written by ``pipelines/serenescapes_etl`` sync."""

    QUERY = (
        "SELECT place_id, name, category, latitude, longitude, cognitive_load, biophilia, "
        "awe, novelty, social_density, trigger_warnings, status, summary "
        "FROM places WHERE status = 'approved'"
    )

    def __init__(self, database_url: str) -> None:
        from sqlalchemy import create_engine

        self.engine = create_engine(database_url, pool_pre_ping=True)

    def list_servable(self) -> list[Place]:
        from sqlalchemy import text

        with self.engine.connect() as conn:
            rows = conn.execute(text(self.QUERY)).mappings().all()
        out = []
        for r in rows:
            tw = r["trigger_warnings"] or []
            if isinstance(tw, str):
                tw = json.loads(tw)
            out.append(Place(
                place_id=r["place_id"], name=r["name"], category=r["category"],
                latitude=r["latitude"], longitude=r["longitude"], status=r["status"],
                summary=r["summary"],
                spectrum=Spectrum(
                    cognitive_load=r["cognitive_load"], biophilia=r["biophilia"], awe=r["awe"],
                    novelty=r["novelty"], social_density=r["social_density"], trigger_warnings=tw,
                ),
            ))
        return out
