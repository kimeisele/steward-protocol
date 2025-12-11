"""
PROJECT JNANA: Semantic Intelligence Module

This module provides offline AI capabilities (embeddings, semantic search)
with lazy-loading to keep kernel boot fast when not needed.

Usage:
    # Install semantic dependencies first:
    pip install steward-protocol[semantic]

    # Then use:
    from vibe_core import semantic
    embedding = semantic.embed("Hello world")
    similar = semantic.search(query, documents)

Architecture:
    - Kernel boots WITHOUT loading torch/transformers (fast)
    - This module lazy-loads on first use (slow first call, fast after)
    - Graceful error if dependencies not installed
"""

import logging
from typing import Any, List, Optional, Union

logger = logging.getLogger("SEMANTIC")

# Lazy-loaded components
_model = None
_model_name = "all-MiniLM-L6-v2"  # Default model - fast and good quality


class SemanticNotAvailableError(ImportError):
    """Raised when semantic dependencies are not installed."""

    def __init__(self):
        super().__init__(
            "Semantic capabilities require additional dependencies.\n"
            "Install with: pip install steward-protocol[semantic]\n"
            "Or: pip install sentence-transformers numpy"
        )


def _ensure_loaded() -> Any:
    """Lazy-load the sentence transformer model on first use."""
    global _model

    if _model is not None:
        return _model

    try:
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading semantic model: {_model_name}")
        _model = SentenceTransformer(_model_name)
        logger.info(f"Semantic model loaded successfully")
        return _model
    except ImportError as e:
        raise SemanticNotAvailableError() from e


def is_available() -> bool:
    """Check if semantic capabilities are available (dependencies installed)."""
    try:
        import sentence_transformers  # noqa: F401
        import numpy  # noqa: F401

        return True
    except ImportError:
        return False


def embed(text: Union[str, List[str]], normalize: bool = True) -> Any:
    """
    Generate embeddings for text.

    Args:
        text: Single string or list of strings to embed
        normalize: Whether to L2-normalize embeddings (default: True)

    Returns:
        numpy.ndarray: Embedding vector(s)
        - Single text: shape (384,) for MiniLM
        - List of texts: shape (n, 384)

    Example:
        >>> from vibe_core import semantic
        >>> vec = semantic.embed("Hello world")
        >>> vec.shape
        (384,)
    """
    model = _ensure_loaded()
    return model.encode(text, normalize_embeddings=normalize)


def similarity(text1: str, text2: str) -> float:
    """
    Calculate cosine similarity between two texts.

    Args:
        text1: First text
        text2: Second text

    Returns:
        float: Similarity score between -1 and 1 (1 = identical meaning)

    Example:
        >>> semantic.similarity("Hello", "Hi there")
        0.72
    """
    import numpy as np

    vec1 = embed(text1, normalize=True)
    vec2 = embed(text2, normalize=True)
    return float(np.dot(vec1, vec2))


def search(query: str, documents: List[str], top_k: int = 5) -> List[dict]:
    """
    Semantic search: find most similar documents to query.

    Args:
        query: Search query
        documents: List of documents to search
        top_k: Number of results to return

    Returns:
        List of dicts with 'document', 'index', 'score'

    Example:
        >>> docs = ["Python is great", "Java is verbose", "Rust is fast"]
        >>> semantic.search("programming language speed", docs, top_k=2)
        [{'document': 'Rust is fast', 'index': 2, 'score': 0.68}, ...]
    """
    import numpy as np

    if not documents:
        return []

    query_vec = embed(query, normalize=True)
    doc_vecs = embed(documents, normalize=True)

    # Cosine similarity (normalized vectors = dot product)
    scores = np.dot(doc_vecs, query_vec)

    # Sort by score descending
    indices = np.argsort(scores)[::-1][:top_k]

    return [{"document": documents[i], "index": int(i), "score": float(scores[i])} for i in indices]


def set_model(model_name: str) -> None:
    """
    Change the embedding model.

    Args:
        model_name: HuggingFace model name or path

    Popular models:
        - "all-MiniLM-L6-v2": Fast, good quality (default)
        - "all-mpnet-base-v2": Better quality, slower
        - "paraphrase-multilingual-MiniLM-L12-v2": Multilingual
    """
    global _model, _model_name
    _model = None  # Force reload
    _model_name = model_name
    logger.info(f"Semantic model changed to: {model_name}")


def get_model_info() -> dict:
    """Get information about the current model."""
    return {
        "model_name": _model_name,
        "loaded": _model is not None,
        "available": is_available(),
    }


# Kernel integration point
def get_embedding_dimension() -> int:
    """Get the embedding dimension of the current model."""
    if not is_available():
        return 384  # Default for MiniLM
    model = _ensure_loaded()
    return model.get_sentence_embedding_dimension()
