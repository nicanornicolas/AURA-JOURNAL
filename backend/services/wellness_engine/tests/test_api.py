def test_health(client):
    assert client.get("/health").json()["service"] == "wellness-engine"


def test_recommend_from_text(client):
    r = client.post("/v1/recommend", json={"text": "I'm overwhelmed and exhausted", "limit": 3})
    body = r.json()
    assert r.status_code == 200
    assert body["safety"]["level"] == "none"
    assert len(body["recommendations"]) == 3
    assert body["recommendations"][0]["reasons"]


def test_recommend_from_needs(client):
    r = client.post("/v1/recommend", json={"needs": [{"state": "lonely", "score": 0.9}]})
    assert r.status_code == 200
    assert r.json()["ears"] is None


def test_recommend_requires_input(client):
    assert client.post("/v1/recommend", json={}).status_code == 422


def test_crisis_returns_resources_not_places(client):
    body = client.post("/v1/recommend", json={"text": "sitaki kuishi tena"}).json()
    assert body["safety"]["level"] == "crisis"
    assert body["recommendations"] == []
    assert body["safety"]["resources"]


def test_aura_compatible_analyze(client):
    body = client.post("/analyze", json={"text": "Blessed morning, grateful and happy"}).json()
    assert body["sentiment"]["label"] == "POSITIVE"
    assert "content" in body["topics"]
    assert body["language"] == "en"
