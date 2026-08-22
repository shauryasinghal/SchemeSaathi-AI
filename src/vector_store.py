"""
FAISS index management: build once (ingest.py), load and search many
times (retriever.py). The index is persisted to disk so the Streamlit
app never has to rebuild it on startup.
"""

import json

import faiss
import numpy as np

from src.config import INDEX_PATH, METADATA_PATH


def build_index(embeddings: np.ndarray) -> faiss.Index:
    """Inner-product index over normalized vectors == cosine similarity."""
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    return index


def save_index(index: faiss.Index, metadata: list) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def load_index():
    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"No index found at {INDEX_PATH}. Run `python src/ingest.py` first."
        )
    index = faiss.read_index(str(INDEX_PATH))
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata


def search(index: faiss.Index, query_vector: np.ndarray, top_k: int):
    scores, indices = index.search(query_vector, top_k)
    return scores[0], indices[0]
