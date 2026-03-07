"""
Application configuration. Loads from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from typing import List

# Base paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Database
DATABASE_PATH = os.getenv(
    "SEARCH_ENGINE_DB_PATH",
    str(PROJECT_ROOT / "data" / "search_engine.db")
)

# Crawler
CRAWLER_SEED_URLS: List[str] = os.getenv(
    "CRAWLER_SEED_URLS",
    "https://example.com"
).split(",")

CRAWLER_MAX_PAGES = int(os.getenv("CRAWLER_MAX_PAGES", "50"))
CRAWLER_MAX_DEPTH = int(os.getenv("CRAWLER_MAX_DEPTH", "2"))
CRAWLER_DELAY_SECONDS = float(os.getenv("CRAWLER_DELAY_SECONDS", "1.0"))

# Empty = allow any domain discovered from seeds
CRAWLER_ALLOWED_DOMAINS: List[str] = []

CRAWLER_TIMEOUT_SECONDS = int(os.getenv("CRAWLER_TIMEOUT_SECONDS", "10"))

CRAWLER_USER_AGENT = os.getenv(
    "CRAWLER_USER_AGENT",
    "MiniSearchEngine/1.0 (Educational crawler; contact for removal)"
)

# SSL verification control for crawler requests
# False by default to avoid SSL certificate issues on some local environments
CRAWLER_VERIFY_SSL = os.getenv(
    "CRAWLER_VERIFY_SSL",
    "false"
).lower() == "true"

# Indexing
INDEXER_STOP_WORDS = True
INDEXER_MIN_TERM_LENGTH = 2

# Search
SEARCH_RESULTS_PER_PAGE = int(os.getenv("SEARCH_RESULTS_PER_PAGE", "10"))
SEARCH_TITLE_BOOST = float(os.getenv("SEARCH_TITLE_BOOST", "2.0"))
SEARCH_PHRASE_BOOST = float(os.getenv("SEARCH_PHRASE_BOOST", "1.5"))
SEARCH_SNIPPET_MAX_LENGTH = int(os.getenv("SEARCH_SNIPPET_MAX_LENGTH", "200"))
SEARCH_SNIPPET_CONTEXT_WORDS = int(os.getenv("SEARCH_SNIPPET_CONTEXT_WORDS", "15"))

# Server
HOST = os.getenv("SEARCH_ENGINE_HOST", "0.0.0.0")
PORT = int(os.getenv("SEARCH_ENGINE_PORT", "8000"))


def get_database_dir() -> Path:
    """
    Return directory containing the database file and ensure it exists.
    """
    path = Path(DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.parent