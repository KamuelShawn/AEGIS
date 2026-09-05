import json
from pathlib import Path
from functools import lru_cache

DEMO_DIR = Path(__file__).parent / "demo"


@lru_cache(maxsize=None)
def load_demo(name: str) -> dict:
    """Load a demo dataset by filename stem, e.g. load_demo('forest_history')."""
    path = DEMO_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
