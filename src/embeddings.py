"""
Thin wrapper around sentence-transformers so the model is loaded once
per process (loading it is the slow part) and every other module just
calls encode().
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def encode(texts: list) -> np.ndarray:
    """Encode a list of strings into normalized embedding vectors
    (normalized so inner-product search == cosine similarity)."""
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.array(vectors, dtype="float32")
