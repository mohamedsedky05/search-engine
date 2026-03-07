"""Tests for TF-IDF ranker."""
import pytest

from app.ranking.ranker import compute_tfidf, rank_documents


def test_compute_tfidf_basic():
    score = compute_tfidf(term_freq=2, doc_freq=1, num_docs=10, doc_length=100, avg_doc_length=100)
    assert score > 0


def test_compute_tfidf_zero_doc_freq():
    assert compute_tfidf(1, 0, 10, 100, 100) == 0.0


def test_compute_tfidf_length_norm():
    # Longer doc should get slightly penalized
    s_short = compute_tfidf(2, 1, 10, 50, 100)
    s_long = compute_tfidf(2, 1, 10, 200, 100)
    assert s_short > s_long


def test_rank_documents_empty_candidates():
    assert rank_documents(
        ["q"], [], {}, {}, 10
    ) == []


def test_rank_documents_single_doc():
    doc_terms = {1: {"hello": (2, [0, 5]), "world": (1, [1])}}
    doc_titles = {1: "Hello World"}
    ranked = rank_documents(
        ["hello", "world"],
        [],
        doc_terms,
        doc_titles,
        num_docs=5,
    )
    assert len(ranked) == 1
    assert ranked[0][0] == 1
    assert ranked[0][1] > 0


def test_rank_documents_title_boost():
    doc_terms = {
        1: {"term": (1, [0])},
        2: {"term": (1, [0])},
    }
    doc_titles = {1: "other", 2: "term in title"}
    ranked = rank_documents(
        ["term"],
        [],
        doc_terms,
        doc_titles,
        num_docs=10,
        title_boost=2.0,
    )
    assert len(ranked) == 2
    # Doc 2 has term in title, should rank higher
    assert ranked[0][0] == 2
