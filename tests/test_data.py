"""
Validates data/schemes.json structurally. No network/model dependency --
these tests run with just the standard library plus the file itself.
"""

import json
import unittest
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "schemes.json"
REQUIRED_FIELDS = [
    "id", "name", "ministry", "category", "level", "states", "description",
    "benefits", "eligibility", "documents", "application_process",
    "keywords", "source_url", "source_name",
]


class TestSchemeData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
        cls.schemes = payload["schemes"]

    def test_dataset_not_empty(self):
        self.assertGreater(len(self.schemes), 0, "Dataset should not be empty")

    def test_required_fields_present(self):
        for s in self.schemes:
            for field in REQUIRED_FIELDS:
                self.assertIn(field, s, f"Scheme '{s.get('id')}' missing field '{field}'")

    def test_ids_are_unique(self):
        ids = [s["id"] for s in self.schemes]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate scheme ids found")

    def test_names_are_non_empty(self):
        for s in self.schemes:
            self.assertTrue(s["name"].strip(), f"Scheme '{s['id']}' has an empty name")

    def test_source_urls_look_valid(self):
        for s in self.schemes:
            url = s["source_url"]
            self.assertTrue(
                url.startswith("https://") or url.startswith("http://"),
                f"Scheme '{s['id']}' has a malformed source_url: {url}",
            )

    def test_eligibility_and_documents_are_lists(self):
        for s in self.schemes:
            self.assertIsInstance(s["eligibility"], list, f"'{s['id']}' eligibility should be a list")
            self.assertIsInstance(s["documents"], list, f"'{s['id']}' documents should be a list")
            self.assertGreater(len(s["eligibility"]), 0, f"'{s['id']}' has no eligibility criteria listed")

    def test_states_field_present_and_nonempty(self):
        for s in self.schemes:
            self.assertIsInstance(s["states"], list)
            self.assertGreater(len(s["states"]), 0)


if __name__ == "__main__":
    unittest.main()
