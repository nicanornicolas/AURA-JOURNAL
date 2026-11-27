# Testing guide: prove each step works

Every step of the plan ends with three kinds of test. Run them in this order; each one
needs the previous one to pass.

| Level | What it proves | Needs | Time |
|---|---|---|---|
| 1. Unit tests | The code does what it should, in isolation | Python only | ~15 s |
| 2. Stack smoke test | The real containers work together over HTTP | Docker or Podman | ~1 min |
| 3. Phone check | A person can use it on the Android phone | The phone on the homelab Wi-Fi | ~5 min |

Deploying the stack (homelab now, Truehost later) is in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## One-time setup (laptop or homelab)

```bash
git clone https://github.com/nicanornicolas/AURA-JOURNAL.git
cd AURA-JOURNAL/backend

# uv: https://docs.astral.sh/uv/  (curl -LsSf https://astral.sh/uv/install.sh | sh)
uv venv --python 3.12
uv pip install fastapi "uvicorn[standard]" pydantic pydantic-settings sqlalchemy \
  psycopg2-binary pymongo httpx pyyaml loguru pytest pytest-mock pyairtable ruff \
  "passlib[bcrypt]" "python-jose[cryptography]" "pydantic[email]" pytest-asyncio
source .venv/bin/activate
```

This is the same list CI installs (`.github/workflows/backend-tests.yml`), so a pass here
means a pass on GitHub.

---

## Level 1: unit tests

From `backend/` with the venv active:

```bash
# Engine, pipeline, entries API, shared code
DATABASE_URL=sqlite:// PYTHONPATH=. pytest pipelines services/wellness_engine/tests \
  services/entry_ingestor/tests tests -o addopts="" -q

# Auth service (runs from its own folder, the way its container does)
(cd services/auth_service && DATABASE_URL=sqlite:// ../../.venv/bin/pytest tests -o addopts="" -q -p no:cacheprovider)

# Lint (the same files CI checks)
ruff check --select E,W,F,I,B,UP --ignore E501,B008 services/wellness_engine pipelines \
  shared/mental_spectrum.py shared/auth.py scripts/smoke_test.py tests/test_optional_deps.py
```

**Expected:** `70 passed` and `19 passed` (as of step 3b), and no ruff output.
The counts only go up as steps add tests. If one goes down, a test was lost.

---

## Level 2: stack smoke test

