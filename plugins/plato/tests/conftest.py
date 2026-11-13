import os
import sys
from pathlib import Path

# Client tests drive the real openakademeia server in-process; point OPENAKADEMEIA_REPO at its checkout (default: a sibling clone).
OPENAKADEMEIA_REPO = Path(os.environ.get("OPENAKADEMEIA_REPO", Path(__file__).resolve().parents[4] / "openakademeia"))
sys.path.insert(0, str(OPENAKADEMEIA_REPO / "src"))
