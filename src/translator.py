"""
Translation layer. Uses deep-translator's Google backend, which needs no
API key or billing setup -- important when you only have ~48 hours and
don't want to burn time on Google Cloud project setup.

Only English and Hindi are wired up as first-class answer languages for
Phase 1 (see config.SUPPORTED_LANGUAGES). The remaining languages in
config.PLANNED_LANGUAGES are documented as roadmap items rather than
half-implemented -- see docs/architecture.md's scalability section and
the README roadmap for the Bhashini upgrade path.
"""

from src.config import SUPPORTED_LANGUAGES

MAX_CHUNK_CHARS = 4500  # stay under the ~5000 char limit of the free backend


class TranslationError(Exception):
    def __init__(self, user_message: str, cause: Exception = None):
        super().__init__(user_message)
        self.user_message = user_message
        self.cause = cause


def translate_text(text: str, target_lang_name: str = "Hindi") -> str:
    """Translate text to the given language name (must be a key in
    SUPPORTED_LANGUAGES). Returns the original text unchanged for
    English. Raises TranslationError (never a raw exception) on
    failure -- callers should fall back to showing the English text
    rather than crashing the whole answer."""
    if target_lang_name == "English":
        return text
    if target_lang_name not in SUPPORTED_LANGUAGES:
        raise TranslationError(f"'{target_lang_name}' is not a supported answer language yet.")

    try:
        from deep_translator import GoogleTranslator

        target_code = SUPPORTED_LANGUAGES[target_lang_name]
        translator = GoogleTranslator(source="en", target=target_code)

        if len(text) <= MAX_CHUNK_CHARS:
            return translator.translate(text)

        chunks, current = [], ""
        for paragraph in text.split("\n\n"):
            if len(current) + len(paragraph) + 2 > MAX_CHUNK_CHARS:
                chunks.append(current)
                current = paragraph
            else:
                current = f"{current}\n\n{paragraph}" if current else paragraph
        if current:
            chunks.append(current)

        return "\n\n".join(translator.translate(c) for c in chunks)
    except TranslationError:
        raise
    except Exception as e:
        raise TranslationError("Translation is temporarily unavailable.", cause=e)


if __name__ == "__main__":
    sample = "You may be eligible for PM-KISAN, which provides direct income support to farmers."
    print(translate_text(sample, "Hindi"))
