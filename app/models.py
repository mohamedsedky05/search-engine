"""
Data models used across the application (in-memory representations).
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Document:
    """A crawled document ready for indexing."""
    url: str
    title: str
    body_text: str
    doc_id: Optional[int] = None
    crawl_depth: int = 0


@dataclass
class Posting:
    """Single posting in the inverted index: one term in one document."""
    doc_id: int
    term_freq: int
    positions: List[int]  # character or token positions for snippet generation


@dataclass
class IndexTerm:
    """Index entry for a term: document frequency and list of postings."""
    term: str
    doc_freq: int
    postings: List[Posting]


@dataclass
class SearchResult:
    """A single search result with metadata for display."""
    doc_id: int
    url: str
    title: str
    snippet: str
    score: float
