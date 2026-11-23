import pytest
from fastapi.testclient import TestClient

from services.wellness_engine.app.config import Settings
from services.wellness_engine.app.main import app, build_engine


@pytest.fixture(scope="session")
def engine():
    return build_engine(Settings(ears_provider="lexicon", places_source="file"))


@pytest.fixture()
def client(engine):
    app.state.engine = engine
    with TestClient(app) as c:
        yield c
