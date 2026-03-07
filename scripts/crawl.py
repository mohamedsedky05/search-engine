#!/usr/bin/env python3
"""
CLI script to run the web crawler. Use from project root:
  python scripts/crawl.py
  python scripts/crawl.py --seed "https://example.com" --max-pages 20
"""
import argparse
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.crawler import Crawler
from app.database import init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl web pages and store in SQLite")
    parser.add_argument(
        "--seed",
        nargs="+",
        default=None,
        help="Seed URLs (default: from config)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Max pages to crawl",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Max depth from seed",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="Delay between requests in seconds",
    )
    args = parser.parse_args()

    init_db()
    kwargs = {}
    if args.seed is not None:
        kwargs["seed_urls"] = args.seed
    if args.max_pages is not None:
        kwargs["max_pages"] = args.max_pages
    if args.max_depth is not None:
        kwargs["max_depth"] = args.max_depth
    if args.delay is not None:
        kwargs["delay_seconds"] = args.delay
    crawler = Crawler(**kwargs)
    pages, urls, errors = crawler.run()
    print(f"Crawl complete: {pages} pages crawled, {urls} URLs discovered, {errors} errors.")
    print("Done.")


if __name__ == "__main__":
    main()
