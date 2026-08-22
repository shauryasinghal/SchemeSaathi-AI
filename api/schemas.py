"""API request/response models. Kept separate from src/models.py (the
dataclasses used internally by the pipeline) so the wire format can
evolve independently of the domain model."""

from typing import List, Optional

from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Free-text description of the person's situation")
    language: str = Field(default="English", description="Answer language: 'English' or 'Hindi'")
    top_k: int = Field(default=6, ge=1, le=10)


class SchemeOut(BaseModel):
    id: str
    name: str
    ministry: str
    category: str
    level: str
    states: List[str]
    description: str
    benefits: str
    eligibility: List[str]
    documents: List[str]
    application_process: List[str]
    source_url: str
    source_name: str
    similarity: Optional[float] = None


class SchemeSummary(BaseModel):
    id: str
    name: str
    category: str


class MatchResultOut(BaseModel):
    scheme: SchemeOut
    match_level: str
    matched_criteria: List[str]
    missing_criteria: List[str]
    unmatched_criteria: List[str]


class ProfileOut(BaseModel):
    age: Optional[int] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    land_size: Optional[str] = None
    income_bracket: Optional[str] = None
    need: Optional[str] = None
    gender: Optional[str] = None
    has_disability: Optional[bool] = None


class RecommendResponse(BaseModel):
    profile: ProfileOut
    match_results: List[MatchResultOut]
    answer_text: str
    used_ai: bool
    missing_info_prompts: List[str]
    warning: str = ""


class CompareRequest(BaseModel):
    scheme_ids: List[str] = Field(..., min_length=1, max_length=3)
