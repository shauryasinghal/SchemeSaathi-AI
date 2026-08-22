"""
Retrieval layer. Loads the persisted index once per process and answers
top-k queries against it.
"""

from src.config import DEFAULT_TOP_K
from src.embeddings import encode
from src.models import Scheme
from src.vector_store import load_index, search

_index = None
_metadata = None


def _ensure_loaded():
    global _index, _metadata
    if _index is None:
        _index, _metadata = load_index()


def retrieve(query: str, top_k: int = DEFAULT_TOP_K) -> list:
    """Return the top_k Scheme objects most relevant to the query, each
    with .similarity populated. Returns [] for an empty query rather
    than raising, so callers can handle that case gracefully."""
    if not query or not query.strip():
        return []

    _ensure_loaded()

    query_vector = encode([query])
    scores, indices = search(_index, query_vector, top_k)

    results = []
    for score, idx in zip(scores, indices):
        if idx == -1:
            continue
        scheme = Scheme.from_dict(_metadata[idx])
        scheme.similarity = float(score)
        results.append(scheme)
    return results


def get_by_id(scheme_id: str):
    """Look up a single scheme by id, used by the Compare Schemes feature.
    Returns None if the index hasn't been built yet or the id isn't found."""
    try:
        _ensure_loaded()
    except FileNotFoundError:
        return None
    for record in _metadata:
        if record.get("id") == scheme_id:
            return Scheme.from_dict(record)
    return None


def all_scheme_ids_and_names() -> list:
    """Used to populate the Compare Schemes picker without needing a
    fresh retrieval query."""
    try:
        _ensure_loaded()
    except FileNotFoundError:
        return []
    return [(r["id"], r["name"]) for r in _metadata]


if __name__ == "__main__":
    # Manual smoke test: python src/retrieve.py
    for q in [
        "I am a 45 year old farmer in Uttar Pradesh with 2 acres of land, need irrigation support",
        "I run a small street food stall and need financial support",
        "I am a student from a low-income family looking for scholarships",
    ]:
        print(f"\nQuery: {q}")
        for r in retrieve(q, top_k=3):
            print(f"  - {r.name}  (similarity={r.similarity:.3f})")
