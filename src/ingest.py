"""
Builds the vector index from data/schemes.json. Run this once, and again
any time schemes.json changes:

    python src/ingest.py

This is deliberately a separate, explicit step -- the Streamlit app
(app.py) only ever loads a pre-built index, so it never re-embeds the
whole dataset on every restart.
"""

import json
import sys

from src.config import SCHEMES_PATH
from src.embeddings import encode
from src.vector_store import build_index, save_index


def load_schemes() -> list:
    with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload["schemes"]


def validate_schemes(schemes: list) -> list:
    """Real validation, not a rubber stamp -- drops and reports any
    record missing a required field instead of silently indexing it."""
    required = ["id", "name", "category", "description", "eligibility"]
    valid, errors = [], []
    seen_ids = set()

    for i, s in enumerate(schemes):
        missing = [f for f in required if not s.get(f)]
        if missing:
            errors.append(f"Record {i} missing fields {missing}: {s.get('name', '<no name>')}")
            continue
        if s["id"] in seen_ids:
            errors.append(f"Duplicate id '{s['id']}'")
            continue
        seen_ids.add(s["id"])
        valid.append(s)

    if errors:
        print("Validation warnings (records skipped):")
        for e in errors:
            print(f"  - {e}")

    return valid


def build_embedding_text(scheme: dict) -> str:
    parts = [
        scheme.get("name", ""),
        scheme.get("category", ""),
        scheme.get("description", ""),
        " ".join(scheme.get("eligibility", [])),
        " ".join(scheme.get("keywords", [])),
    ]
    return " | ".join(p for p in parts if p)


def main():
    print(f"Loading schemes from {SCHEMES_PATH} ...")
    raw_schemes = load_schemes()
    print(f"Loaded {len(raw_schemes)} raw records.")

    schemes = validate_schemes(raw_schemes)
    print(f"{len(schemes)} records passed validation.")

    if not schemes:
        print("No valid schemes to index. Aborting.", file=sys.stderr)
        sys.exit(1)

    texts = [build_embedding_text(s) for s in schemes]
    print("Encoding embeddings (first run downloads the model, may take a minute)...")
    embeddings = encode(texts)

    index = build_index(embeddings)
    save_index(index, schemes)

    print(f"Done. Indexed {len(schemes)} schemes.")


if __name__ == "__main__":
    main()
