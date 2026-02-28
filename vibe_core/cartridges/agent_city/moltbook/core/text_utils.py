"""Shared text utilities for Moltbook content pipeline.

Tokenization and Jaccard similarity for topic matching and semantic verification.
Used by strategy.py (topic matching) and composer.py (post-output verification).
"""

# Stop words — common English words that carry no topical signal
STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of",
    "is", "are", "was", "were", "be", "been", "this", "that", "with",
    "from", "by", "it", "its", "as", "not", "but", "no", "all", "any",
    "do", "does", "did", "can", "could", "would", "should", "will",
    "may", "might", "must", "shall", "has", "have", "had", "about",
    "into", "over", "after", "before", "more", "most", "very", "just",
    "also", "how", "what", "which", "who", "whom", "when", "where",
    "why", "than", "then", "so", "if", "only", "own", "same", "too",
    "each", "every", "both", "few", "some", "such", "other",
})


def tokenize(text: str) -> frozenset:
    """Tokenize text into content words for Jaccard similarity.

    Strips punctuation, removes stop words and short tokens (<=2 chars).
    Returns frozenset for O(1) set operations.
    """
    tokens = set()
    for word in text[:200].lower().split():
        clean = "".join(c for c in word if c.isalnum())
        if clean and clean not in STOP_WORDS and len(clean) > 2:
            tokens.add(clean)
    return frozenset(tokens)


def keyword_jaccard(text_a: str, text_b: str) -> float:
    """Keyword Jaccard similarity between two texts.

    Returns 0.0 to 1.0. Stop-words removed, punctuation stripped.
    """
    tokens_a = tokenize(text_a)
    tokens_b = tokenize(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return intersection / union if union > 0 else 0.0
