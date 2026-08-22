"""
Central configuration. Reads environment variables (via .env) so no
secrets or environment-specific paths are hardcoded anywhere else.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"

SCHEMES_PATH = DATA_DIR / "schemes.json"
INDEX_PATH = STORAGE_DIR / "index.faiss"
METADATA_PATH = STORAGE_DIR / "metadata.json"

# --- LLM provider -----------------------------------------------------
# Default provider is Gemini (per project requirements). Set LLM_PROVIDER
# to "gemini" or "openai" -- llm.py branches on this value, so adding a
# third provider later means adding one branch there, not rewriting the
# rest of the pipeline.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- Embeddings ---------------------------------------------------------
# Multilingual model so a Hindi/Hinglish query still retrieves the right
# scheme even before the translation layer runs on the output side.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")

# --- Retrieval ------------------------------------------------------------
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "6"))

# --- Languages ------------------------------------------------------------
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
}
# Documented-but-not-yet-wired languages -- see docs/architecture.md
# "Scalability" section and README roadmap.
PLANNED_LANGUAGES = ["Bengali", "Tamil", "Telugu", "Marathi", "Gujarati", "Kannada"]
