"""Pipeline record types."""

from pydantic import BaseModel, Field

from shared.mental_spectrum import Spectrum, SubFactors


class POI(BaseModel):
    osm_id: str  # e.g. "way/123456" (type + id is unique; bare ids are not)
    name: str
    latitude: float
    longitude: float
    category: str
    tags: dict[str, str] = Field(default_factory=dict)
    foursquare: dict | None = None


class Annotation(BaseModel):
    sub_factors: SubFactors
    social_density: float = 3.0
    trigger_warnings: list[str] = Field(default_factory=list)
    rationale: str = ""
    annotator: str = "heuristic"


class GoldenRecord(BaseModel):
    poi: POI
    annotation: Annotation
    spectrum: Spectrum
