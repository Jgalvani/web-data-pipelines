from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def portal_config() -> dict:
    """Load the books_toscrape portal config."""
    import yaml

    config_path = Path(__file__).resolve().parent.parent / "config" / "portals" / "books_toscrape.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)
