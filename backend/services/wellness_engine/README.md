# SereneScapes Wellness Engine

One shared backend for **SereneScapes** and **Aura Journal**.

- **Ears**: detects language (English or Swahili), emotions, need states
  (overwhelmed, drained, stuck, lonely, anxious, restless, low, curious, content)
  and runs a crisis-language safety screen.
- **Brain**: turns need states into a target Mental Spectrum profile using the
  heuristics corpus (`app/brain/heuristics.yaml`), then ranks curated places.

## Ears providers

| `EARS_PROVIDER` | What runs | RAM | Notes |
|---|---|---|---|
| `lexicon` | Phrase rules (EN + SW) | ~150 MB | No downloads. Good for tests and very small boxes. |
| `hf` | `SamLowe/roberta-base-go_emotions` + `Helsinki-NLP/opus-mt-sw-en` for Swahili, plus the phrase rules for metaphors | ~2 GB | CPU only. Models download on first start into `/models`. |
| `auto` (default) | `hf` if `transformers` is installed, else `lexicon` | | |

The phrase rules always run, because emotion models miss metaphors such as
"running on empty" or "nimelemewa". Sheng is not covered yet.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness |
| POST | `/v1/ears/analyze` | `{"text"}` to emotions, needs, valence, energy, safety |
| POST | `/v1/brain/profile` | `{"needs": [...]}` to target profile |
| POST | `/v1/recommend` | `{"text"}` or `{"needs"}`, optional `avoid_triggers`, `latitude`, `longitude`, `max_km`, `limit` |
| POST | `/analyze` | Aura Journal compatible (sentiment + topics, plus emotions/needs/safety) |

If the safety screen returns `crisis`, `/v1/recommend` returns support resources
and **no** places. Verify the numbers in `SAFETY_RESOURCES` before real users.

## Run locally

```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install fastapi "uvicorn[standard]" pydantic-settings pyyaml loguru sqlalchemy psycopg2-binary
EARS_PROVIDER=lexicon PYTHONPATH=. uvicorn services.wellness_engine.app.main:app --port 8300
curl -s localhost:8300/v1/recommend -H 'content-type: application/json' \
  -d '{"text":"Nimechoka sana, nina msongo wa mawazo","limit":3}'
```

Tests: `PYTHONPATH=. pytest services/wellness_engine/tests -o addopts=""`
