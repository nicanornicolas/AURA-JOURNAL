"""Wellness Engine API.

Endpoints
- POST /v1/ears/analyze   text -> emotions, need states, valence/energy, safety
- POST /v1/brain/profile  need states -> target Mental Spectrum profile
- POST /v1/recommend      text or need states -> ranked places (or safety resources)
- POST /analyze           Aura Journal compatible (sentiment + topics, plus extras)
- GET  /health
"""

from __future__ import annotations

import threading
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import Depends, FastAPI, HTTPException, Request
from loguru import logger
from pydantic import BaseModel, Field, model_validator

from shared import (
    AnalysisPayload,
    HealthResponse,
    NeedState,
    SafetySignal,
    SentimentResult,
    TextPayload,
)

from .brain.places import FilePlaceRepository, PlaceRepository, PostgresPlaceRepository
from .brain.profile import Heuristics, NeedsProfile, build_profile
from .brain.ranking import Recommendation, rank_places
from .config import Settings, get_settings
from .ears import EarsResult, EarsService, build_ears_service
from .ears.service import NEGATIVE, POSITIVE

VERSION = "0.1.0"


@dataclass
class Engine:
    settings: Settings
    ears: EarsService
    heuristics: Heuristics
    places: PlaceRepository


def build_engine(settings: Settings) -> Engine:
    places: PlaceRepository
    if settings.places_source == "postgres":
        places = PostgresPlaceRepository(settings.database_url)
    else:
        places = FilePlaceRepository(settings.places_file)
    return Engine(
        settings=settings,
        ears=build_ears_service(settings),
        heuristics=Heuristics.load(settings.heuristics_file),
        places=places,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not hasattr(app.state, "engine"):
        app.state.engine = build_engine(get_settings())
    provider = app.state.engine.ears.provider
    if hasattr(provider, "warm_up"):
        # Load models in the background so /health answers while they download.
        threading.Thread(target=provider.warm_up, daemon=True).start()
    logger.info(f"Wellness Engine {VERSION} ready (ears={app.state.engine.ears.provider.name})")
    yield


app = FastAPI(title="SereneScapes Wellness Engine", version=VERSION, lifespan=lifespan)


def get_engine(request: Request) -> Engine:
    return request.app.state.engine


# ---------- request / response models ----------

class ProfileRequest(BaseModel):
    needs: list[NeedState]


class RecommendRequest(BaseModel):
    text: str | None = Field(None, description="Free text; runs Ears first")
    needs: list[NeedState] | None = Field(None, description="Pre-computed need states (e.g. from Aura Journal)")
    avoid_triggers: list[str] = Field(default_factory=list)
    latitude: float | None = None
    longitude: float | None = None
    max_km: float | None = None
    limit: int = Field(5, ge=1, le=20)

    @model_validator(mode="after")
    def _need_input(self) -> RecommendRequest:
        if not self.text and not self.needs:
            raise ValueError("provide either text or needs")
        return self


class RecommendResponse(BaseModel):
    safety: SafetySignal
    profile: NeedsProfile | None
    recommendations: list[Recommendation]
    ears: EarsResult | None = None


# ---------- endpoints ----------

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service="wellness-engine", version=VERSION)


@app.post("/v1/ears/analyze", response_model=EarsResult)
def ears_analyze(payload: TextPayload, engine: Engine = Depends(get_engine)) -> EarsResult:
    return engine.ears.analyze(payload.text)


@app.post("/v1/brain/profile", response_model=NeedsProfile)
def brain_profile(payload: ProfileRequest, engine: Engine = Depends(get_engine)) -> NeedsProfile:
    return build_profile(payload.needs, engine.heuristics)


@app.post("/v1/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest, engine: Engine = Depends(get_engine)) -> RecommendResponse:
    ears = engine.ears.analyze(payload.text) if payload.text else None
    safety = ears.safety if ears else SafetySignal()
    if safety.level == "crisis":
        # Never recommend outings in a crisis: show support resources instead.
        return RecommendResponse(safety=safety, profile=None, recommendations=[], ears=ears)

    needs = payload.needs if payload.needs is not None else (ears.needs if ears else [])
    profile = build_profile(needs, engine.heuristics)
    near = (payload.latitude, payload.longitude) if payload.latitude is not None and payload.longitude is not None else None
    try:
        places = engine.places.list_servable()
    except Exception as e:  # database down etc.
        logger.error(f"Could not load places: {e}")
        raise HTTPException(503, "Places knowledge base unavailable") from e
    recs = rank_places(places, profile, engine.heuristics, set(payload.avoid_triggers),
                       near, payload.max_km, payload.limit)
    return RecommendResponse(safety=safety, profile=profile, recommendations=recs, ears=ears)


@app.post("/analyze", response_model=AnalysisPayload)
def analyze_compat(payload: TextPayload, engine: Engine = Depends(get_engine)) -> AnalysisPayload:
    """Drop-in replacement for the old Google NLP agent used by the entry ingestor."""
    r = engine.ears.analyze(payload.text)
    label = "POSITIVE" if r.valence > 0.25 else "NEGATIVE" if r.valence < -0.25 else "NEUTRAL"
    labels = {e.label for e in r.emotions}
    if label == "NEUTRAL" and labels & POSITIVE and labels & NEGATIVE:
        label = "MIXED"
    topics = [n.state for n in r.needs[:3]] + [e.label for e in r.emotions[:3] if e.label != "neutral"]
    return AnalysisPayload(
        sentiment=SentimentResult(label=label, score=r.valence),
        topics=list(dict.fromkeys(topics))[:5],
        language=r.language,
        emotions=r.emotions,
        needs=r.needs,
        safety=r.safety,
    )
