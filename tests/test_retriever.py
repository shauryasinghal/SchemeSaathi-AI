"""
Tests real retrieval quality against the actual dataset. Unlike
test_data.py and test_eligibility.py, this module needs:
  1. sentence-transformers + faiss installed (`pip install -r requirements.txt`)
  2. The index already built (`python src/ingest.py`)
  3. Network access on the FIRST run only, to download the embedding
     model weights (cached locally after that)

This is why these are kept in a separate file: you can run test_data.py
and test_eligibility.py in any environment, but these need the full
pipeline set up first. If `python src/ingest.py` hasn't been run, these
tests are skipped with a clear message instead of failing confusingly.
"""

import unittest

from src.config import INDEX_PATH

try:
    from src.retriever import retrieve

    RETRIEVER_IMPORTABLE = True
except Exception:
    RETRIEVER_IMPORTABLE = False


@unittest.skipUnless(
    RETRIEVER_IMPORTABLE and INDEX_PATH.exists(),
    "Index not built or dependencies missing -- run `pip install -r requirements.txt` "
    "then `python src/ingest.py` before running this test file.",
)
class TestRetrieval(unittest.TestCase):
    def test_farmer_query_returns_farmer_scheme(self):
        results = retrieve(
            "I am a 45 year old farmer in Uttar Pradesh with 2 acres of land, "
            "need irrigation support",
            top_k=5,
        )
        self.assertGreater(len(results), 0)
        names = " ".join(r.name.lower() for r in results)
        self.assertTrue(
            "kisan" in names or "farmer" in names or "irrigation" in names or "sinchayee" in names,
            f"Expected a farmer/irrigation-related scheme in top results, got: "
            f"{[r.name for r in results]}",
        )

    def test_street_vendor_query_returns_svanidhi(self):
        results = retrieve(
            "I run a small street food stall and need financial support", top_k=5
        )
        names = " ".join(r.name.lower() for r in results)
        self.assertIn("svanidhi", names)

    def test_student_query_returns_scholarship(self):
        results = retrieve(
            "I am a student from a low-income family looking for scholarships", top_k=5
        )
        names = " ".join(r.name.lower() for r in results)
        self.assertTrue("scholarship" in names)

    def test_empty_query_returns_empty_list(self):
        results = retrieve("", top_k=5)
        self.assertEqual(results, [])

    def test_results_are_sorted_by_similarity_descending(self):
        results = retrieve("farmer irrigation support", top_k=5)
        similarities = [r.similarity for r in results]
        self.assertEqual(similarities, sorted(similarities, reverse=True))


if __name__ == "__main__":
    unittest.main()
