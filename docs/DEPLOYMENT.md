# Deployment guide: homelab now, Truehost later

This guide gets the whole stack running on the homelab (Fedora, 6 GB RAM, 2 cores, no GPU,
already running Gramps Web), then explains what changes on a Truehost VPS.
After each part, prove it works with [GUIDE.md](../GUIDE.md).

**Recommended order:** lexicon mode first (sections 1 to 3), places in Postgres (section 6),
then Hugging Face models (section 4), then the Ollama annotator (section 7).

---

## 0. What runs where

```
 Android phone ──HTTP──▶ entries API :8001 ──▶ Wellness Engine :8300 (Ears + Brain)
        │                      │                      │
        └──HTTP──▶ auth :8003  └──────▶ Postgres ◀────┘  (entries, insights, users, places)
                                        127.0.0.1:5433 only

 Laptop (or Kaggle): places pipeline ── OSM ──▶ annotate (heuristic | Ollama | Gemini)
                                     ──▶ Postgres places (direct) or Airtable (review) ──▶ Postgres
```

| Container | Host port | RAM limit | Job |
|---|---|---|---|
| `aura_homelab_db` (Postgres 16) | 127.0.0.1:5433 | 384 MB | All data. Not reachable from the LAN |
| `aura_homelab_engine` | 8300 | 2 GB (~150 MB in lexicon mode) | Ears (emotion, needs, crisis) and Brain (recommendations) |
| `aura_homelab_auth` | 8003 | 192 MB | Register, login, refresh, logout. Signs JWTs |
| `aura_homelab_ingestor` | 8001 | 256 MB | Journal entries API, mood trends. Sends text to the engine |

All of it is defined in `backend/docker-compose.homelab.yml` and configured by one file,
`backend/.env.homelab`.

---

## 1. Prepare the server

### Homelab (Fedora)

Podman ships with Fedora. You can use it or Docker. The stack was validated with Docker
Compose; Podman uses the same file.

**Which one?** Check first: `rpm -q podman-docker docker-compose`. If both are installed
(as on the homelab), use **Option A with the Podman socket**. Your `docker` command is
already Podman, and Docker CE would conflict with both packages. Don't force Docker CE in
with `--allowerasing`: it removes `podman-docker`, and anything else already running on
Podman (Gramps Web) ends up on a different engine from this stack.

**Option A: Podman (already installed)**

```bash
sudo dnf install -y podman-compose git
loginctl enable-linger $USER                     # containers keep running after you log out
systemctl --user enable podman-restart.service   # restart containers after a reboot
```

If `podman-compose` rejects `depends_on: condition:`, use Docker Compose against the
Podman socket instead, which supports the whole file:

```bash
sudo dnf install -y docker-compose               # the compose CLI only, no Docker daemon
systemctl --user enable --now podman.socket
echo 'export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock' >> ~/.bashrc && source ~/.bashrc
```

Then every `docker compose` command below works unchanged. Check it with:

```bash
docker compose version        # podman-docker passes this to Podman, which runs docker-compose
docker info | grep -i rootless   # "rootless: true" means it is talking to your user's Podman
```

