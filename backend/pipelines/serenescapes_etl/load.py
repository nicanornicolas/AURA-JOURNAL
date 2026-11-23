"""LOAD: push golden records to Airtable (curation queue) and sync approved
places from Airtable into Postgres (what the Wellness Engine serves).

Airtable is the human-in-the-loop step. The pipeline only ever writes "Est *"
fields; curators set "Final *" fields and Status. Re-running the pipeline never
overwrites a curator's work.
"""

from __future__ import annotations

import json
from collections.abc import Iterable

from loguru import logger

from .models import GoldenRecord

STATUS_NEW = "Needs Review"
STATUS_APPROVED = "Approved"
FIELDS = ("cognitive_load", "biophilia", "awe", "novelty", "social_density")


def _title(f: str) -> str:
    return f.replace("_", " ").title()


def to_airtable_fields(g: GoldenRecord) -> dict:
    s = g.spectrum
    fields = {
        "OSM ID": g.poi.osm_id,
        "Name": g.poi.name,
        "Category": g.poi.category,
        "Latitude": g.poi.latitude,
        "Longitude": g.poi.longitude,
        "Annotator": g.annotation.annotator,
        "Rationale": g.annotation.rationale,
        "Sub-factors": json.dumps(g.annotation.sub_factors.model_dump()),
        "Est Triggers": ", ".join(s.trigger_warnings),
    }
    for f in FIELDS:
        fields[f"Est {_title(f)}"] = getattr(s, f)
    return fields


def load_to_airtable(records: Iterable[GoldenRecord], table) -> dict[str, int]:
    """Create new places as 'Needs Review'; refresh estimates on existing ones.

    ``table`` is a ``pyairtable.Table`` (or anything with all/batch_create/batch_update).
    """
    existing = {r["fields"].get("OSM ID"): r["id"] for r in table.all(fields=["OSM ID"])}
    creates, updates = [], []
    for g in records:
        fields = to_airtable_fields(g)
        rid = existing.get(g.poi.osm_id)
        if rid:
            updates.append({"id": rid, "fields": fields})
        else:
            creates.append({**fields, "Status": STATUS_NEW})
    if creates:
        table.batch_create(creates, typecast=True)
    if updates:
        table.batch_update(updates, typecast=True)
    logger.info(f"Airtable: {len(creates)} created, {len(updates)} refreshed")
    return {"created": len(creates), "updated": len(updates)}


# ---------------- Airtable -> Postgres ----------------

DDL = """
CREATE TABLE IF NOT EXISTS places (
    place_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    cognitive_load REAL NOT NULL,
    biophilia REAL NOT NULL,
    awe REAL NOT NULL,
    novelty REAL NOT NULL,
    social_density REAL NOT NULL,
    trigger_warnings JSONB NOT NULL DEFAULT '[]',
    status TEXT NOT NULL,
    summary TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

UPSERT = """
INSERT INTO places (place_id, name, category, latitude, longitude, cognitive_load, biophilia,
                    awe, novelty, social_density, trigger_warnings, status, summary, updated_at)
VALUES (:place_id, :name, :category, :latitude, :longitude, :cognitive_load, :biophilia,
        :awe, :novelty, :social_density, CAST(:trigger_warnings AS JSONB), :status, :summary, now())
ON CONFLICT (place_id) DO UPDATE SET
    name = EXCLUDED.name, category = EXCLUDED.category, latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude, cognitive_load = EXCLUDED.cognitive_load,
    biophilia = EXCLUDED.biophilia, awe = EXCLUDED.awe, novelty = EXCLUDED.novelty,
    social_density = EXCLUDED.social_density, trigger_warnings = EXCLUDED.trigger_warnings,
    status = EXCLUDED.status, summary = EXCLUDED.summary, updated_at = now()
"""


def airtable_row_to_place(fields: dict) -> dict | None:
    """Final values win over estimates. Returns None if a row is incomplete."""
    try:
        row = {
            "place_id": fields["OSM ID"],
            "name": fields["Name"],
            "category": fields.get("Category", "park"),
            "latitude": float(fields["Latitude"]),
            "longitude": float(fields["Longitude"]),
            "status": "approved",
            "summary": fields.get("Summary"),
        }
        for f in FIELDS:
            v = fields.get(f"Final {_title(f)}", fields.get(f"Est {_title(f)}"))
            row[f] = float(v)
        triggers = fields.get("Final Triggers", fields.get("Est Triggers", "")) or ""
        row["trigger_warnings"] = json.dumps([t.strip() for t in triggers.split(",") if t.strip()])
        return row
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Skipping incomplete Airtable row {fields.get('Name')}: {e}")
        return None


def sync_approved_to_postgres(table, database_url: str) -> int:
    from sqlalchemy import create_engine, text

    rows = [airtable_row_to_place(r["fields"])
            for r in table.all(formula=f"{{Status}}='{STATUS_APPROVED}'")]
    rows = [r for r in rows if r]
    engine = create_engine(database_url)
    with engine.begin() as conn:
        conn.execute(text(DDL))
        for r in rows:
            conn.execute(text(UPSERT), r)
    logger.info(f"Synced {len(rows)} approved places to Postgres")
    return len(rows)
