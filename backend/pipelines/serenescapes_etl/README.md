# SereneScapes places pipeline

Builds the curated places knowledge base without Vertex AI or paid APIs.

```
OSM Overpass ─► (Foursquare, optional) ─► annotate ─► Airtable "Needs Review" ─► human review ─► "Approved" ─► Postgres places ─► Wellness Engine
```

Replaces the `serenescapes-prod-101` Kaggle notebook. Fixes carried over:
correct Nairobi bounding box (south, west, north, east), Gemini response parsed
as `candidates[0].content.parts[0].text`, no KFP type errors, Kaggle secrets
instead of Colab secrets, and all rubric fields scored (not just two).

## Stages

Run from `backend/` (`PYTHONPATH=.`):

```bash
python -m pipelines.serenescapes_etl.run extract                 # data/serenescapes/raw.jsonl
python -m pipelines.serenescapes_etl.run annotate                # heuristic by default
python -m pipelines.serenescapes_etl.run annotate --annotator gemini   # needs GEMINI_API_KEY (free tier)
python -m pipelines.serenescapes_etl.run load                    # Airtable, status "Needs Review"
python -m pipelines.serenescapes_etl.run sync                    # Approved rows -> Postgres
```

Each stage writes a JSONL checkpoint, so a failed run resumes without re-calling APIs.
On Kaggle, see `kaggle.py`.

## Environment

| Variable | Needed for | Default |
|---|---|---|
| `BBOX` | extract | Nairobi `[-1.45,36.65,-1.15,37.0]` |
| `FOURSQUARE_API_KEY` | optional enrichment | skipped if blank |
| `ANNOTATOR` | annotate | `heuristic` (`gemini`, `ollama`) |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | gemini annotator | `gemini-2.0-flash` |
| `OLLAMA_URL`, `OLLAMA_MODEL` | ollama annotator | `http://localhost:11434`, `qwen2.5:3b` |
| `AIRTABLE_PAT`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE_NAME` | load, sync | table `Places` |
| `DATABASE_URL` | sync | e.g. `postgresql+psycopg2://aura:...@localhost:5433/aura_journal` |

## Airtable table "Places"

The pipeline creates options automatically (`typecast`). Fields:

| Field | Type | Written by |
|---|---|---|
| OSM ID | Single line text (unique key) | pipeline |
| Name, Category | Single line text | pipeline |
| Latitude, Longitude | Number (decimal) | pipeline |
| Status | Single select: Needs Review, Approved, Rejected | pipeline sets Needs Review once; curators change it |
| Annotator, Rationale, Sub-factors | Text | pipeline |
| Est Cognitive Load, Est Biophilia, Est Awe, Est Novelty, Est Social Density | Number | pipeline |
| Est Triggers | Text (comma separated) | pipeline |
| Final Cognitive Load, Final Biophilia, Final Awe, Final Novelty, Final Social Density | Number | curator (optional, overrides Est) |
| Final Triggers, Summary | Text | curator |

The pipeline never writes `Status` on existing rows or any `Final *` field, so re-runs are safe.
Free Airtable plans cap records per base (1,000 at the time of writing): enough for the 100-300 place pilot.
