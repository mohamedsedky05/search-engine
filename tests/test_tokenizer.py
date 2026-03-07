"""Tests for tokenizer."""
import pytest

from app.indexing.tokenizer import tokenize, tokenize_with_positions


def test_tokenize_lowercase():
    assert tokenize("Hello World") == ["hello", "world"]


def test_tokenize_stop_words():
    assert "the" not in tokenize("the quick brown fox")
    assert "quick" in tokenize("the quick brown fox")


def test_tokenize_min_length():
    # default min_length=2
    assert "a" not in tokenize("a bc")
    assert "bc" in tokenize("a bc")


def test_tokenize_empty():
    assert tokenize("") == []
    assert tokenize("   ") == []


def test_tokenize_with_positions():
    result = tokenize_with_positions("hello world hello")
    assert result == [("hello", 0), ("world", 1), ("hello", 2)]


def test_tokenize_with_positions_skips_stop_words():
    result = tokenize_with_positions("the cat")
    assert result == [("cat", 1)]


def test_tokenize_no_stop_words_option():
    result = tokenize("the quick", stop_words=False)
    assert "the" in result
    assert "quick" in result
