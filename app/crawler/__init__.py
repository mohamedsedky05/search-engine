"""
Web crawler components: URL handling, HTML parsing, and crawling logic.
"""
from app.crawler.crawler import Crawler
from app.crawler.parser import parse_html
from app.crawler.url_utils import normalize_url, same_domain, is_allowed_domain

__all__ = [
    "Crawler",
    "parse_html",
    "normalize_url",
    "same_domain",
    "is_allowed_domain",
]
