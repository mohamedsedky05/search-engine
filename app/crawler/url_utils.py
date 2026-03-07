"""
URL normalization and domain checks for the crawler.
"""
from urllib.parse import urljoin, urlparse, urlunparse
from typing import List, Optional


def normalize_url(url: str, base: Optional[str] = None) -> str:
    """
    Normalize URL: resolve relative to base, remove fragment, lowercase scheme/host.
    """
    url = url.strip()
    if not url:
        return ""
    if base:
        url = urljoin(base, url)
    parsed = urlparse(url)
    # Remove fragment and normalize
    normalized = urlunparse((
        parsed.scheme.lower() if parsed.scheme else "http",
        parsed.netloc.lower() if parsed.netloc else "",
        parsed.path or "/",
        parsed.params,
        parsed.query,
        "",  # no fragment
    ))
    # Ensure path ends without trailing slash for consistency (or keep / for root)
    if len(normalized) > 1 and normalized.endswith("/"):
        normalized = normalized.rstrip("/")
    return normalized


def get_domain(url: str) -> str:
    """Extract domain (netloc) from URL."""
    parsed = urlparse(url)
    return (parsed.netloc or "").lower()


def same_domain(url1: str, url2: str) -> bool:
    """Return True if both URLs belong to the same domain (netloc)."""
    return get_domain(url1) == get_domain(url2)


def is_allowed_domain(url: str, allowed_domains: List[str]) -> bool:
    """
    Return True if url's domain is in allowed_domains.
    If allowed_domains is empty, allow any domain.
    """
    if not allowed_domains:
        return True
    domain = get_domain(url)
    return domain in allowed_domains
