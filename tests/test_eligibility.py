"""
Tests the eligibility heuristic directly against hand-built Scheme and
UserProfile objects. Deliberately does NOT touch the embedding model or
FAISS index -- this module has no ML dependency, so these tests run
anywhere, including offline / no-network CI.
"""

import unittest

from src.eligibility import assess_eligibility, detect_missing_information
from src.models import MatchLevel, Scheme, UserProfile


def make_farmer_scheme():
    return Scheme(
        id="test_farmer",
        name="Test Farmer Support Scheme",
        ministry="Ministry of Agriculture",
        category="Agriculture",
        level="Central",
        states=["All India"],
        description="Support for farmers.",
        benefits="Cash support.",
        eligibility=["Farmer owning agricultural land", "Age 18 to 60 years"],
        documents=["Aadhaar"],
        application_process=["Apply online"],
        keywords=["farmer", "agriculture"],
        source_url="https://example.gov.in",
        source_name="Test Ministry",
    )


def make_income_restricted_scholarship():
    return Scheme(
        id="test_scholarship",
        name="Test Scholarship for Economically Weaker Sections",
        ministry="Ministry of Education",
        category="Education / Scholarships",
        level="Central",
        states=["All India"],
        description="Scholarship for low-income students.",
        benefits="Annual scholarship.",
        eligibility=["Family income below the prescribed ceiling", "Enrolled student"],
        documents=["Income certificate"],
        application_process=["Apply via National Scholarship Portal"],
        keywords=["student", "scholarship", "education"],
        source_url="https://example.gov.in",
        source_name="Test Ministry",
    )


def make_maharashtra_only_scheme():
    return Scheme(
        id="test_state_scheme",
        name="Test Maharashtra-Only Scheme",
        ministry="Government of Maharashtra",
        category="Rural Development",
        level="State",
        states=["Maharashtra"],
        description="State-specific rural support.",
        benefits="Support.",
        eligibility=["Resident of Maharashtra"],
        documents=["Aadhaar"],
        application_process=["Apply at district office"],
        keywords=["rural"],
        source_url="https://example.gov.in",
        source_name="Test Ministry",
    )


class TestEligibilityMatching(unittest.TestCase):
    def test_matching_profile_gets_high_or_medium_match(self):
        profile = UserProfile(
            occupation="farmer", age=35, land_size="2 acres", raw_query="test"
        )
        scheme = make_farmer_scheme()
        result = assess_eligibility(profile, scheme)
        self.assertIn(result.match_level, (MatchLevel.HIGH, MatchLevel.MEDIUM))
        self.assertGreater(len(result.matched_criteria), 0)
        self.assertEqual(len(result.unmatched_criteria), 0)

    def test_missing_criteria_detected_for_income_scheme(self):
        profile = UserProfile(occupation="student", raw_query="test")
        scheme = make_income_restricted_scholarship()
        result = assess_eligibility(profile, scheme)
        self.assertTrue(
            any("income" in m.lower() for m in result.missing_criteria),
            f"Expected an income-related missing criterion, got: {result.missing_criteria}",
        )

    def test_non_matching_profile_flags_unmatched(self):
        profile = UserProfile(state="Delhi", occupation="rural worker", raw_query="test")
        scheme = make_maharashtra_only_scheme()
        result = assess_eligibility(profile, scheme)
        self.assertEqual(result.match_level, MatchLevel.LOW)
        self.assertGreater(len(result.unmatched_criteria), 0)

    def test_income_mismatch_is_flagged(self):
        profile = UserProfile(
            occupation="student", income_bracket="high", raw_query="test"
        )
        scheme = make_income_restricted_scholarship()
        result = assess_eligibility(profile, scheme)
        self.assertTrue(any("lower-income" in m for m in result.unmatched_criteria))

    def test_never_returns_absolute_certainty_language(self):
        """The match level enum itself should never contain '100%' or
        'approved' -- this is a structural guarantee, not just a prompt
        instruction."""
        for level in MatchLevel:
            self.assertNotIn("100%", level.value)
            self.assertNotIn("approved", level.value.lower())


class TestMissingInformationDetection(unittest.TestCase):
    def test_empty_profile_asks_for_core_fields(self):
        profile = UserProfile(raw_query="I need help")
        prompts = detect_missing_information(profile)
        self.assertIn("Your state", prompts)
        self.assertIn("Your occupation", prompts)

    def test_complete_profile_asks_for_nothing(self):
        profile = UserProfile(
            state="Bihar",
            occupation="farmer",
            income_bracket="low",
            need="irrigation support",
            raw_query="test",
        )
        prompts = detect_missing_information(profile)
        self.assertEqual(prompts, [])


if __name__ == "__main__":
    unittest.main()
