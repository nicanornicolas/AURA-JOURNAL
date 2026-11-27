"""End-to-end tests of the entries API on in-memory SQLite with real services.

Only the Wellness Engine call is faked. Covers ownership: nobody can read, edit or
delete someone else's entries.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from shared import AnalysisPayload, EmotionScore, NeedState, SentimentResult
from shared.auth import AuthSettings, sign_test_token
from services.entry_ingestor.app.dependencies import get_auth_settings, get_db, get_entry_service
from services.entry_ingestor.app.main import app
from services.entry_ingestor.app.models import Base
from services.entry_ingestor.app.services import EntryService, PostgresInsightStorage

SECRET = "unit-test-secret"


class FakeEngine:
    """Stands in for the Wellness Engine's /analyze."""

    def __init__(self):
        self.down = False

    def analyze_text(self, text):
        if self.down:
            return None
        sad = "tired" in text or "nimechoka" in text
        return AnalysisPayload(
            sentiment=SentimentResult(label="NEGATIVE" if sad else "POSITIVE", score=-0.6 if sad else 0.7),
            topics=["drained"] if sad else ["content"],
            emotions=[EmotionScore(label="sadness" if sad else "joy", score=0.8)],
            needs=[NeedState(state="drained" if sad else "content", score=0.9)],
        )


@pytest.fixture()
def env():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False)
    nlp = FakeEngine()
    service = EntryService(nlp, PostgresInsightStorage(Session))

    def db():
        s = Session()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = db
    app.dependency_overrides[get_entry_service] = lambda: service
    app.dependency_overrides[get_auth_settings] = lambda: AuthSettings(jwt_secret_key=SECRET, auth_required=True)
    yield TestClient(app), nlp
    app.dependency_overrides.clear()


def auth(uid):
    return {"Authorization": f"Bearer {sign_test_token(uid, SECRET)}"}


def test_requires_token(env):
    client, _ = env
    assert client.get("/entries").status_code == 401
    assert client.post("/entries", json={"content": "hi"}).status_code == 401
    bad = {"Authorization": f"Bearer {sign_test_token(uuid.uuid4(), 'wrong')}"}
    assert client.get("/entries", headers=bad).status_code == 401


def test_create_takes_owner_from_token(env):
    client, _ = env
    me = uuid.uuid4()
    r = client.post("/entries", json={"content": "Blessed morning"}, headers=auth(me))
    assert r.status_code == 201
    body = r.json()
    assert body["user_id"] == str(me)
    assert body["analysis"]["needs"][0]["state"] == "content"


def test_cannot_post_as_someone_else(env):
    client, _ = env
    r = client.post("/entries", json={"content": "x", "user_id": str(uuid.uuid4())}, headers=auth(uuid.uuid4()))
    assert r.status_code == 403


def test_full_lifecycle_and_isolation(env):
    client, _ = env
    me, other = uuid.uuid4(), uuid.uuid4()
    ids = [client.post("/entries", json={"content": t}, headers=auth(me)).json()["entry_id"]
           for t in ["Blessed morning", "So tired today", "Nimechoka sana"]]
    client.post("/entries", json={"content": "not yours"}, headers=auth(other))

    page = client.get("/entries?limit=2", headers=auth(me)).json()
    assert page["total"] == 3 and len(page["items"]) == 2
    assert all(i["analysis"] for i in page["items"])
    assert client.get("/entries?offset=2", headers=auth(me)).json()["items"][0]["entry_id"] in ids

    # The other user sees only their own entry and gets 404 on mine
    assert client.get("/entries", headers=auth(other)).json()["total"] == 1
    for call in (client.get, client.delete):
        assert call(f"/entries/{ids[0]}", headers=auth(other)).status_code == 404
    assert client.patch(f"/entries/{ids[0]}", json={"content": "hacked"}, headers=auth(other)).status_code == 404

    # Edit re-analyses
    r = client.patch(f"/entries/{ids[0]}", json={"content": "Actually tired now"}, headers=auth(me))
    assert r.status_code == 200 and r.json()["analysis"]["sentiment"]["label"] == "NEGATIVE"
    assert client.get(f"/entries/{ids[0]}", headers=auth(me)).json()["content"] == "Actually tired now"

    # Delete removes entry and analysis
    assert client.delete(f"/entries/{ids[1]}", headers=auth(me)).status_code == 204
    assert client.get(f"/entries/{ids[1]}", headers=auth(me)).status_code == 404
    assert client.get("/entries", headers=auth(me)).json()["total"] == 2


def test_edit_drops_stale_analysis_when_engine_down(env):
    client, nlp = env
    me = uuid.uuid4()
    eid = client.post("/entries", json={"content": "Blessed"}, headers=auth(me)).json()["entry_id"]
    nlp.down = True
    r = client.patch(f"/entries/{eid}", json={"content": "So tired"}, headers=auth(me))
    assert r.status_code == 200 and r.json()["analysis"] is None
    assert client.get(f"/entries/{eid}", headers=auth(me)).json()["analysis"] is None


def test_mood_trends(env):
    client, _ = env
    me = uuid.uuid4()
    for t in ["Blessed morning", "So tired today", "tired again"]:
        client.post("/entries", json={"content": t}, headers=auth(me))
    t = client.get("/insights/trends?days=7", headers=auth(me)).json()
    assert t["entries"] == 3
    assert len(t["daily"]) == 1 and t["daily"][0]["entries"] == 3
    assert t["daily"][0]["mood"] == pytest.approx((0.7 - 0.6 - 0.6) / 3, abs=1e-3)
    assert t["top_needs"][0] == {"state": "drained", "count": 2}


def test_dev_mode_without_auth(env):
    client, _ = env
    app.dependency_overrides[get_auth_settings] = lambda: AuthSettings(jwt_secret_key=SECRET, auth_required=False)
    uid = uuid.uuid4()
    r = client.post("/entries", json={"user_id": str(uid), "content": "Blessed"})
    assert r.status_code == 201 and r.json()["user_id"] == str(uid)
    assert client.get("/entries", headers={"X-User-Id": str(uid)}).json()["total"] == 1
    assert client.post("/entries", json={"content": "no owner"}).status_code == 422
