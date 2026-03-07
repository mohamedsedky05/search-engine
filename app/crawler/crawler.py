"""
BFS web crawler with politeness delay and domain filtering.
"""
import time
from typing import List, Optional, Set, Tuple

import requests
import urllib3

from app.config import (
    CRAWLER_ALLOWED_DOMAINS,
    CRAWLER_DELAY_SECONDS,
    CRAWLER_MAX_DEPTH,
    CRAWLER_MAX_PAGES,
    CRAWLER_SEED_URLS,
    CRAWLER_TIMEOUT_SECONDS,
    CRAWLER_USER_AGENT,
    CRAWLER_VERIFY_SSL,
)
from app.crawler.parser import parse_html
from app.crawler.url_utils import get_domain, is_allowed_domain, normalize_url
from app.database import db_cursor, get_connection, init_db

if not CRAWLER_VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Crawler:
    """
    Crawls web pages from seed URLs, stores documents in SQLite.
    Uses BFS with configurable max pages, depth, and delay.
    """

    def __init__(
        self,
        seed_urls: Optional[List[str]] = None,
        max_pages: int = CRAWLER_MAX_PAGES,
        max_depth: int = CRAWLER_MAX_DEPTH,
        delay_seconds: float = CRAWLER_DELAY_SECONDS,
        allowed_domains: Optional[List[str]] = None,
        timeout: int = CRAWLER_TIMEOUT_SECONDS,
        user_agent: str = CRAWLER_USER_AGENT,
    ) -> None:
        self.seed_urls = seed_urls or CRAWLER_SEED_URLS
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.delay_seconds = delay_seconds
        self.allowed_domains = (
            allowed_domains if allowed_domains is not None else list(CRAWLER_ALLOWED_DOMAINS)
        )
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent}

        self.visited: Set[str] = set()
        self.pages_crawled = 0
        self.urls_discovered = 0
        self.errors = 0

    def _resolve_allowed_domains(self) -> None:
        """If allowed_domains is empty, infer them from seed URLs."""
        if self.allowed_domains:
            return

        for url in self.seed_urls:
            domain = get_domain(url)
            if domain and domain not in self.allowed_domains:
                self.allowed_domains.append(domain)

    def _fetch(self, url: str) -> Optional[str]:
        """Fetch a URL and return HTML text, or None on failure/non-HTML responses."""
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                headers=self.headers,
                verify=CRAWLER_VERIFY_SSL,
                allow_redirects=True,
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type.lower():
                return None

            return response.text

        except requests.RequestException as exc:
            print(f"[crawler] Failed to fetch {url}: {exc}")
            self.errors += 1
            return None

    def _insert_document(self, url: str, title: str, body_text: str, depth: int) -> int:
        """Insert a crawled document into the database and return its row id."""
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO documents (url, title, body_text, crawl_depth)
                VALUES (?, ?, ?, ?)
                """,
                (url, title, body_text, depth),
            )
            conn.commit()
            return cur.lastrowid

    def _enqueue_urls(self, urls: List[str], depth: int) -> None:
        """Add normalized, allowed, unseen URLs to the crawl queue."""
        if depth > self.max_depth:
            return

        with get_connection() as conn:
            cur = conn.cursor()

            for url in urls:
                normalized_url = normalize_url(url)

                if not normalized_url:
                    continue
                if normalized_url in self.visited:
                    continue
                if not is_allowed_domain(normalized_url, self.allowed_domains):
                    continue

                self.urls_discovered += 1
                cur.execute(
                    """
                    INSERT OR IGNORE INTO crawl_queue (url, depth)
                    VALUES (?, ?)
                    """,
                    (normalized_url, depth),
                )

            conn.commit()

    def run(self) -> Tuple[int, int, int]:
        """
        Run the crawler.

        Returns:
            Tuple[int, int, int]:
                (pages_crawled, urls_discovered, errors)
        """
        init_db()
        self._resolve_allowed_domains()

        with db_cursor() as cur:
            cur.execute("DELETE FROM crawl_queue")

            for url in self.seed_urls:
                normalized_url = normalize_url(url)
                if normalized_url:
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO crawl_queue (url, depth)
                        VALUES (?, 0)
                        """,
                        (normalized_url,),
                    )

        self.visited.clear()
        self.pages_crawled = 0
        self.urls_discovered = len(self.seed_urls)
        self.errors = 0

        while self.pages_crawled < self.max_pages:
            with db_cursor() as cur:
                cur.execute(
                    """
                    SELECT url, depth
                    FROM crawl_queue
                    ORDER BY depth, added_at
                    LIMIT 1
                    """
                )
                row = cur.fetchone()

                if not row:
                    break

                url, depth = row[0], row[1]
                cur.execute("DELETE FROM crawl_queue WHERE url = ?", (url,))

            if url in self.visited:
                continue

            self.visited.add(url)

            html = self._fetch(url)
            if not html:
                continue

            title, body_text, links = parse_html(html, base_url=url)
            doc_id = self._insert_document(url, title, body_text, depth)

            if doc_id is not None:
                self.pages_crawled += 1

            self._enqueue_urls(links, depth + 1)
            time.sleep(self.delay_seconds)

        with db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO crawl_stats (pages_crawled, urls_discovered, errors)
                VALUES (?, ?, ?)
                """,
                (self.pages_crawled, self.urls_discovered, self.errors),
            )

        return self.pages_crawled, self.urls_discovered, self.errors