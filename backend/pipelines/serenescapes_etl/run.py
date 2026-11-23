"""SereneScapes places pipeline CLI.

    python -m pipelines.serenescapes_etl.run extract     # OSM (+ Foursquare) -> data/raw.jsonl
    python -m pipelines.serenescapes_etl.run annotate    # raw -> data/golden.jsonl
    python -m pipelines.serenescapes_etl.run load        # golden -> Airtable (Needs Review)
    python -m pipelines.serenescapes_etl.run sync        # Airtable Approved -> Postgres places
    python -m pipelines.serenescapes_etl.run all         # extract + annotate + load

Each stage writes a JSONL checkpoint, so a failed run resumes from the last
stage instead of re-calling every API. Run from backend/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from loguru import logger

from .annotate import make_annotator, to_golden
from .config import PipelineSettings
from .extract import build_overpass_query, enrich_foursquare, fetch_osm, parse_overpass
from .load import load_to_airtable, sync_approved_to_postgres
from .models import POI, GoldenRecord


def _write(path: Path, items) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for it in items:
            f.write(it.model_dump_json() + "\n")
    logger.info(f"Wrote {path}")


def _read(path: Path, model):
    if not path.exists():
        sys.exit(f"{path} not found: run the previous stage first")
    return [model.model_validate_json(line) for line in path.read_text().splitlines() if line.strip()]


def _airtable_table(s: PipelineSettings):
    if not (s.airtable_pat and s.airtable_base_id):
        sys.exit("AIRTABLE_PAT and AIRTABLE_BASE_ID are required for this stage")
    from pyairtable import Api

    return Api(s.airtable_pat).table(s.airtable_base_id, s.airtable_table_name)


def stage_extract(s: PipelineSettings) -> list[POI]:
    data = fetch_osm(build_overpass_query(s.bbox), s.overpass_url)
    pois = parse_overpass(data, s.max_places)
    pois = enrich_foursquare(pois, s.foursquare_api_key, s.foursquare_url, s.foursquare_api_version)
    _write(s.data_dir / "raw.jsonl", pois)
    return pois


def stage_annotate(s: PipelineSettings, annotator: str | None = None) -> list[GoldenRecord]:
    pois = _read(s.data_dir / "raw.jsonl", POI)
    ann = make_annotator(annotator or s.annotator, s)
    golden = [to_golden(p, ann.annotate(p)) for p in pois]
    _write(s.data_dir / "golden.jsonl", golden)
    summary: dict[str, int] = {}
    for g in golden:
        summary[g.annotation.annotator] = summary.get(g.annotation.annotator, 0) + 1
    logger.info(f"Annotated {len(golden)} places: {json.dumps(summary)}")
    return golden


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["extract", "annotate", "load", "sync", "all"])
    ap.add_argument("--annotator", choices=["heuristic", "gemini", "ollama"])
    args = ap.parse_args(argv)
    s = PipelineSettings()

    if args.stage in {"extract", "all"}:
        stage_extract(s)
    if args.stage in {"annotate", "all"}:
        stage_annotate(s, args.annotator)
    if args.stage in {"load", "all"}:
        load_to_airtable(_read(s.data_dir / "golden.jsonl", GoldenRecord), _airtable_table(s))
    if args.stage == "sync":
        if not s.database_url:
            sys.exit("DATABASE_URL is required for sync")
        sync_approved_to_postgres(_airtable_table(s), s.database_url)


if __name__ == "__main__":
    main()
