"""
Pytest configuration and shared fixtures.
"""
import os
import tempfile
from pathlib import Path

import pytest

# Project root
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
sys_path = str(PROJECT_ROOT)
if sys_path not in os.environ.get("PYTHONPATH", ""):
    os.environ["PYTHONPATH"] = sys_path + os.pathsep + os.environ.get("PYTHONPATH", "")


@pytest.fixture
def temp_db_path():
    """Use a temporary database for tests that need DB."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass
