from services.wellness_engine.app.ears.language import detect_language
from services.wellness_engine.app.ears.lexicon import detect_needs
from services.wellness_engine.app.ears.safety import screen


def states(text):
    return [n.state for n in detect_needs(text)]


def test_detects_swahili_and_english():
    assert detect_language("Leo nimechoka sana na kazi nyingi") == "sw"
    assert detect_language("I am so tired after work today") == "en"
    assert detect_language("") == "en"


def test_metaphors_map_to_need_states():
    assert states("Honestly I'm running on empty this week")[0] == "drained"
    assert "overwhelmed" in states("Too much going on, my mind is cluttered")
    assert "stuck" in states("I feel stuck in a rut")


def test_swahili_need_states():
    assert "drained" in states("Nimechoka sana leo")
    assert "overwhelmed" in states("Nina msongo wa mawazo, nimelemewa")
    assert "lonely" in states("Najihisi mpweke, niko peke yangu")
    assert "anxious" in states("Nina wasiwasi kuhusu kesho")


def test_safety_crisis_english_and_swahili():
    res = ["help line"]
    assert screen("I want to end my life", res).level == "crisis"
    assert screen("Nataka kufa", res).flagged is True
    assert screen("I feel hopeless", res).level == "concern"
    assert screen("Lovely walk today", res).level == "none"


def test_ears_service_shape(engine):
    r = engine.ears.analyze("Nimechoka na nina huzuni")
    assert r.language == "sw"
    assert r.provider == "lexicon"
    assert {"drained", "low"} <= {n.state for n in r.needs}
    assert r.valence < 0
