"""Tests for snippet generation."""
import pytest

from app.ranking.snippets import generate_snippet


def test_snippet_empty_text():
    assert generate_snippet("", ["query"]) == ""


def test_snippet_no_match():
    out = generate_snippet("Some text here without match", ["xyz"])
    assert "..." in out or len(out) <= 250
    assert "xyz" not in out.lower()


def test_snippet_includes_query_terms():
    text = "The quick brown fox jumps over the lazy dog."
    out = generate_snippet(text, ["fox"])
    assert "fox" in out.lower()


def test_snippet_highlight():
    text = "Hello world and hello again."
    out = generate_snippet(text, ["hello"], highlight=True)
    assert "<mark>" in out
    assert "Hello" in out or "hello" in out
