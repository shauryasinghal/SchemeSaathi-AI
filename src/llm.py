"""
Provider-agnostic LLM wrapper. Gemini is the default provider (per
project requirements); OpenAI is supported as a drop-in alternative by
setting LLM_PROVIDER=openai in .env. Adding a third provider means
adding one branch in call_llm(), not touching prompt_engine.py,
recommender.py, or app.py.

Every error is caught here and turned into an LLMError with a plain,
user-safe message -- callers (recommender.py) never see a raw stack
trace, and can fall back to local-retrieval-only mode.
"""

from src.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


class LLMError(Exception):
    """Raised for any LLM failure. .user_message is safe to show
    directly in the UI -- never expose the raw underlying exception."""

    def __init__(self, user_message: str, cause: Exception = None):
        super().__init__(user_message)
        self.user_message = user_message
        self.cause = cause


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise LLMError(
            "AI explanation is temporarily unavailable (no Gemini API key configured)."
        )
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
            ),
        )
        text = getattr(response, "text", None)
        if not text:
            raise LLMError("AI explanation is temporarily unavailable (empty response from Gemini).")
        return text
    except LLMError:
        raise
    except Exception as e:
        msg = str(e).lower()
        if "api key" in msg or "auth" in msg or "401" in msg or "permission" in msg:
            raise LLMError(
                "AI explanation is temporarily unavailable (invalid or missing Gemini API key).",
                cause=e,
            )
        if "timeout" in msg or "deadline" in msg:
            raise LLMError(
                "AI explanation is temporarily unavailable (the request timed out).", cause=e
            )
        raise LLMError(
            "AI explanation is temporarily unavailable due to an unexpected error.", cause=e
        )


def _call_openai(system_prompt: str, user_prompt: str) -> str:
    if not OPENAI_API_KEY:
        raise LLMError(
            "AI explanation is temporarily unavailable (no OpenAI API key configured)."
        )
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        content = response.choices[0].message.content
        if not content:
            raise LLMError("AI explanation is temporarily unavailable (empty response from OpenAI).")
        return content
    except LLMError:
        raise
    except Exception as e:
        msg = str(e).lower()
        if "api key" in msg or "auth" in msg or "401" in msg:
            raise LLMError(
                "AI explanation is temporarily unavailable (invalid or missing OpenAI API key).",
                cause=e,
            )
        if "timeout" in msg:
            raise LLMError(
                "AI explanation is temporarily unavailable (the request timed out).", cause=e
            )
        raise LLMError(
            "AI explanation is temporarily unavailable due to an unexpected error.", cause=e
        )


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Routes to the configured provider. Raises LLMError on any
    failure -- never raises a raw SDK exception to the caller."""
    if LLM_PROVIDER == "gemini":
        return _call_gemini(system_prompt, user_prompt)
    elif LLM_PROVIDER == "openai":
        return _call_openai(system_prompt, user_prompt)
    else:
        raise LLMError(f"Unknown LLM_PROVIDER '{LLM_PROVIDER}' in configuration.")
