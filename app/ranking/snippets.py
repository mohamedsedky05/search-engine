"""
Snippet generation: extract a short passage around query terms with optional highlighting.
"""
import re
from typing import List, Optional

from app.config import SEARCH_SNIPPET_CONTEXT_WORDS, SEARCH_SNIPPET_MAX_LENGTH
from app.indexing.tokenizer import tokenize_with_positions


def generate_snippet(
    text: str,
    query_terms: List[str],
    max_length: int = SEARCH_SNIPPET_MAX_LENGTH,
    context_words: int = SEARCH_SNIPPET_CONTEXT_WORDS,
    highlight: bool = True,
    highlight_tag: str = "mark",
) -> str:
    """
    Extract a snippet from text that includes query terms, with optional HTML highlighting.
    Uses token positions to center snippet around first match.
    """
    if not text or not query_terms:
        return ""

    term_set = set(t.lower() for t in query_terms)
    tokens_with_pos = tokenize_with_positions(text)

    if not tokens_with_pos:
        # Fallback: truncate raw text
        cleaned = re.sub(r"\s+", " ", text).strip()
        return cleaned[:max_length] + ("..." if len(cleaned) > max_length else "")

    # Find first position where any query term appears
    first_match_idx: Optional[int] = None
    for i, (term, _) in enumerate(tokens_with_pos):
        if term in term_set:
            first_match_idx = i
            break

    if first_match_idx is None:
        return text[:max_length].strip() + ("..." if len(text) > max_length else "")

    # Span: [start, end) in token indices
    start = max(0, first_match_idx - context_words)
    end = min(len(tokens_with_pos), first_match_idx + context_words + 1)

    tokens = [t for t, _ in tokens_with_pos[start:end]]
    snippet = " ".join(tokens)

    if len(snippet) > max_length:
        snippet = snippet[: max_length - 3].rsplit(" ", 1)[0] + "..."

    if highlight and highlight_tag:
        pattern = re.compile(
            r"(\b" + "|".join(re.escape(t) for t in term_set) + r"\b)",
            re.IGNORECASE,
        )
        snippet = pattern.sub(
            f"<{highlight_tag}>\\1</{highlight_tag}>",
            snippet,
        )

    return snippet
