"""The auth service uses flat imports (``from database import ...``), exactly as it
runs in its container, so tests put the service folder on sys.path and import the
same module objects. Otherwise dependency overrides would target a second copy."""

import os
import sys
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite://")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
