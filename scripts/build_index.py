#!/usr/bin/env python3
"""
CLI script to build the search index from crawled documents. Use from project root:
  python scripts/build_index.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db
from app.indexing import Indexer


def main() -> None:
    init_db()
    indexer = Indexer()
    docs_count, terms_count = indexer.build()
    print(f"Index built: {docs_count} documents, {terms_count} unique terms.")


if __name__ == "__main__":
    main()
