from services.wellness_engine.app.brain.profile import build_profile
from services.wellness_engine.app.brain.ranking import rank_places
from shared import NeedState
from shared.mental_spectrum import SubFactors, compute_spectrum


def test_rubric_formulas_match_definition():
    s = compute_spectrum(SubFactors(navigational=1, sensory=2, rules=2, immersion=5,
                                    biodiversity=4, water_present=1, vastness=5,
                                    stimulus_power=4, cultural=2, experiential=3,
                                    sensory_surprise=1), social_density=2)
    assert s.cognitive_load == 1.6
    assert s.biophilia == 5.6
    assert s.awe == 4.6
    assert s.novelty == 3


def test_overwhelmed_profile_wants_low_load(engine):
    p = build_profile([NeedState(state="overwhelmed", score=1.0)], engine.heuristics)
    assert p.targets["cognitive_load"] <= 2
    assert p.importance["cognitive_load"] == 1.0


def test_empty_needs_use_default(engine):
    p = build_profile([], engine.heuristics)
    assert p.drivers == []
    assert "biophilia" in p.targets


def test_ranking_prefers_quiet_green_for_overwhelm(engine):
    p = build_profile([NeedState(state="overwhelmed", score=1.0)], engine.heuristics)
    recs = rank_places(engine.places.list_servable(), p, engine.heuristics, limit=3)
    names = [r.place.name for r in recs]
    assert "Village Market" not in names
    assert recs[0].fit >= recs[-1].fit


def test_ranking_respects_trigger_warnings(engine):
    p = build_profile([NeedState(state="stuck", score=1.0)], engine.heuristics)
    recs = rank_places(engine.places.list_servable(), p, engine.heuristics,
                       avoid={"heights"}, limit=10)
    assert all("heights" not in r.place.spectrum.trigger_warnings for r in recs)


def test_distance_filter(engine):
    p = build_profile([], engine.heuristics)
    recs = rank_places(engine.places.list_servable(), p, engine.heuristics,
                       near=(-1.2864, 36.8172), max_km=5, limit=20)
    assert recs and all(r.distance_km <= 5 for r in recs)
