"""shared.auth must accept tokens minted by the auth service and reject everything else."""

import sys
import time
import uuid
from pathlib import Path

import pytest

from shared.auth import AuthError, sign_test_token, verify_access_token

SECRET = "test-secret"


def test_accepts_own_format():
    uid = uuid.uuid4()
    assert verify_access_token(sign_test_token(uid, SECRET), SECRET).user_id == uid


@pytest.mark.parametrize("mutate,msg", [
    (lambda t: t[:-2] + ("AA" if t[-2:] != "AA" else "BB"), "bad signature"),
    (lambda t: "not.a.jwt.at.all", "malformed"),
    (lambda t: "x", "malformed"),
])
def test_rejects_tampered(mutate, msg):
    with pytest.raises(AuthError, match=msg):
        verify_access_token(mutate(sign_test_token(uuid.uuid4(), SECRET)), SECRET)


def test_rejects_wrong_secret_expired_and_refresh_tokens():
    with pytest.raises(AuthError, match="bad signature"):
        verify_access_token(sign_test_token(uuid.uuid4(), "other"), SECRET)
    with pytest.raises(AuthError, match="expired"):
        verify_access_token(sign_test_token(uuid.uuid4(), SECRET, ttl=-120), SECRET)
    with pytest.raises(AuthError, match="not an access token"):
        verify_access_token(sign_test_token(uuid.uuid4(), SECRET, token_type="refresh"), SECRET)


def test_rejects_alg_none():
    import base64
    import json
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()  # noqa: E731
    token = f"{enc({'alg': 'none'})}.{enc({'user_id': str(uuid.uuid4()), 'token_type': 'access', 'exp': time.time() + 60})}."
    with pytest.raises(AuthError):
        verify_access_token(token, SECRET)


@pytest.mark.parametrize("header", [[1], "HS256", 42, None])
def test_non_object_json_is_rejected_not_a_crash(header):
    import base64
    import json
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()  # noqa: E731
    with pytest.raises(AuthError, match="malformed"):
        verify_access_token(f"{enc(header)}.{enc({})}.{enc('sig')}", SECRET)


def test_compatible_with_auth_service_tokens(monkeypatch):
    """Tokens from the real auth service (python-jose) verify with the shared stdlib verifier."""
    pytest.importorskip("jose")
    pytest.importorskip("passlib")
    monkeypatch.setenv("JWT_SECRET_KEY", SECRET)
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "auth_service"))
    from auth_handler import AuthHandler

    uid = str(uuid.uuid4())
    token = AuthHandler().create_access_token(uid, "a@b.co", str(uuid.uuid4()))
    assert str(verify_access_token(token, SECRET).user_id) == uid
