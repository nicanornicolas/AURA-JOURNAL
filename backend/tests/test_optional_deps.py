"""The Wellness Engine image has no pymongo: importing ``shared`` must not need it."""

import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def test_shared_imports_without_pymongo():
    code = "import sys; sys.modules['pymongo'] = None; import shared; print('ok')"
    r = subprocess.run([sys.executable, "-c", code], cwd=BACKEND, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
