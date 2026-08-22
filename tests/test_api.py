"""
API smoke tests. /health, /schemes, /schemes/{id}, and /compare are
tested directly here -- they only read data/schemes.json, no embedding
model, FAISS index, or network needed.

/recommend is NOT tested here since it needs the vector index
(`python src/ingest.py`) and a live LLM key for the full-quality path
-- exercise that one manually after setup, or via the frontend.
"""

import unittest

try:
    from fastapi.testclient import TestClient

    from api.main import app

    CLIENT_AVAILABLE = True
except Exception:
    CLIENT_AVAILABLE = False


@unittest.skipUnless(
    CLIENT_AVAILABLE,
    "fastapi/httpx not installed -- run `pip install -r requirements.txt` first.",
)
class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_list_schemes_returns_all_schemes(self):
        resp = self.client.get("/api/schemes")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 45)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertIn("category", data[0])

    def test_get_single_scheme(self):
        resp = self.client.get("/api/schemes/scheme_001")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], "scheme_001")
        self.assertIn("eligibility", resp.json())

    def test_get_missing_scheme_returns_404(self):
        resp = self.client.get("/api/schemes/does-not-exist")
        self.assertEqual(resp.status_code, 404)

    def test_compare_returns_requested_schemes_in_order(self):
        resp = self.client.post("/api/compare", json={"scheme_ids": ["scheme_001", "scheme_024"]})
        self.assertEqual(resp.status_code, 200)
        ids = [s["id"] for s in resp.json()]
        self.assertEqual(ids, ["scheme_001", "scheme_024"])

    def test_compare_with_unknown_id_returns_404(self):
        resp = self.client.post("/api/compare", json={"scheme_ids": ["scheme_001", "not-a-real-id"]})
        self.assertEqual(resp.status_code, 404)

    def test_compare_requires_at_least_one_id(self):
        resp = self.client.post("/api/compare", json={"scheme_ids": []})
        self.assertEqual(resp.status_code, 422)  # pydantic validation error


if __name__ == "__main__":
    unittest.main()
