"""
Route handlers. These are a thin wrapper around src/ -- all the actual
retrieval, eligibility, and generation logic still lives there. This
file's only job is translating between HTTP/JSON and the existing
Python objects.

/health, /schemes, /schemes/{id}, and /compare only ever read
data/schemes.json directly, so they work even before the vector index
is built. /recommend is the one endpoint that needs `python src/ingest.py`
to have been run first (it calls src.recommender, which needs the
FAISS index).
"""

import json

from fastapi import APIRouter, HTTPException

from api.schemas import (
    CompareRequest,
    MatchResultOut,
    ProfileOut,
    RecommendRequest,
    RecommendResponse,
    SchemeOut,
    SchemeSummary,
)
from src.config import SCHEMES_PATH

router = APIRouter()


def _load_raw_schemes() -> list:
    with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload["schemes"]


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/schemes", response_model=list[SchemeSummary])
def list_schemes():
    """Lightweight listing for the Compare picker -- id/name/category
    only, so the frontend doesn't have to fetch full scheme text just
    to populate a dropdown."""
    schemes = _load_raw_schemes()
    return [
        SchemeSummary(id=s["id"], name=s["name"], category=s["category"])
        for s in schemes
    ]


@router.get("/schemes/{scheme_id}")
def get_scheme(scheme_id: str):
    schemes = _load_raw_schemes()
    for s in schemes:
        if s["id"] == scheme_id:
            return s
    raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found")


@router.post("/compare")
def compare_schemes(req: CompareRequest):
    schemes = _load_raw_schemes()
    by_id = {s["id"]: s for s in schemes}
    missing = [i for i in req.scheme_ids if i not in by_id]
    if missing:
        raise HTTPException(status_code=404, detail=f"Unknown scheme id(s): {missing}")
    return [by_id[i] for i in req.scheme_ids]


def _scheme_to_out(scheme) -> SchemeOut:
    return SchemeOut(
        id=scheme.id,
        name=scheme.name,
        ministry=scheme.ministry,
        category=scheme.category,
        level=scheme.level,
        states=scheme.states,
        description=scheme.description,
        benefits=scheme.benefits,
        eligibility=scheme.eligibility,
        documents=scheme.documents,
        application_process=scheme.application_process,
        source_url=scheme.source_url,
        source_name=scheme.source_name,
        similarity=scheme.similarity,
    )


@router.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    # Imported lazily so /health, /schemes etc. work even if the ML
    # dependencies (sentence-transformers, faiss) or the index aren't
    # ready yet -- only this endpoint pays that cost.
    from src.retriever import retrieve  # noqa: F401 (import-time check)
    from src.recommender import get_recommendations

    try:
        result = get_recommendations(req.query, target_language=req.language, top_k=req.top_k)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Vector index not built yet. Run `python src/ingest.py` on the server. ({e})",
        )

    return RecommendResponse(
        profile=ProfileOut(
            age=result.profile.age,
            state=result.profile.state,
            occupation=result.profile.occupation,
            land_size=result.profile.land_size,
            income_bracket=result.profile.income_bracket,
            need=result.profile.need,
            gender=result.profile.gender,
            has_disability=result.profile.has_disability,
        ),
        match_results=[
            MatchResultOut(
                scheme=_scheme_to_out(mr.scheme),
                match_level=mr.match_level.value,
                matched_criteria=mr.matched_criteria,
                missing_criteria=mr.missing_criteria,
                unmatched_criteria=mr.unmatched_criteria,
            )
            for mr in result.match_results
        ],
        answer_text=result.answer_text,
        used_ai=result.used_ai,
        missing_info_prompts=result.missing_info_prompts,
        warning=result.warning,
    )
