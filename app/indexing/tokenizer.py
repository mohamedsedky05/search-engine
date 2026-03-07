"""
Tokenization: lowercase, split on non-alphanumeric, optional stop words, min length.
"""
import re
from typing import List, Optional, Tuple

from app.config import INDEXER_MIN_TERM_LENGTH, INDEXER_STOP_WORDS

# Common English stop words (subset)
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with",
}


def tokenize(
    text: str,
    stop_words: bool = INDEXER_STOP_WORDS,
    min_length: int = INDEXER_MIN_TERM_LENGTH,
) -> List[str]:
    """
    Split text into tokens: lowercase, alphanumeric sequences only.
    Optionally filter stop words and short tokens.
    """
    if not text:
        return []
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    if stop_words:
        tokens = [t for t in tokens if t not in STOP_WORDS]
    if min_length > 0:
        tokens = [t for t in tokens if len(t) >= min_length]
    return tokens


def tokenize_with_positions(
    text: str,
    stop_words: bool = INDEXER_STOP_WORDS,
    min_length: int = INDEXER_MIN_TERM_LENGTH,
) -> List[Tuple[str, int]]:
    """
    Tokenize and return list of (term, position) where position is token index (0-based).
    Used for snippet generation and phrase matching.
    """
    if not text:
        return []
    raw = re.findall(r"[a-z0-9]+", text.lower())
    result: List[Tuple[str, int]] = []
    for i, t in enumerate(raw):
        if stop_words and t in STOP_WORDS:
            continue
        if min_length > 0 and len(t) < min_length:
            continue
        result.append((t, i))
    return result
