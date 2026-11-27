import json
from pathlib import Path

import httpx
import pytest

from pipelines.serenescapes_etl.annotate import (
    GeminiAnnotator,
    HeuristicAnnotator,
    OllamaAnnotator,
    parse_llm_json,
    to_golden,
)
from pipelines.serenescapes_etl.config import NAIROBI_BBOX
from pipelines.serenescapes_etl.extract import (
    best_match,
    build_overpass_query,
    parse_overpass,
)
from pipelines.serenescapes_etl.load import (
    FIELDS,
    STATUS_NEW,
    airtable_row_to_place,
    golden_to_place,
    load_to_airtable,
    seed_to_place,
    to_airtable_fields,
)
from pipelines.serenescapes_etl.models import POI
from pipelines.serenescapes_etl.run import SEED_FILE

FIX = Path(__file__).parent / "fixtures" / "overpass_sample.json"


def pois():
    return parse_overpass(json.loads(FIX.read_text()))


def test_nairobi_bbox_is_south_west_north_east_and_in_kenya():
    s, w, n, e = NAIROBI_BBOX
    assert s < n < 0 and 36 < w < e < 38  # southern hemisphere, east of Greenwich
    q = build_overpass_query(NAIROBI_BBOX)
    assert "(-1.45,36.65,-1.15,37.0)" in q and q.startswith("[out:json]")


def test_bbox_validation_rejects_old_bug():
    with pytest.raises(ValueError):
        build_overpass_query((-1.35, -36.75, -1.20, -36.85))  # west > east


def test_parse_keeps_named_relevant_places_and_dedupes():
    ps = pois()
    assert [p.name for p in ps] == ["Karura Forest", "Ngong Hills Viewpoint",
                                    "Nairobi National Museum", "Oloolua River Trail"]
    assert {p.osm_id for p in ps} == {"way/1001", "node/2002", "way/3003", "relation/6006"}
    assert ps[0].category == "forest"


def test_heuristic_annotation_and_spectrum():
    by = {p.name: to_golden(p, HeuristicAnnotator().annotate(p)) for p in pois()}
    forest, view, museum, trail = (by["Karura Forest"], by["Ngong Hills Viewpoint"],
                                   by["Nairobi National Museum"], by["Oloolua River Trail"])
    assert forest.spectrum.biophilia > museum.spectrum.biophilia
    assert view.spectrum.awe > forest.spectrum.awe
    assert museum.spectrum.novelty >= 4
    assert "heights" in view.spectrum.trigger_warnings
    assert trail.annotation.sub_factors.water_present == 1  # "River" in name
    assert forest.annotation.social_density < 2.5  # fee lowers crowding


def test_parse_llm_json_validates_and_clamps():
    raw = json.dumps({"sub_factors": {"navigational": 2, "sensory": 7, "rules": 1, "immersion": 5,
                                      "biodiversity": 4, "water_present": 1, "vastness": 3,
                                      "stimulus_power": 3, "cultural": 2, "experiential": 2,
                                      "sensory_surprise": 3},
                      "social_density": 2, "trigger_warnings": ["wildlife", "made_up"],
                      "rationale": "Dense forest."})
    a = parse_llm_json(f"```json\n{raw}\n```", "gemini")
    assert a.sub_factors.sensory == 5 and a.trigger_warnings == ["wildlife"]
    with pytest.raises(ValueError):
        parse_llm_json('{"oops": 1}', "gemini")


def _mock_client(payload):
    return httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json=payload)))


def test_gemini_reads_candidates_shape_not_openai():
    body = {"sub_factors": {k: 3 for k in ["navigational", "sensory", "rules", "immersion",
            "biodiversity", "vastness", "stimulus_power", "cultural", "experiential",
            "sensory_surprise"]} | {"water_present": 0}, "social_density": 3,
            "trigger_warnings": [], "rationale": "ok"}
    client = _mock_client({"candidates": [{"content": {"parts": [{"text": json.dumps(body)}]}}]})
    a = GeminiAnnotator("k", "gemini-2.0-flash", "Nairobi", client).annotate(pois()[0])
    assert a.annotator == "gemini" and a.rationale == "ok"


def test_llm_failure_falls_back_to_heuristic():
    client = httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(500)))
    a = OllamaAnnotator("http://x", "m", "Nairobi", client).annotate(pois()[0])
    assert a.annotator == "heuristic" and "fallback" in a.rationale


def test_foursquare_entity_resolution():
    p = POI(osm_id="way/1", name="Karura Forest", latitude=-1.2386, longitude=36.8344, category="forest")
    near_same = {"name": "Karura Forest Reserve", "latitude": -1.2390, "longitude": 36.8350}
    far_same = {"name": "Karura Forest", "latitude": -1.30, "longitude": 36.90}
    other = {"name": "Java House", "latitude": -1.2386, "longitude": 36.8344}
    assert best_match(p, [other, far_same, near_same]) is near_same
    assert best_match(p, [other, far_same]) is None


class FakeTable:
    def __init__(self, rows=None):
        self.rows, self.created, self.updated = rows or [], [], []

    def all(self, fields=None, formula=None):
        return self.rows

    def batch_create(self, recs, typecast=False):
        self.created += recs

    def batch_update(self, recs, typecast=False):
        self.updated += recs


def test_airtable_load_creates_new_and_never_touches_status_of_existing():
    golden = [to_golden(p, HeuristicAnnotator().annotate(p)) for p in pois()]
    t = FakeTable([{"id": "rec1", "fields": {"OSM ID": "way/1001"}}])
    assert load_to_airtable(golden, t) == {"created": 3, "updated": 1}
    assert all(r["Status"] == STATUS_NEW for r in t.created)
    assert "Status" not in t.updated[0]["fields"]
    assert not any(k.startswith("Final") for k in t.updated[0]["fields"])


def test_final_values_win_over_estimates():
    g = to_golden(pois()[0], HeuristicAnnotator().annotate(pois()[0]))
    fields = to_airtable_fields(g) | {"Final Biophilia": 6.0, "Final Triggers": "wildlife, darkness"}
    row = airtable_row_to_place(fields)
    assert row["biophilia"] == 6.0 and json.loads(row["trigger_warnings"]) == ["wildlife", "darkness"]
    assert row["cognitive_load"] == g.spectrum.cognitive_load
    assert airtable_row_to_place({"Name": "broken"}) is None


def test_direct_postgres_rows_match_the_places_table():
    g = to_golden(pois()[0], HeuristicAnnotator().annotate(pois()[0]))
    row = golden_to_place(g)
    assert row["place_id"] == g.poi.osm_id and row["status"] == "approved"
    assert all(row[f] == getattr(g.spectrum, f) for f in FIELDS)
    assert json.loads(row["trigger_warnings"]) == list(g.spectrum.trigger_warnings)


def test_every_seed_place_converts_for_load_postgres():
    seeds = json.loads(SEED_FILE.read_text())
    rows = [seed_to_place(s) for s in seeds]
    assert len(rows) == len(seeds) >= 10
    assert all(r["status"] == "approved" and isinstance(json.loads(r["trigger_warnings"]), list) for r in rows)
