#!/usr/bin/env python3
"""End-to-end smoke test for a running Aura Journal / SereneScapes stack.

Standard library only, so it runs on any machine with Python 3.9+: your laptop,
the homelab, or a VPS.

    python3 backend/scripts/smoke_test.py                       # localhost
    python3 backend/scripts/smoke_test.py --host 192.168.1.50   # homelab from your laptop
    python3 backend/scripts/smoke_test.py --skip-auth           # Wellness Engine only

Every check prints PASS or FAIL; the exit code is the number of failures.
It creates two throwaway users (smoke-<random>@example.com) and deletes the
journal entries it makes.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import uuid

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        FAILURES.append(name)
    return ok


def call(method: str, url: str, body: dict | None = None, headers: dict | None = None,
         timeout: float = 30) -> tuple[int, dict | list | None]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return e.code, {"raw": raw.decode(errors="replace")[:200]}
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return 0, {"error": str(e)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--scheme", default="http")
    ap.add_argument("--engine-port", type=int, default=8300)
    ap.add_argument("--auth-port", type=int, default=8003)
    ap.add_argument("--entries-port", type=int, default=8001)
    ap.add_argument("--skip-auth", action="store_true", help="only test the Wellness Engine")
    a = ap.parse_args()

    engine = f"{a.scheme}://{a.host}:{a.engine_port}"
    auth = f"{a.scheme}://{a.host}:{a.auth_port}"
    entries = f"{a.scheme}://{a.host}:{a.entries_port}"

    print("\n1. Health")
    for name, base in [("wellness engine", engine), ("auth service", auth), ("entries API", entries)]:
        if a.skip_auth and base != engine:
            continue
        code, body = call("GET", f"{base}/health")
        check(f"{name} /health", code == 200, f"{code} {body}")

    print("\n2. Wellness Engine (Ears and Brain)")
    code, b = call("POST", f"{engine}/v1/ears/analyze", {"text": "I'm overwhelmed and running on empty"})
    states = [n["state"] for n in (b or {}).get("needs", [])] if code == 200 else []
    check("English need detection (overwhelmed, drained)", {"overwhelmed", "drained"} <= set(states), f"{code} {states}")
    if code == 200:
        print(f"        provider={b['provider']} language={b['language']} valence={b['valence']}")

    code, b = call("POST", f"{engine}/v1/ears/analyze", {"text": "Nimechoka sana leo, nina msongo wa mawazo"})
    check("Swahili detected and understood", code == 200 and b["language"] == "sw"
          and any(n["state"] in {"drained", "overwhelmed"} for n in b["needs"]), f"{code} {b}")

    code, b = call("POST", f"{engine}/v1/recommend", {"text": "I feel stuck in a rut", "limit": 3})
    recs = (b or {}).get("recommendations", []) if code == 200 else []
    check("Recommendations returned with reasons", len(recs) >= 1 and all(r["reasons"] for r in recs), f"{code} {b}")
    for r in recs:
        print(f"        {r['fit']:.2f}  {r['place']['name']}: {'; '.join(r['reasons'])}")

    code, b = call("POST", f"{engine}/v1/recommend", {"text": "stuck", "avoid_triggers": ["heights"], "limit": 10})
    check("Trigger filter removes 'heights' places", code == 200 and all(
        "heights" not in r["place"]["spectrum"]["trigger_warnings"] for r in b["recommendations"]), f"{code}")

    code, b = call("POST", f"{engine}/v1/recommend", {"text": "I want to end my life"})
    check("Crisis text returns helplines and no places", code == 200 and b["safety"]["level"] == "crisis"
          and b["recommendations"] == [] and b["safety"]["resources"], f"{code} {b}")

    code, b = call("POST", f"{engine}/analyze", {"text": "Blessed morning, grateful"})
    check("Aura-compatible /analyze", code == 200 and b["sentiment"]["label"] == "POSITIVE", f"{code} {b}")

    if a.skip_auth:
        return finish()

    print("\n3. Auth service")
    users = []
    for i in range(2):
        email, pw = f"smoke-{uuid.uuid4().hex[:10]}@example.com", "SmokeTest123!"
        code, b = call("POST", f"{auth}/auth/register", {"email": email, "password": pw, "first_name": "Smoke"})
        check(f"register user {i + 1}", code == 201, f"{code} {b}")
        code, b = call("POST", f"{auth}/auth/login", {"email": email, "password": pw})
        ok = check(f"login user {i + 1}", code == 200 and "access_token" in (b or {}), f"{code} {b}")
        if ok:
            users.append(b)
    if len(users) < 2:
        return finish()
    h1 = {"Authorization": f"Bearer {users[0]['access_token']}"}
    h2 = {"Authorization": f"Bearer {users[1]['access_token']}"}
    code, b = call("GET", f"{auth}/auth/profile", headers=h1)
    check("profile with access token", code == 200 and b["email"].startswith("smoke-"), f"{code} {b}")
    code, _ = call("POST", f"{auth}/auth/login", {"email": "nobody@example.com", "password": "WrongPass123!"})
    check("wrong password rejected", code == 401, f"{code}")

    print("\n4. Entries API")
    code, _ = call("GET", f"{entries}/entries")
    auth_required = code == 401
    print(f"        AUTH_REQUIRED looks {'true' if auth_required else 'false'} (unauthenticated GET -> {code})")

    code, b = call("POST", f"{entries}/entries", {"content": "So tired today, nimechoka"}, headers=h1, timeout=60)
    ok = check("create entry with token (analysed)", code == 201 and b.get("analysis") is not None, f"{code} {b}")
    if not ok:
        return finish()
    eid = b["entry_id"]
    print(f"        needs={[n['state'] for n in b['analysis'].get('needs', [])]} "
          f"sentiment={b['analysis']['sentiment']['label']}")

    code, b = call("GET", f"{entries}/entries?limit=5", headers=h1)
    check("list my entries", code == 200 and b["total"] >= 1 and b["items"][0]["entry_id"] == eid, f"{code}")
    code, b = call("GET", f"{entries}/entries", headers=h2)
    check("other user sees none of my entries", code == 200 and all(i["entry_id"] != eid for i in b["items"]), f"{code}")
    code, _ = call("GET", f"{entries}/entries/{eid}", headers=h2)
    check("other user gets 404 on my entry", code == 404, f"{code}")
    code, b = call("PATCH", f"{entries}/entries/{eid}", {"content": "Feeling grateful and calm now"}, headers=h1, timeout=60)
    check("edit re-analyses", code == 200 and b["analysis"]["sentiment"]["label"] == "POSITIVE", f"{code} {b}")
    code, b = call("GET", f"{entries}/insights/trends?days=7", headers=h1)
    check("mood trends", code == 200 and b["entries"] >= 1 and b["daily"], f"{code} {b}")
    code, _ = call("DELETE", f"{entries}/entries/{eid}", headers=h1)
    check("delete entry", code == 204, f"{code}")
    code, _ = call("GET", f"{entries}/entries/{eid}", headers=h1)
    check("deleted entry is gone", code == 404, f"{code}")
    code, _ = call("GET", f"{entries}/entries", headers={"Authorization": "Bearer not-a-token"})
    check("garbage token rejected", code == 401, f"{code}")
    return finish()


def finish() -> int:
    print("\n" + ("All checks passed." if not FAILURES else f"{len(FAILURES)} check(s) failed: {', '.join(FAILURES)}"))
    return len(FAILURES)


if __name__ == "__main__":
    sys.exit(main())