Start the stack (full steps in [DEPLOYMENT.md](docs/DEPLOYMENT.md#3-homelab-first-start)):

```bash
cd backend
cp .env.homelab.example .env.homelab        # set POSTGRES_PASSWORD and JWT_SECRET_KEY
docker compose -f docker-compose.homelab.yml --env-file .env.homelab up -d --build
```

Then, from any machine that can reach the server:

```bash
python3 backend/scripts/smoke_test.py                        # on the server itself
python3 backend/scripts/smoke_test.py --host 192.168.0.10    # from the laptop, homelab IP
python3 backend/scripts/smoke_test.py --skip-auth            # Wellness Engine only
```

The script uses only the Python standard library, so it needs no venv. Each line prints
`PASS` or `FAIL`, and the exit code is the number of failures. It registers two throwaway
`smoke-…@example.com` users and deletes the journal entries it creates.

**Expected output (lexicon mode, seed places):**

```
1. Health
  PASS  wellness engine /health
  PASS  auth service /health
  PASS  entries API /health

2. Wellness Engine (Ears and Brain)
  PASS  English need detection (overwhelmed, drained)
        provider=lexicon language=en valence=0.0
  PASS  Swahili detected and understood
  PASS  Recommendations returned with reasons
        0.91  Nairobi National Park: Something new (novelty 4.4/5); Awe-inspiring (awe 4.6/5)
        ...
  PASS  Trigger filter removes 'heights' places
  PASS  Crisis text returns helplines and no places
  PASS  Aura-compatible /analyze

3. Auth service
  PASS  register user 1 ... PASS  wrong password rejected

4. Entries API
        AUTH_REQUIRED looks true (unauthenticated GET -> 401)
  PASS  create entry with token (analysed)
  ... (isolation, edit, trends, delete, bad token)

All checks passed.
```

With `EARS_EXTRAS=hf` the second line says `provider=hf`, and the scores and valence differ.
That line is how you confirm the models are really in use.

If it fails, see [Troubleshooting](#troubleshooting).

---

## Level 3: phone check (Android)

1. Phone on the **NIKOS-HOMELAB** Wi-Fi (the server sits behind the Tenda's NAT).
2. In `aura-journal-app/.env`: `EXPO_PUBLIC_API_URL=http://192.168.0.10:8001`
3. `cd aura-journal-app && npm install && npx expo start`, then scan the QR code with Expo Go.
4. Write an entry such as "Nimechoka sana leo". You should see an analysis card with a
   sentiment and topics such as `drained`.
5. On the server, confirm it was stored:
   ```bash
   docker exec aura_homelab_db psql -U aura -d aura_journal -c \
     "select left(content,40), timestamp from journal_entries order by timestamp desc limit 3"
   ```

Until the app has login screens, the server needs `AUTH_REQUIRED=false` for this check,
because the app still sends a fixed test `user_id`. Switch it to `true` once logins ship.

---

## What each step delivered, and how to check it

Use this as the record of what is done. Each new step adds a section.

### Step 2: Wellness Engine (Ears and Brain) and places pipeline

| Check | Command | Pass looks like |
|---|---|---|
| Unit tests | Level 1 | engine and pipeline tests pass |
| English need detection | smoke test section 2 | `overwhelmed`, `drained` found |
| Swahili | smoke test section 2 | `language=sw` and a need found |
| Recommendations with reasons | smoke test section 2 | 1 to 3 places, each with reasons |
| Trigger filter | smoke test section 2 | no `heights` place returned |
| Crisis safety | smoke test section 2 | no places, helplines returned |
| Pipeline offline | `cd backend && python -m pipelines.serenescapes_etl.run annotate` after an `extract` | `data/serenescapes/golden.jsonl` written |
| Tune a rule | edit `heuristics.yaml`, `docker compose ... restart wellness_engine`, rerun smoke | ranking order changes |

Try the engine by hand:

```bash
curl -s -X POST http://192.168.0.10:8300/v1/recommend -H 'Content-Type: application/json' \
  -d '{"text":"I feel overwhelmed and need quiet","avoid_triggers":["crowds"],"limit":3}' | python3 -m json.tool
```

### Step 3a: Aura backend (auth, entries API, Postgres insights)

| Check | Command | Pass looks like |
|---|---|---|
| Unit tests | Level 1 | auth (19) and entries tests pass |
| Register and log in | smoke test section 3 | `register`, `login`, `profile` PASS |
| Entries are private | smoke test section 4 | other user sees none, gets 404 |
| Edit re-analyses | smoke test section 4 | sentiment changes to POSITIVE |
| Mood trends | smoke test section 4 | daily rows returned |
| Login enforced | `AUTH_REQUIRED=true`, restart ingestor, rerun smoke | `unauthenticated GET -> 401` |

### Step 3b: testing and deployment guides, Postgres places without Airtable

| Check | Command | Pass looks like |
|---|---|---|
| Engine starts without MongoDB libs | `pytest tests/test_optional_deps.py` | pass (this crash was found by running the real containers) |
| Load places with no Airtable | `DATABASE_URL=postgresql+psycopg2://aura:PASS@localhost:5433/aura_journal python -m pipelines.serenescapes_etl.run load-postgres --seed` | `Upserted 10 places into Postgres` |
| Engine serves from Postgres | `PLACES_SOURCE=postgres`, restart engine, rerun smoke | all PASS |
| Live edits | `update places set status='hidden' where place_id='seed-nnp'`, call `/v1/recommend` again | Nairobi National Park gone, no restart |

Verified on 27 Nov 2026 against the real Docker stack: all 24 smoke checks passed, with
lexicon mode, both `PLACES_SOURCE=file` and `postgres`, and both `AUTH_REQUIRED` values.
Not yet verified on real hardware: Hugging Face models (blocked in the build environment),
the Ollama annotator against a live Ollama, and Podman instead of Docker.

### Adding the next step

Every new step should land with:

1. Unit tests for the new code, added to the Level 1 commands if they live somewhere new.
2. New checks in `backend/scripts/smoke_test.py` for each new endpoint.
3. A section above: a table of checks, the commands, and what a pass looks like.
4. A note of anything that could not be verified, and why.

---

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `FAIL ... /health (0 {'error': 'Connection refused'})` | Service not up. `docker compose -f docker-compose.homelab.yml ps` and `docker logs aura_homelab_engine` |
| Everything fails from the laptop, passes on the server | Firewall. See DEPLOYMENT.md, step 2 |
| `create entry with token` fails with 500 | Engine unreachable from the ingestor, or DB down. `docker logs aura_homelab_ingestor` |
| `garbage token rejected` fails | `AUTH_REQUIRED=false`. Expected in phone-test mode only |
| `login` works but entries say 401 | `JWT_SECRET_KEY` differs between auth and ingestor. Both read it from `.env.homelab`; recreate both containers |
| First request with `hf` takes minutes | Models are downloading into the `hf_models` volume. Only happens once. Watch `docker logs -f aura_homelab_engine` |
| Smoke test hangs behind a corporate proxy | Run `no_proxy='*' python3 backend/scripts/smoke_test.py` |
