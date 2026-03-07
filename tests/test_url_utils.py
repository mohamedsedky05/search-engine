"""Tests for URL normalization and domain checks."""
import pytest

# Import after path is set (conftest sets PYTHONPATH when run via pytest)
from app.crawler.url_utils import (
    normalize_url,
    get_domain,
    same_domain,
    is_allowed_domain,
)


def test_normalize_url_basic():
    # Scheme and host lowercased; path case may be preserved per RFC
    assert normalize_url("https://Example.COM/Path").startswith("https://example.com/")
    # Fragment removed; path may be / or empty
    out = normalize_url("http://foo.com/#section")
    assert out == "http://foo.com/" or out == "http://foo.com"


def test_normalize_url_with_base():
    assert normalize_url("/bar", "https://foo.com/a/b") == "https://foo.com/bar"
    assert normalize_url("page", "https://foo.com/dir/") == "https://foo.com/dir/page"


def test_get_domain():
    assert get_domain("https://sub.example.com/path") == "sub.example.com"
    assert get_domain("http://localhost:8000") == "localhost:8000"


def test_same_domain():
    assert same_domain("https://a.com/x", "https://a.com/y") is True
    assert same_domain("https://a.com", "https://b.com") is False


def test_is_allowed_domain_empty_allows_all():
    assert is_allowed_domain("https://any.com/page", []) is True


def test_is_allowed_domain_filter():
    assert is_allowed_domain("https://a.com/p", ["a.com"]) is True
    assert is_allowed_domain("https://b.com/p", ["a.com"]) is False
