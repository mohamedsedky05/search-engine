"""Tests for search service and query parsing."""
import pytest

from app.search.service import parse_query, SearchService


def test_parse_query_simple():
    terms, phrase = parse_query("hello world")
    assert "hello" in terms
    assert "world" in terms
    assert phrase == []


def test_parse_query_phrase():
    terms, phrase = parse_query('"exact phrase"')
    assert "exact" in terms
    assert "phrase" in terms
    assert phrase == ["exact", "phrase"]


def test_parse_query_mixed():
    terms, phrase = parse_query('foo "bar baz" qux')
    assert "foo" in terms
    assert "bar" in terms
    assert "baz" in terms
    assert "qux" in terms
    assert "bar" in phrase and "baz" in phrase


def test_parse_query_empty():
    terms, phrase = parse_query("")
    assert terms == []
    assert phrase == []


def test_parse_query_stop_words_removed():
    terms, _ = parse_query("the a and")
    assert terms == []


def test_search_service_empty_query():
    """Empty query returns no results without hitting DB."""
    svc = SearchService()
    results, total = svc.search("")
    assert results == []
    assert total == 0
