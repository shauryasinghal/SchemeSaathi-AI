"""
All prompt text lives here, in one place, so the grounding rules can't
drift between the extraction call and the generation call.
"""

import json

from src.models import MatchResult, UserProfile

# ---------------------------------------------------------------------
# 1. Profile extraction: turn free-text (English, Hindi, or Hinglish)
#    into a structured profile the eligibility engine can reason over.
# ---------------------------------------------------------------------

EXTRACTION_SYSTEM_PROMPT = """You extract a structured profile from a citizen's
free-text description of their situation. The text may be in English, Hindi,
or Hinglish (mixed).

Return ONLY a JSON object with these keys (use null for anything not
mentioned -- never guess or invent a value):
{
  "age": <integer or null>,
  "state": <string or null>,
  "occupation": <string or null>,
  "land_size": <string or null>,
  "income_bracket": <"low" | "middle" | "high" or null>,
  "need": <short string describing what help they want, or null>,
  "gender": <string or null>,
  "has_disability": <true | false | null>
}

Do not include any text before or after the JSON object."""


def build_extraction_prompt(raw_query: str) -> str:
    return f"Extract the profile from this text:\n\n{raw_query}"


def parse_profile_response(raw_query: str, llm_json_text: str) -> UserProfile:
    """Parses the LLM's JSON response into a UserProfile. Falls back to
    an empty profile (query-only) if parsing fails -- retrieval still
    works on raw_query even if structured extraction breaks."""
    try:
        cleaned = llm_json_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json\n", "", 1) if cleaned.startswith("json\n") else cleaned
        data = json.loads(cleaned)
    except (json.JSONDecodeError, AttributeError):
        return UserProfile(raw_query=raw_query)

    return UserProfile(
        age=data.get("age"),
        state=data.get("state"),
        occupation=data.get("occupation"),
        land_size=data.get("land_size"),
        income_bracket=data.get("income_bracket"),
        need=data.get("need"),
        gender=data.get("gender"),
        has_disability=data.get("has_disability"),
        raw_query=raw_query,
    )


# ---------------------------------------------------------------------
# 2. Final answer generation: grounded, honest, structured.
# ---------------------------------------------------------------------

ANSWER_SYSTEM_PROMPT = """You are SchemeSaathi, an assistant that helps Indian
citizens -- farmers, street vendors, artisans, students, persons with
disabilities, and other underserved communities -- understand which
government welfare schemes they may be eligible for.

STRICT RULES:
- Use ONLY the schemes provided in the CONTEXT below. Never invent a scheme,
  a benefit, or an eligibility criterion that isn't in the context.
- For each scheme, you are given a match level (High Match / Medium Match /
  Needs More Information / Low Match), what matched, what's missing, and
  what didn't match. Reflect this honestly -- do not upgrade a Medium Match
  to sound like a certainty.
- NEVER say a scheme is "approved" or that the person is "100% eligible".
  Use phrasing like "you may be eligible based on the information provided".
  Always note that final eligibility and approval are determined by the
  relevant government authority.
- If a scheme has missing information needed to assess it properly, say so
  and name what's missing.
- If nothing in the context is a good fit, say so plainly and suggest what
  kind of scheme the person should look for instead. Do not force a match.
- Write in simple, plain language -- explain like you're talking to a
  neighbour, not filing a government form. Avoid bureaucratic jargon.
- If asked to answer in Hindi, use simple, natural Hindi -- not stiff,
  overly formal bureaucratic Hindi.
- For each recommended scheme, mention: why it may fit, what documents are
  typically needed, how to apply, and that its official source should be
  checked (the app displays the source link separately -- you don't need
  to repeat the URL in your prose)."""


def build_context_block(match_results: list) -> str:
    blocks = []
    for mr in match_results:
        s = mr.scheme
        blocks.append(
            f"Scheme: {s.name}\n"
            f"Category: {s.category}\n"
            f"Match level: {mr.match_level.value}\n"
            f"Matched: {'; '.join(mr.matched_criteria) or 'none identified'}\n"
            f"Missing info: {'; '.join(mr.missing_criteria) or 'none'}\n"
            f"Did not match: {'; '.join(mr.unmatched_criteria) or 'none'}\n"
            f"Description: {s.description}\n"
            f"Eligibility (official): {'; '.join(s.eligibility)}\n"
            f"Benefits: {s.benefits}\n"
            f"Documents required: {', '.join(s.documents)}\n"
            f"How to apply: {'; '.join(s.application_process)}\n"
        )
    return "\n---\n".join(blocks)


def build_answer_prompt(profile: UserProfile, match_results: list, target_language: str) -> str:
    context = build_context_block(match_results)
    return (
        f"Person's situation (as described):\n{profile.raw_query}\n\n"
        f"Answer language: {target_language}\n\n"
        f"Candidate schemes (already retrieved and pre-assessed -- do not add others):\n"
        f"{context}\n\n"
        "Write the answer now, following all rules in the system prompt."
    )
