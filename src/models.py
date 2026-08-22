"""
Shared data structures used across the pipeline. Keeping these in one
place means retriever, eligibility, and prompt_engine all agree on the
same shapes.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


@dataclass
class Scheme:
    id: str
    name: str
    ministry: str
    category: str
    level: str
    states: list
    description: str
    benefits: str
    eligibility: list
    documents: list
    application_process: list
    keywords: list
    source_url: str
    source_name: str
    last_verified: Optional[str] = None
    similarity: Optional[float] = None  # populated only on retrieval results

    @classmethod
    def from_dict(cls, d: dict) -> "Scheme":
        known_fields = {
            "id", "name", "ministry", "category", "level", "states",
            "description", "benefits", "eligibility", "documents",
            "application_process", "keywords", "source_url", "source_name",
            "last_verified",
        }
        filtered = {k: v for k, v in d.items() if k in known_fields}
        return cls(**filtered)


class MatchLevel(str, Enum):
    HIGH = "High Match"
    MEDIUM = "Medium Match"
    NEEDS_INFO = "Needs More Information"
    LOW = "Low Match"


@dataclass
class UserProfile:
    """Structured profile extracted from the user's free-text query.
    Every field is optional -- we never force the user to provide
    sensitive information (see eligibility.py for how missing fields
    are handled)."""

    age: Optional[int] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    land_size: Optional[str] = None
    income_bracket: Optional[str] = None
    need: Optional[str] = None
    gender: Optional[str] = None
    has_disability: Optional[bool] = None
    raw_query: str = ""

    def filled_fields(self) -> list:
        skip = {"raw_query"}
        return [
            k for k, v in self.__dict__.items()
            if k not in skip and v not in (None, "")
        ]


@dataclass
class MatchResult:
    scheme: Scheme
    match_level: MatchLevel
    matched_criteria: list = field(default_factory=list)
    missing_criteria: list = field(default_factory=list)
    unmatched_criteria: list = field(default_factory=list)
