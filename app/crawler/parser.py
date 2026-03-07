"""
HTML parsing: extract title, clean body text, and outgoing links.
"""
import re
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup


# Tags to remove (noise for search)
REMOVE_TAGS = [
    "script", "style", "noscript", "iframe", "svg", "meta", "link",
    "nav", "header", "footer", "aside", "form", "button", "input",
]


def _normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace to single space and strip."""
    return re.sub(r"\s+", " ", text).strip()


def parse_html(
    html: str,
    base_url: Optional[str] = None,
) -> Tuple[str, str, List[str]]:
    """
    Parse HTML and return (title, body_text, links).
    - title: page title or empty string
    - body_text: cleaned main text, normalized whitespace
    - links: list of absolute URLs (normalization done by caller if base_url provided)
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise elements
    for tag_name in REMOVE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    title = ""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        title = _normalize_whitespace(title_tag.get_text())

    # Prefer main content containers to reduce nav clutter
    body = soup.find("body") or soup
    main_candidates = body.find_all("main") or body.find_all("article")
    if not main_candidates:
        main_candidates = body.select('[role="main"]')
    if main_candidates:
        body = main_candidates[0]

    body_text = _normalize_whitespace(body.get_text(separator=" ", strip=True))

    links: List[str] = []
    for a in body.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.lower().startswith("javascript:"):
            continue
        if base_url:
            from app.crawler.url_utils import normalize_url
            href = normalize_url(href, base_url)
        links.append(href)

    return title, body_text, links
