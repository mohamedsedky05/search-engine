"""
Search service: query parsing, index lookup, ranking, snippets.
"""
import json
import re
from typing import List, Optional, Tuple

from app.config import SEARCH_RESULTS_PER_PAGE
from app.database import db_cursor, get_document_count
from app.indexing.tokenizer import tokenize
from app.models import SearchResult
from app.ranking.ranker import rank_documents
from app.ranking.snippets import generate_snippet


def parse_query(query: str) -> Tuple[List[str], List[str]]:
    """
    Parse search query into flat terms and phrase terms.
    Phrases are quoted, e.g. "exact phrase" -> phrase_terms ["exact", "phrase"].
    Returns (all_terms, phrase_terms). Phrase terms are also in all_terms.
    """
    query = (query or "").strip()
    if not query:
        return [], []

    all_terms: List[str] = []
    phrase_terms: List[str] = []

    # Extract quoted phrases
    phrase_pattern = re.compile(r'"([^"]+)"')
    remaining = query
    for m in phrase_pattern.finditer(query):
        phrase = m.group(1).strip()
        if phrase:
            tokens = tokenize(phrase)
            phrase_terms.extend(tokens)
            all_terms.extend(tokens)
        remaining = remaining.replace(m.group(0), " ")

    # Remaining unquoted tokens
    for word in remaining.split():
        tokens = tokenize(word)
        all_terms.extend(tokens)

    # Deduplicate while preserving order for phrase detection
    seen = set()
    unique_terms = []
    for t in all_terms:
        if t not in seen:
            seen.add(t)
            unique_terms.append(t)

    return unique_terms, phrase_terms


class SearchService:
    """Execute search against the inverted index and return ranked results with snippets."""

    def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = SEARCH_RESULTS_PER_PAGE,
    ) -> Tuple[List[SearchResult], int]:
        """
        Search and return (list of SearchResult, total_count).
        """
        query_terms, phrase_terms = parse_query(query)
        if not query_terms:
            return [], 0

        with db_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM documents")
            num_docs = cur.fetchone()[0]

            if num_docs == 0:
                return [], 0

            # Load postings for each query term
            doc_terms: dict = {}  # doc_id -> { term -> (tf, positions) }
            doc_titles: dict = {}  # doc_id -> title
            doc_bodies: dict = {}  # doc_id -> body_text
            doc_urls: dict = {}   # doc_id -> url

            for term in query_terms:
                cur.execute(
                    "SELECT doc_id, term_freq, positions FROM index_terms WHERE term = ?",
                    (term,),
                )
                for row in cur.fetchall():
                    doc_id, tf, positions_json = row[0], row[1], row[2]
                    positions = json.loads(positions_json) if positions_json else []
                    doc_terms.setdefault(doc_id, {})[term] = (tf, positions)

            # Load doc metadata for candidates
            if doc_terms:
                placeholders = ",".join("?" * len(doc_terms))
                cur.execute(
                    f"SELECT id, url, title, body_text FROM documents WHERE id IN ({placeholders})",
                    list(doc_terms.keys()),
                )
                for row in cur.fetchall():
                    doc_id, url, title, body_text = row[0], row[1], row[2], row[3]
                    doc_urls[doc_id] = url or ""
                    doc_titles[doc_id] = title or ""
                    doc_bodies[doc_id] = body_text or ""

            ranked = rank_documents(
                query_terms,
                phrase_terms,
                doc_terms,
                doc_titles,
                num_docs,
            )

            total = len(ranked)
            start = (page - 1) * per_page
            end = start + per_page
            page_slice = ranked[start:end]

            results = []
            for doc_id, score in page_slice:
                url = doc_urls.get(doc_id, "")
                title = doc_titles.get(doc_id, "")
                body = doc_bodies.get(doc_id, "")
                snippet = generate_snippet(body or title, query_terms)
                results.append(
                    SearchResult(
                        doc_id=doc_id,
                        url=url,
                        title=title or url,
                        snippet=snippet,
                        score=round(score, 4),
                    )
                )

            return results, total
