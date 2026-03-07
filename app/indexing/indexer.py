"""
Inverted index builder: reads documents from DB, writes term -> postings to DB.
"""
import json
from typing import Dict, List

from app.database import db_cursor, init_db
from app.indexing.tokenizer import tokenize_with_positions


class Indexer:
    """
    Builds inverted index from documents table.
    Stores: index_terms (term, doc_id, term_freq, positions as JSON array).
    """

    def __init__(self):
        pass

    def _clear_index(self) -> None:
        with db_cursor() as cur:
            cur.execute("DELETE FROM index_terms")

    def build(self) -> tuple:
        """
        Rebuild the full index from documents. Returns (documents_indexed, terms_count).
        """
        init_db()
        self._clear_index()

        with db_cursor() as cur:
            cur.execute("SELECT id, url, title, body_text FROM documents")
            rows = cur.fetchall()

        # term -> list of (doc_id, term_freq, positions)
        index: Dict[str, List[tuple]] = {}

        for row in rows:
            doc_id, url, title, body_text = row[0], row[1], row[2], row[3]
            combined = f"{title} {body_text}"
            term_positions = tokenize_with_positions(combined)

            # Aggregate by term for this doc: term -> positions
            doc_terms: Dict[str, List[int]] = {}
            for term, pos in term_positions:
                doc_terms.setdefault(term, []).append(pos)

            for term, positions in doc_terms.items():
                index.setdefault(term, []).append((
                    doc_id,
                    len(positions),
                    positions,
                ))

        # Write to DB
        with db_cursor() as cur:
            for term, postings in index.items():
                for doc_id, term_freq, positions in postings:
                    cur.execute(
                        """
                        INSERT INTO index_terms (term, doc_id, term_freq, positions)
                        VALUES (?, ?, ?, ?)
                        """,
                        (term, doc_id, term_freq, json.dumps(positions)),
                    )

        docs_count = len(rows)
        terms_count = len(index)
        return docs_count, terms_count
