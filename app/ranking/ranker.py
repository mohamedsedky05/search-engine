"""
TF-IDF ranking with title and phrase boosts.
"""
import math
from typing import Dict, List, Set, Tuple

from app.config import SEARCH_TITLE_BOOST, SEARCH_PHRASE_BOOST
from app.indexing.tokenizer import tokenize


def compute_tfidf(
    term_freq: int,
    doc_freq: int,
    num_docs: int,
    doc_length: int,
    avg_doc_length: float,
) -> float:
    """
    TF-IDF with length normalization (pivoted length norm would be ideal; we use simple norm).
    tf = 1 + log(tf), idf = log((N+1)/(df+1)) + 1, then divide by sqrt(doc_length/avg).
    """
    if num_docs <= 0 or doc_freq <= 0:
        return 0.0
    tf = 1.0 + math.log(1 + term_freq) if term_freq > 0 else 0.0
    idf = math.log((num_docs + 1) / (doc_freq + 1)) + 1.0
    raw = tf * idf
    if doc_length > 0 and avg_doc_length > 0:
        length_norm = math.sqrt(doc_length / avg_doc_length)
        raw = raw / max(length_norm, 0.1)
    return raw


def _get_doc_lengths(doc_terms: Dict[int, Dict[str, Tuple[int, List[int]]]]) -> Dict[int, int]:
    """Total term count per doc (for length norm)."""
    return {
        doc_id: sum(tf for tf, _ in terms.values())
        for doc_id, terms in doc_terms.items()
    }


def rank_documents(
    query_terms: List[str],
    query_phrase_terms: List[str],
    doc_terms: Dict[int, Dict[str, Tuple[int, List[int]]]],
    doc_titles: Dict[int, str],
    num_docs: int,
    title_boost: float = SEARCH_TITLE_BOOST,
    phrase_boost: float = SEARCH_PHRASE_BOOST,
) -> List[Tuple[int, float]]:
    """
    Rank candidate doc_ids by TF-IDF + title boost + phrase boost.
    doc_terms: doc_id -> { term -> (term_freq, positions) }
    doc_titles: doc_id -> title string
    Returns list of (doc_id, score) sorted by score descending.
    """
    if not doc_terms or num_docs <= 0:
        return []

    doc_lengths = _get_doc_lengths(doc_terms)
    avg_len = sum(doc_lengths.values()) / len(doc_lengths) if doc_lengths else 1.0

    doc_freq: Dict[str, int] = {}
    for terms in doc_terms.values():
        for t in terms:
            doc_freq[t] = doc_freq.get(t, 0) + 1

    scores: Dict[int, float] = {}
    query_term_set: Set[str] = set(query_terms)

    for doc_id, terms in doc_terms.items():
        score = 0.0
        doc_len = doc_lengths.get(doc_id, 1)

        for term in query_term_set:
            if term not in terms:
                continue
            tf, _ = terms[term]
            df = doc_freq.get(term, 1)
            score += compute_tfidf(tf, df, num_docs, doc_len, avg_len)

        # Title boost: terms in title get extra weight (use same tokenization as index)
        title = doc_titles.get(doc_id) or ""
        title_tokens = set(tokenize(title))
        for term in query_term_set:
            if term in title_tokens:
                score *= title_boost
                break

        # Phrase boost: if query had a phrase, check for consecutive token positions in this doc
        applied_phrase_boost = False
        if query_phrase_terms and len(query_phrase_terms) >= 2:
            term_map = doc_terms.get(doc_id, {})
            pos_lists = [term_map.get(t) for t in query_phrase_terms]
            if not any(p is None for p in pos_lists):
                for idx, (_, first_positions) in enumerate(pos_lists):
                    if idx > 0:
                        break
                    for p in first_positions:
                        found = True
                        for j in range(1, len(query_phrase_terms)):
                            _, other_positions = pos_lists[j]
                            if p + j not in other_positions:
                                found = False
                                break
                        if found:
                            score *= phrase_boost
                            applied_phrase_boost = True
                            break
                    if applied_phrase_boost:
                        break

        scores[doc_id] = score

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return [(doc_id, s) for doc_id, s in ranked if s > 0]
