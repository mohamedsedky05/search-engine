"""
SQLite database setup and access. Uses a single file and thread-local connection pattern.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, List, Optional, Tuple

from app.config import DATABASE_PATH, get_database_dir


def _ensure_db_dir() -> None:
    get_database_dir()


def get_connection() -> sqlite3.Connection:
    """Return a new connection (caller must close or use context manager)."""
    _ensure_db_dir()
    conn = sqlite3.connect(
        DATABASE_PATH,
        timeout=60,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 60000;")
    return conn


@contextmanager
def db_cursor() -> Generator[sqlite3.Cursor, None, None]:
    """Context manager for a database cursor. Commits on success, rolls back on exception."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they do not exist."""
    _ensure_db_dir()
    with db_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                body_text TEXT NOT NULL DEFAULT '',
                crawl_depth INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS index_terms (
                term TEXT NOT NULL,
                doc_id INTEGER NOT NULL,
                term_freq INTEGER NOT NULL,
                positions TEXT NOT NULL,
                PRIMARY KEY (term, doc_id),
                FOREIGN KEY (doc_id) REFERENCES documents(id)
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_index_terms_term ON index_terms(term)
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS crawl_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pages_crawled INTEGER NOT NULL DEFAULT 0,
                urls_discovered INTEGER NOT NULL DEFAULT 0,
                errors INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS crawl_queue (
                url TEXT PRIMARY KEY,
                depth INTEGER NOT NULL DEFAULT 0,
                added_at TEXT DEFAULT (datetime('now'))
            )
        """)


def get_document_count() -> int:
    """Return total number of documents in the database."""
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM documents")
        row = cur.fetchone()
        return row[0] if row else 0


def get_index_terms_count() -> int:
    """Return number of unique terms in the index."""
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(DISTINCT term) FROM index_terms")
        row = cur.fetchone()
        return row[0] if row else 0


def get_last_crawl_stats() -> Optional[Tuple[int, int]]:
    """Return (pages_crawled, errors) for the most recent crawl, or None."""
    with db_cursor() as cur:
        cur.execute(
            "SELECT pages_crawled, errors FROM crawl_stats ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        return (row[0], row[1]) if row else None
