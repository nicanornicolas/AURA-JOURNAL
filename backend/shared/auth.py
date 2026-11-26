"""Verify access tokens issued by the auth service, without calling it.

The auth service signs JWTs with HS256 and ``JWT_SECRET_KEY``. Other services
share that secret and verify tokens locally with the standard library, so a
journal request never waits on another network hop.

Note: access tokens stay valid until they expire (30 minutes by default) even
after logout. Logout revokes the refresh token, so the session ends at the next
refresh. That is the usual trade-off for stateless access tokens.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_DEFAULT = "your-secret-key-change-in-production"


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret_key: str = INSECURE_DEFAULT
    # false = local development only: requests fall back to the user_id in the body.
    auth_required: bool = True
    clock_skew_seconds: int = 30


class AuthError(Exception):
    """Token missing, malformed, badly signed, expired, or the wrong type."""


class CurrentUser(BaseModel):
    user_id: uuid.UUID
    email: str | None = None
    session_id: str | None = None


def _b64decode(part: str) -> bytes:
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def verify_access_token(token: str, secret: str, skew: int = 30, now: float | None = None) -> CurrentUser:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        header = json.loads(_b64decode(header_b64))
        payload = json.loads(_b64decode(payload_b64))
        signature = _b64decode(sig_b64)
    except (ValueError, json.JSONDecodeError) as e:
        raise AuthError("malformed token") from e
    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise AuthError("malformed token")

    if header.get("alg") != "HS256":
        raise AuthError("unsupported algorithm")  # blocks alg=none and key-confusion tricks
    expected = hmac.new(secret.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise AuthError("bad signature")
    if payload.get("token_type") != "access":
        raise AuthError("not an access token")
    exp = payload.get("exp")
    if not isinstance(exp, int | float) or (now or time.time()) > exp + skew:
        raise AuthError("token expired")
    try:
        return CurrentUser(user_id=uuid.UUID(str(payload["user_id"])), email=payload.get("email"),
                           session_id=payload.get("session_id"))
    except (KeyError, ValueError) as e:
        raise AuthError("token has no valid user_id") from e


def sign_test_token(user_id: uuid.UUID | str, secret: str, ttl: int = 600, token_type: str = "access",
                    email: str = "test@example.com") -> str:
    """Create a token in the auth service's format. For tests and local tooling only."""
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64encode(json.dumps({
        "user_id": str(user_id), "email": email, "session_id": str(uuid.uuid4()),
        "exp": int(time.time()) + ttl, "iat": int(time.time()), "token_type": token_type,
    }).encode())
    sig = hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    return f"{header}.{payload}.{_b64encode(sig)}"
