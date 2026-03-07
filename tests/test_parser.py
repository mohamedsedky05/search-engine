"""Tests for HTML parser."""
import pytest

from app.crawler.parser import parse_html


def test_parse_html_title_and_text():
    html = "<html><head><title>Hello World</title></head><body><p>Content here.</p></body></html>"
    title, text, links = parse_html(html)
    assert title == "Hello World"
    assert "Content here" in text
    assert links == []


def test_parse_html_strips_scripts():
    html = "<html><body><script>alert(1);</script><p>Visible</p></body></html>"
    _, text, _ = parse_html(html)
    assert "Visible" in text
    assert "alert" not in text


def test_parse_html_extracts_links():
    html = '<html><body><a href="https://example.com">Link</a><a href="#">Skip</a></body></html>'
    _, _, links = parse_html(html, base_url="https://site.com/")
    assert any("example.com" in u for u in links)
    assert not any("#" in u for u in links)


def test_parse_html_normalizes_whitespace():
    html = "<html><body>  One   \n\t  Two  </body></html>"
    _, text, _ = parse_html(html)
    assert text == "One Two"
