"""
Orchestrates the full pipeline:

    raw query
      -> profile extraction (LLM)
      -> retrieval (FAISS, local, always works)
      -> eligibility assessment (local heuristic, always works)
      -> missing-information detection
      -> LLM explanation (graceful fallback if unavailable)
      -> translation (if a non-English language was requested)

This is the one module app.py actually calls. Everything above it is
kept independently testable/importable.
"""

from dataclasses import dataclass, field

from src.config import DEFAULT_TOP_K
from src.eligibility import assess_eligibility, detect_missing_information
from src.llm import LLMError, call_llm
from src.models import MatchLevel, UserProfile
from src.prompt_engine import (
    ANSWER_SYSTEM_PROMPT,
    EXTRACTION_SYSTEM_PROMPT,
    build_answer_prompt,
    build_extraction_prompt,
    parse_profile_response,
)
from src.retriever import retrieve
from src.translator import TranslationError, translate_text
from src.utils import get_logger

logger = get_logger(__name__)


@dataclass
class RecommendationResult:
    profile: UserProfile
    match_results: list
    answer_text: str
    used_ai: bool  # False when we fell back to local-retrieval-only mode
    missing_info_prompts: list = field(default_factory=list)
    warning: str = ""  # shown to the user if something degraded gracefully


def extract_profile(raw_query: str) -> UserProfile:
    """Best-effort structured extraction. Never blocks the pipeline --
    if the LLM is unavailable, retrieval still runs on raw_query alone."""
    try:
        response = call_llm(EXTRACTION_SYSTEM_PROMPT, build_extraction_prompt(raw_query))
        return parse_profile_response(raw_query, response)
    except LLMError as e:
        logger.info("Profile extraction skipped: %s", e.user_message)
        return UserProfile(raw_query=raw_query)


def _fallback_answer(match_results: list) -> str:
    """Used when the LLM is unavailable. Explicitly labelled as NOT
    AI-generated -- never pretend this came from the model."""
    if not match_results:
        return (
            "AI explanation is temporarily unavailable. We couldn't find a closely "
            "matching scheme in the local database either -- try describing your "
            "occupation, state, and what kind of help you need."
        )
    lines = [
        "AI explanation is temporarily unavailable. Here are the most relevant "
        "schemes found in the local government-scheme database:\n"
    ]
    for mr in match_results:
        s = mr.scheme
        lines.append(f"**{s.name}** ({mr.match_level.value})")
        lines.append(f"- {s.description}")
        lines.append(f"- Benefits: {s.benefits}")
        lines.append(f"- Documents: {', '.join(s.documents)}")
        lines.append(f"- Apply: {'; '.join(s.application_process)}")
        lines.append("")
    return "\n".join(lines)


def get_recommendations(
    raw_query: str, target_language: str = "English", top_k: int = DEFAULT_TOP_K
) -> RecommendationResult:
    if not raw_query or not raw_query.strip():
        return RecommendationResult(
            profile=UserProfile(),
            match_results=[],
            answer_text="Please describe your situation so we can look for relevant schemes.",
            used_ai=False,
        )

    profile = extract_profile(raw_query)

    retrieved = retrieve(raw_query, top_k=top_k)
    match_results = [assess_eligibility(profile, scheme) for scheme in retrieved]

    # Surface the strongest matches first; never hide a low match, just
    # don't let it crowd out better ones.
    order = {MatchLevel.HIGH: 0, MatchLevel.MEDIUM: 1, MatchLevel.NEEDS_INFO: 2, MatchLevel.LOW: 3}
    match_results.sort(key=lambda mr: order[mr.match_level])

    missing_prompts = detect_missing_information(profile)

    warning = ""
    used_ai = True
    try:
        answer = call_llm(
            ANSWER_SYSTEM_PROMPT,
            build_answer_prompt(profile, match_results, target_language),
        )
    except LLMError as e:
        logger.warning("Falling back to local-only answer: %s", e.user_message)
        answer = _fallback_answer(match_results)
        used_ai = False
        warning = e.user_message
        target_language = "English"  # fallback text isn't translated

    if used_ai and target_language != "English":
        try:
            answer = translate_text(answer, target_language)
        except TranslationError as e:
            logger.warning("Translation failed, showing English: %s", e.user_message)
            warning = e.user_message

    return RecommendationResult(
        profile=profile,
        match_results=match_results,
        answer_text=answer,
        used_ai=used_ai,
        missing_info_prompts=missing_prompts,
        warning=warning,
    )