Rootless Podman containers belong to your user, so run every command here **without
`sudo`** (with `sudo` you'd see an empty, separate set of containers).

**Option B: Docker** (only on a server without `podman-docker`, such as a fresh VPS)

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager addrepo --from-repofile=https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER && newgrp docker
```

Pick one. Running both side by side works, but doubles the confusion when debugging.

### Get the code

```bash
# On the homelab, apps live in /srv/apps (created by 04-apps-prep.sh) and the repo is
# cloned over SSH with the read-only deploy key that script made.
cd /srv/apps
git clone git@github.com:nicanornicolas/AURA-JOURNAL.git
cd /srv/apps/AURA-JOURNAL/backend
```

Everything in this guide runs from `/srv/apps/AURA-JOURNAL` (the compose file and
`.env.homelab` are in its `backend/` folder). Check you're in the right place with
`git -C /srv/apps/AURA-JOURNAL remote -v`.

---

## 2. Firewall

The phone and laptop need ports 8001 (entries) and 8003 (auth). Port 8300 (engine) is
useful from the laptop for testing, and the SereneScapes app will need it later.
Postgres stays local.

```bash
sudo firewall-cmd --permanent --add-port=8001/tcp --add-port=8003/tcp --add-port=8300/tcp
sudo firewall-cmd --reload
hostname -I        # the homelab IP the phone uses, for example 192.168.0.10
```

---

## 3. Homelab first start (lexicon mode)

Lexicon mode is rules only: no downloads, about 150 MB RAM, instant replies. English and
Swahili need detection and the crisis screen work fully. Emotion scores are coarser than
with the models.

```bash
cd /srv/apps/AURA-JOURNAL/backend
cp .env.homelab.example .env.homelab
nano .env.homelab
```

Set:

```ini
POSTGRES_PASSWORD=<a long random password>
EARS_EXTRAS=none
EARS_PROVIDER=lexicon
PLACES_SOURCE=file
JWT_SECRET_KEY=<output of: openssl rand -hex 32>
AUTH_REQUIRED=false          # until the app has login screens; see section 5
```

Start it:

```bash
docker compose -f docker-compose.homelab.yml --env-file .env.homelab up -d --build
docker compose -f docker-compose.homelab.yml ps          # all four "Up", then "healthy" within ~1 min
python3 scripts/smoke_test.py                            # expect: All checks passed.
```

To save typing, add an alias:

```bash
echo "alias aura='docker compose -f /srv/apps/AURA-JOURNAL/backend/docker-compose.homelab.yml --env-file /srv/apps/AURA-JOURNAL/backend/.env.homelab'" >> ~/.bashrc
source ~/.bashrc
aura ps; aura logs -f wellness_engine; aura restart entry_ingestor
```

The rest of this guide uses `aura` for that compose command.

---

## 4. Hugging Face models (one-time download)

The models give better emotion detection, and Swahili entries are translated to English
before classification:

| Model | Job | Download | RAM |
|---|---|---|---|
| `SamLowe/roberta-base-go_emotions` | 28 emotions | ~500 MB | ~0.5 GB |
| `Helsinki-NLP/opus-mt-sw-en` | Swahili to English | ~300 MB | ~0.3 GB |

They are downloaded once into the `hf_models` volume, which survives rebuilds and restarts.

```ini
# .env.homelab
EARS_EXTRAS=hf
EARS_PROVIDER=auto        # uses the models when installed, else lexicon
HF_HUB_OFFLINE=0
```

```bash
aura up -d --build wellness_engine     # rebuild: adds CPU-only torch + transformers (~1 GB image)
aura logs -f wellness_engine           # "Loading emotion model ...", "Loading translator ..."
```

The download starts in the background when the engine starts; `/health` answers right away.
Wait until the first analysis call answers (it waits for the models), then confirm:

```bash
curl -s -X POST localhost:8300/v1/ears/analyze -H 'Content-Type: application/json' \
  -d '{"text":"Nimechoka sana leo"}' | python3 -m json.tool | grep -E '"provider"|"language"'
# "provider": "hf", "language": "sw"
python3 scripts/smoke_test.py          # section 2 now prints provider=hf
```

Once that works, cut the server off from Hugging Face for good:

```ini
HF_HUB_OFFLINE=1
```

```bash
aura up -d wellness_engine
```

**Memory:** with the models, the engine uses up to 2 GB. Together with Postgres, auth,
the ingestor and Gramps Web, that fits in 6 GB but leaves little room. Don't run Ollama on
the homelab at the same time (see section 7). If the box starts swapping, go back to
`EARS_PROVIDER=lexicon`; nothing else changes.

**First call per entry is slow on 2 cores:** expect a few seconds per entry. The app's
timeout is 20 seconds.

---

## 5. Aura backend: auth, entries API, insights

Nothing extra to install: all three are part of the stack.

- **Auth service (`:8003`)**: `POST /auth/register`, `/auth/login`, `/auth/refresh`,
  `/auth/logout`, `GET /auth/profile`. Access tokens last 30 minutes; refresh tokens are
  revoked on logout.
- **Entries API (`:8001`)**: `POST/GET /entries`, `GET/PATCH/DELETE /entries/{id}`,
  `GET /insights/trends?days=30`. Every entry is analysed by the engine and the analysis
  is stored in Postgres (`journal_insights`). No MongoDB.
- **Interactive docs:** `http://<server>:8001/docs` and `http://<server>:8003/docs`.

### `JWT_SECRET_KEY`

The auth service signs tokens with it and the entries API checks them with it, so both
containers must get the same value. They do, because both read `.env.homelab`. If you ever
change it, recreate both (`aura up -d auth_service entry_ingestor`); everyone has to log in again.

### `AUTH_REQUIRED`

| Value | Behaviour | Use when |
|---|---|---|
| `false` | Requests without a token are accepted and use `user_id` from the body | Phone testing on the LAN, until the app has login screens |
| `true` | Every request needs `Authorization: Bearer <access token>` | Anything reachable from the internet, and as soon as login screens ship |

Change it in `.env.homelab`, then `aura up -d entry_ingestor`. The smoke test prints which
mode it detected.

---

## 6. Places in Postgres, without Airtable

By default the engine serves the 10 bundled seed places from a file. Switching to Postgres
lets you change places without rebuilding, and is where real pipeline output goes.

The pipeline runs on the laptop or the homelab host, not in a container. It reaches
Postgres on `127.0.0.1:5433`. From the laptop, open a tunnel first:

```bash
ssh -N -L 5433:127.0.0.1:5433 <you>@192.168.0.10     # leave running in its own terminal
```

Then, from `backend/` with the venv from GUIDE.md active:

```bash
export DATABASE_URL=postgresql+psycopg2://aura:<POSTGRES_PASSWORD>@localhost:5433/aura_journal

# Start with the seed places
python -m pipelines.serenescapes_etl.run load-postgres --seed
# Upserted 10 places into Postgres
```

Switch the engine over:

```ini
PLACES_SOURCE=postgres
```

```bash
aura up -d wellness_engine
python3 scripts/smoke_test.py --skip-auth      # recommendations now come from Postgres
```

The engine reads the table on every request, so edits take effect immediately:

```bash
docker exec -it aura_homelab_db psql -U aura -d aura_journal
  select place_id, name, status, awe, biophilia from places;
  update places set status = 'hidden' where place_id = 'seed-nnp';   -- stop recommending it
  update places set status = 'approved' where place_id = 'seed-nnp'; -- bring it back
```

Only rows with `status = 'approved'` are served. `load-postgres` writes `approved`
directly, so use it for places you have looked over yourself. When real users arrive, put
the Airtable review step back (`load`, then `sync`); the table and the engine stay the same.

---

## 7. Places pipeline with the Ollama annotator

The pipeline turns OpenStreetMap places into scored places:

1. **extract**: OSM Overpass for parks, forests, viewpoints, waterfalls, museums and so on
   inside a bounding box (Nairobi by default; the order is south, west, north, east).
2. **annotate**: scores 11 sub-factors (1 to 5) per place, which the rubric turns into the
   five Mental Spectrum fields (section 8). Annotators: `heuristic` (rules, free, instant),
   `ollama` (local open model), `gemini` (free AI Studio key, later).
3. **load-postgres** (or `load` + `sync` through Airtable).

Each stage writes a checkpoint in `backend/data/serenescapes/` (`raw.jsonl`,
`golden.jsonl`), so a failed stage reruns without repeating the earlier ones.

### Where to run Ollama

You already have `~/.ollama` on your machine. **Run the annotation there, not on the
homelab:** a 3B model needs about 2 to 3 GB RAM, which the homelab can't spare next to the
engine with models and Gramps Web. If the homelab is the only option, stop the engine or
put it in lexicon mode while annotating.

```bash
ollama pull qwen2.5:3b          # the pipeline's default model; any JSON-capable model works
ollama serve                    # if it isn't already running as a service
curl -s localhost:11434/api/tags | head -c 200     # check it answers
```

### Run it

From `backend/` on the laptop, venv active, SSH tunnel open (section 6):

```bash
export ANNOTATOR=ollama OLLAMA_URL=http://localhost:11434 OLLAMA_MODEL=qwen2.5:3b
export MAX_PLACES=40            # start small: CPU-only models take several seconds per place
export DATABASE_URL=postgresql+psycopg2://aura:<POSTGRES_PASSWORD>@localhost:5433/aura_journal

python -m pipelines.serenescapes_etl.run extract        # needs internet (Overpass)
python -m pipelines.serenescapes_etl.run annotate       # "Annotated 40 places: {"ollama": 38, ...}"
python -m pipelines.serenescapes_etl.run load-postgres  # "Upserted 40 places into Postgres"
```

Check the result before trusting it:

```bash
python - <<'EOF'
import json
for line in open("data/serenescapes/golden.jsonl"):
    g = json.loads(line); s = g["spectrum"]
    print(f'{g["poi"]["name"][:30]:30} {g["annotation"]["annotator"]:9} '
          f'load {s["cognitive_load"]:.1f} bio {s["biophilia"]:.1f} awe {s["awe"]:.1f} '
          f'triggers {s["trigger_warnings"]}')
EOF
```

If the model's reply is not valid JSON or breaks the rubric, that place falls back to the
heuristic score and is labelled `heuristic` in the summary, so a run always completes. Many
fallbacks mean the model is too small or busy: try `qwen2.5:7b` if your machine has the RAM.

To compare annotators on the same places, rerun only `annotate` with `--annotator heuristic`
and look at the differences; `extract` doesn't need to run again.

Other settings (environment variables): `CITY`, `BBOX` (JSON, for example
`'[-1.45,36.65,-1.15,37.0]'`), `FOURSQUARE_API_KEY` (optional crowd data),
`GEMINI_API_KEY` with `ANNOTATOR=gemini`. Details: `backend/pipelines/serenescapes_etl/README.md`.

---

## 8. Rubric and heuristics

Two files decide what gets recommended. Both are plain text, meant to be edited.

### The rubric: `backend/shared/mental_spectrum.py`

How 11 sub-factors (each scored 1 to 5) become the 5 fields every place carries:

| Field | Formula | Meaning |
|---|---|---|
| cognitive_load | 0.4 navigational + 0.4 sensory + 0.2 rules | Mental effort to be there |
| biophilia | 0.6 immersion + 0.4 biodiversity, + 1 if water is present | How natural it feels |
| awe | 0.6 vastness + 0.4 stimulus power | Sense of scale and power |
| novelty | highest of cultural, experiential, sensory surprise | How different from daily life |
| social_density | scored directly | How crowded |

Plus trigger tags (heights, deep_water, crowds, darkness, wildlife, steep_terrain, ...)
that users can ask to avoid. Changing a formula changes every place's scores, so rerun
`annotate` and `load-postgres` afterwards. The pipeline's annotation prompt
(`annotate.py`, `PROMPT`) describes the same rubric to the model; keep the two in step.

### The heuristics: `backend/services/wellness_engine/app/brain/heuristics.yaml`

How each need state Ears detects becomes a target profile:

```yaml
overwhelmed:
  why: "Low cognitive load and few people give an overloaded mind room to settle."
  targets:
    cognitive_load: {target: 1.5, weight: 1.0}   # ideal score, and how much it matters (0-1)
    social_density: {target: 1.5, weight: 0.8}
    biophilia: {target: 4.5, weight: 0.6}
```

To tune:

1. Edit the file (on the server, in your clone).
2. Rebuild the engine so the image picks it up: `aura up -d --build wellness_engine`.
3. Check the effect: `python3 scripts/smoke_test.py --skip-auth` prints the top places with
   their reasons, or call `/v1/brain/profile` and `/v1/recommend` by hand.
4. Commit the change with a short note of why, so later feedback can be compared with it.

Keep `pytest services/wellness_engine/tests` passing; among other things it checks that
overwhelm still favours quiet, green places and that trigger filters still hold.

---

## 9. Mobile apps

### Aura Journal (Expo, Android)

```bash
cd aura-journal-app
cp .env.example .env            # EXPO_PUBLIC_API_URL=http://192.168.0.10:8001
npm install
npx expo start                  # scan the QR code with Expo Go on the phone
```

- `EXPO_PUBLIC_API_URL` is required on a real phone. The auth URL defaults to the same host
  on port 8003; set `EXPO_PUBLIC_AUTH_URL` only if it differs (for example behind a proxy).
- The phone must be on the **NIKOS-HOMELAB** Wi-Fi, because the server is behind the
  Tenda's NAT.
- After changing `.env`, restart Expo with `npx expo start -c` so the new value is bundled.
- **Plain HTTP:** Expo Go allows `http://` URLs. An installed release APK (EAS build) blocks
  them on Android 9 and later. For a staging APK, either serve HTTPS (section 11) or allow
  cleartext with the `expo-build-properties` plugin (`android.usesCleartextTraffic: true`).
- Until login screens ship, keep `AUTH_REQUIRED=false` on the server (section 5).

### SereneScapes app

Not built yet. It will call the Wellness Engine (`/v1/recommend`) on port 8300. Nothing to
deploy for it today.

---

## 10. Day-to-day operations

**Update to the latest code**

```bash
cd /srv/apps/AURA-JOURNAL && git pull
aura up -d --build              # rebuilds only what changed; data and models are kept
python3 backend/scripts/smoke_test.py
```

**Logs and status**

```bash
aura ps
aura logs --tail 100 entry_ingestor
docker stats --no-stream        # memory per container (podman stats with Podman)
```

**Backups** (entries, users and places all live in Postgres)

```bash
mkdir -p ~/backups
docker exec aura_homelab_db pg_dump -U aura aura_journal | gzip > ~/backups/aura-$(date +%F).sql.gz

# Nightly at 02:30, keep 14 days (crontab -e):
30 2 * * * docker exec aura_homelab_db pg_dump -U aura aura_journal | gzip > ~/backups/aura-$(date +\%F).sql.gz && find ~/backups -name 'aura-*.sql.gz' -mtime +14 -delete
```

Restore into a fresh stack:

```bash
gunzip -c ~/backups/aura-2026-11-27.sql.gz | docker exec -i aura_homelab_db psql -U aura -d aura_journal
```

Copy backups off the box now and then; a backup on the same disk doesn't survive the disk.

**Reboots:** containers use `restart: always`. With Podman, `podman-restart.service`
(section 1) brings them back. With Docker, the Docker service does.

**Start fresh (deletes all data):** `aura down -v`. Without `-v` the data is kept.

---

## 11. Moving to Truehost

The same compose file and `.env` run on a VPS. What changes is that the server is on the
public internet.

### Choosing the plan

- You need a **VPS with root access** (KVM). Shared or cPanel web hosting can't run
  containers. Confirm with Truehost that the plan supports Docker before paying.
- RAM: 2 GB is enough in lexicon mode; 4 GB or more for the Hugging Face models (there's no
  Gramps Web on it to share with).
- OS: Ubuntu 24.04 LTS is the simplest choice; AlmaLinux works with the Fedora commands.
- About 15 GB disk covers images, models and data.

### Set it up (Ubuntu)

```bash
ssh root@<vps-ip>
adduser aura && usermod -aG sudo aura
# copy your SSH key, then in /etc/ssh/sshd_config: PasswordAuthentication no, PermitRootLogin no
systemctl restart ssh

curl -fsSL https://get.docker.com | sh
usermod -aG docker aura
su - aura
git clone https://github.com/nicanornicolas/AURA-JOURNAL.git ~/AURA-JOURNAL
```

Then sections 3 to 8 as on the homelab, with these differences:

| Setting | Homelab | Truehost |
|---|---|---|
| `AUTH_REQUIRED` | `false` is fine while testing on the LAN | **`true`**. Anyone can reach the server |
| `POSTGRES_PASSWORD`, `JWT_SECRET_KEY` | random | new random values, not the homelab ones |
| Firewall | firewalld, LAN | `ufw` (below) |
| Engine port 8300 | open on the LAN | closed until the SereneScapes app needs it |
| HTTP vs HTTPS | HTTP on the LAN | HTTPS once you have a domain |

```bash
sudo ufw allow OpenSSH
sudo ufw allow 8001/tcp && sudo ufw allow 8003/tcp
sudo ufw enable
```

Docker publishes ports past `ufw` rules. Postgres is safe because it's bound to
`127.0.0.1` in the compose file. To keep 8300 private, don't rely on `ufw`; change its
line in the compose file to `"127.0.0.1:8300:8300"`.

**Before login screens ship**, the phone can't use the VPS with `AUTH_REQUIRED=true`.
Keep phone testing on the homelab until then, or temporarily allow only your own IP:
`sudo ufw allow from <your-ip> to any port 8001`.

### Move the data

```bash
# homelab
docker exec aura_homelab_db pg_dump -U aura aura_journal | gzip > aura-move.sql.gz
scp aura-move.sql.gz aura@<vps-ip>:~
# VPS, after the first `aura up -d`
gunzip -c ~/aura-move.sql.gz | docker exec -i aura_homelab_db psql -U aura -d aura_journal
```

The `hf_models` volume isn't worth copying: let the VPS download the models once (section 4).

### HTTPS, once there's a domain

Point a DNS record at the VPS and put Caddy in front. It gets certificates automatically:

```
# /etc/caddy/Caddyfile
api.yourdomain.com {
    handle /auth/* {
        reverse_proxy 127.0.0.1:8003     # auth routes already start with /auth
    }
    handle {
        reverse_proxy 127.0.0.1:8001     # entries API
    }
}
```

Then bind 8001 and 8003 to
`127.0.0.1` in the compose file, close them in `ufw`, open 80 and 443, and set in the app:
`EXPO_PUBLIC_API_URL=https://api.yourdomain.com` and
`EXPO_PUBLIC_AUTH_URL=https://api.yourdomain.com`. Keep running the smoke test on the VPS
itself (`python3 backend/scripts/smoke_test.py`, which uses the local ports), and check the
public side from the laptop with `curl https://api.yourdomain.com/health`.

---

## 12. Checklist

- [ ] Server prepared, firewall open (sections 1, 2)
- [ ] Stack up in lexicon mode, smoke test passes (3)
- [ ] Seed places in Postgres, `PLACES_SOURCE=postgres`, smoke test passes (6)
- [ ] Phone writes an entry over Wi-Fi (GUIDE.md level 3)
- [ ] Hugging Face models downloaded, smoke test shows `provider=hf`, `HF_HUB_OFFLINE=1` (4)
- [ ] Ollama annotation of a small batch, checked and loaded (7)
- [ ] Nightly backups running (10)
- [ ] Truehost VPS with `AUTH_REQUIRED=true` and new secrets (11)
