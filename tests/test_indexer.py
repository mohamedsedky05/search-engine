"""Tests for indexer (requires DB)."""
import os
import pytest


@pytest.fixture
def use_temp_db(temp_db_path, monkeypatch):
    """Use a temporary database for indexer tests."""
    monkeypatch.setattr("app.config.DATABASE_PATH", temp_db_path)
    monkeypatch.setattr("app.database.DATABASE_PATH", temp_db_path)
    yield


def test_indexer_build_empty(use_temp_db):
    from app.database import init_db
    from app.indexing import Indexer

    init_db()
    indexer = Indexer()
    docs, terms = indexer.build()
    assert docs == 0
    assert terms == 0


def test_indexer_build_with_docs(use_temp_db):
    from app.database import init_db, db_cursor
    from app.indexing import Indexer

    init_db()
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO documents (url, title, body_text, crawl_depth) VALUES (?, ?, ?, ?)",
            ("https://example.com", "Example", "hello world hello", 0),
        )
    indexer = Indexer()
    docs, terms = indexer.build()
    assert docs == 1
    assert terms >= 1  # at least "hello" and "world"
    with db_cursor() as cur:
        cur.execute("SELECT term, doc_id, term_freq FROM index_terms WHERE term = ?", ("hello",))
        row = cur.fetchone()
        assert row is not None
        assert row[2] == 2  # term_freq
