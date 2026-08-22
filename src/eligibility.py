"""
Eligibility reasoning. This is intentionally a transparent, rule-based
heuristic over the *retrieved* schemes -- not a black box, and not a
promise of official eligibility. It exists so the app can show WHY a
scheme was suggested, WHAT'S missing, and WHAT doesn't match, instead of
just handing everything to the LLM and hoping it reasons correctly.

This module never claims certainty. The worst it will say is
"High Match" -- never "100% eligible" or "approved".
"""

import re

from src.models import MatchLevel, MatchResult, Scheme, UserProfile

# Keywords that signal a scheme is means-tested / income-restricted.
_INCOME_SIGNAL_WORDS = ["income", "below poverty", "bpl", "economically weaker", "ews"]

_LOW_INCOME_TERMS = {"low", "bpl", "below poverty line", "poor", "ews", "economically weaker"}
_HIGH_INCOME_TERMS = {"high", "wealthy", "above ceiling"}

_AGE_RANGE_PATTERN = re.compile(
    r"(?:age[sd]?\s*)?(\d{1,2})\s*(?:to|-|–)\s*(\d{1,2})\s*years?", re.IGNORECASE
)
_AGE_ABOVE_PATTERN = re.compile(r"(\d{1,2})\s*years?\s*(?:and above|or above|\+)", re.IGNORECASE)
_AGE_BELOW_PATTERN = re.compile(r"below\s*(\d{1,2})\s*years?", re.IGNORECASE)


def _text_blob(scheme: Scheme) -> str:
    return " ".join(
        [scheme.name, scheme.category, scheme.description, " ".join(scheme.eligibility), " ".join(scheme.keywords)]
    ).lower()


def _category_matches_occupation(profile: UserProfile, scheme: Scheme) -> bool:
    if not profile.occupation:
        return False
    occ = profile.occupation.lower().strip()
    blob = _text_blob(scheme)
    # direct substring match against category/keywords/description is a
    # reasonable, explainable heuristic for a hackathon-scope matcher
    return occ in blob or any(occ in kw.lower() for kw in scheme.keywords)


def _state_compatible(profile: UserProfile, scheme: Scheme) -> bool:
    if not profile.state:
        return True  # unknown -- don't penalize
    states_lower = [s.lower() for s in scheme.states]
    if "all india" in states_lower:
        return True
    return profile.state.lower() in states_lower


def _extract_age_requirement(scheme: Scheme):
    """Returns (min_age, max_age) if we can parse one from the
    eligibility text, else None. Best-effort only."""
    text = " ".join(scheme.eligibility)
    m = _AGE_RANGE_PATTERN.search(text)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = _AGE_ABOVE_PATTERN.search(text)
    if m:
        return int(m.group(1)), None
    m = _AGE_BELOW_PATTERN.search(text)
    if m:
        return None, int(m.group(1))
    return None


def _age_compatible(profile: UserProfile, scheme: Scheme):
    """Returns True/False/None (None = no age criterion found or no
    profile age to compare)."""
    if profile.age is None:
        return None
    age_req = _extract_age_requirement(scheme)
    if age_req is None:
        return None
    min_age, max_age = age_req
    if min_age is not None and profile.age < min_age:
        return False
    if max_age is not None and profile.age > max_age:
        return False
    return True


def _income_signal(profile: UserProfile, scheme: Scheme):
    """Returns 'match', 'mismatch', 'missing', or None (scheme has no
    income criterion at all)."""
    blob = _text_blob(scheme)
    has_income_criterion = any(w in blob for w in _INCOME_SIGNAL_WORDS)
    if not has_income_criterion:
        return None
    if not profile.income_bracket:
        return "missing"
    bracket = profile.income_bracket.lower()
    if any(term in bracket for term in _LOW_INCOME_TERMS):
        return "match"
    if any(term in bracket for term in _HIGH_INCOME_TERMS):
        return "mismatch"
    return "missing"


def _disability_signal(profile: UserProfile, scheme: Scheme):
    requires_disability = "disability" in scheme.category.lower() or "disabilit" in _text_blob(scheme)
    if not requires_disability:
        return None
    if profile.has_disability is True:
        return "match"
    if profile.has_disability is False:
        return "mismatch"
    return "missing"


def assess_eligibility(profile: UserProfile, scheme: Scheme) -> MatchResult:
    matched, missing, unmatched = [], [], []

    if _category_matches_occupation(profile, scheme):
        matched.append(f"Occupation/category aligns with '{scheme.category}'")

    if not _state_compatible(profile, scheme):
        unmatched.append(f"Scheme is limited to {', '.join(scheme.states)}, not {profile.state}")

    age_result = _age_compatible(profile, scheme)
    if age_result is True:
        matched.append("Age fits the scheme's stated age criterion")
    elif age_result is False:
        unmatched.append("Age falls outside the scheme's stated age criterion")
    elif profile.age is None and _extract_age_requirement(scheme):
        missing.append("Your age (this scheme has an age-based criterion)")

    income_result = _income_signal(profile, scheme)
    if income_result == "match":
        matched.append("Income level fits this scheme's means-tested criterion")
    elif income_result == "mismatch":
        unmatched.append("This scheme targets lower-income households")
    elif income_result == "missing":
        missing.append("Your approximate income level (this scheme is means-tested)")

    disability_result = _disability_signal(profile, scheme)
    if disability_result == "match":
        matched.append("Disability status fits this scheme's target group")
    elif disability_result == "mismatch":
        unmatched.append("This scheme is specifically for persons with disabilities")
    elif disability_result == "missing":
        missing.append("Whether you or the person you're asking for has a disability")

    if profile.land_size and scheme.category.lower() == "agriculture":
        matched.append("Land ownership fits this scheme's agricultural focus")
    elif scheme.category.lower() == "agriculture" and not profile.land_size:
        missing.append("Approximate land size (helps confirm agricultural scheme fit)")

    # --- classify overall match level -------------------------------
    if unmatched:
        level = MatchLevel.LOW
    elif len(matched) >= 2 and not missing:
        level = MatchLevel.HIGH
    elif matched:
        level = MatchLevel.MEDIUM
    elif missing:
        level = MatchLevel.NEEDS_INFO
    else:
        # Retrieved on semantic similarity but the heuristic found
        # nothing concrete either way -- honest middle ground, not a
        # forced high match.
        level = MatchLevel.MEDIUM

    return MatchResult(
        scheme=scheme,
        match_level=level,
        matched_criteria=matched,
        missing_criteria=missing,
        unmatched_criteria=unmatched,
    )


def detect_missing_information(profile: UserProfile) -> list:
    """Core fields worth asking for if absent, shown to the user as
    'we need a little more information to narrow this down'. Never
    includes sensitive fields the user didn't volunteer -- we only ask
    for state, occupation, and approximate income/need, not things
    like religion, caste, or exact income figures."""
    prompts = []
    if not profile.state:
        prompts.append("Your state")
    if not profile.occupation:
        prompts.append("Your occupation")
    if not profile.income_bracket:
        prompts.append("Approximate income level (e.g. low / middle / above ceiling)")
    if not profile.need:
        prompts.append("What kind of help you're looking for")
    return prompts
