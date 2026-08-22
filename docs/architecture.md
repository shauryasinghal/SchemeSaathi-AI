# Architecture

## Frontend/backend split

The product is a React single-page app (`frontend/`) talking to a FastAPI
JSON API (`api/`), which wraps the same `src/` pipeline described below --
switching the UI layer from Streamlit to React did not touch retrieval,
eligibility, or generation logic at all, only how it's exposed.

In production, **one process serves both**: `api/main.py` mounts the built
React app (`frontend/dist`) as static files alongside the `/api/*` routes,
so there's a single service to deploy, not two. In development, Vite's
dev server proxies `/api` requests to the FastAPI server so both sides
hot-reload independently (see `frontend/vite.config.js`).

## Why RAG, not a fine-tuned model or a plain chatbot

We need the system to answer questions about ~45 (expandable to hundreds of)
specific, factual government schemes, and to **never invent one**. Fine-tuning
a model on scheme data would be slow to update (a new Union Budget changes
scheme terms) and doesn't give a clean way to enforce "only use what's true
right now". A plain prompt-stuffed chatbot without retrieval would run into
context limits past a few dozen schemes and has no way to *ground* an answer
in a specific, citable source.

Retrieval-Augmented Generation solves both: the scheme database is the
source of truth, retrieval narrows it to what's relevant to *this* person,
and the LLM's only job is to explain the retrieved facts in plain language
-- not to know facts on its own.

## Why FAISS

FAISS is a local, in-process vector index -- no server to run, no network
dependency once embeddings are computed, and it's fast enough for a
hundreds-of-schemes dataset without any tuning. `IndexFlatIP` (exact search)
is intentionally simple: at this dataset size, approximate-nearest-neighbour
indexes (IVF, HNSW) would add complexity without a measurable speed benefit.
This is also why the index is scalable: brute-force flat search stays fast
into the low thousands of records, which comfortably covers "more states,
more schemes" as a roadmap item without an architecture change.

## Why local embeddings (sentence-transformers)

Embeddings are computed once at ingest time and reused for every query, so
using a local, free, multilingual model (`paraphrase-multilingual-MiniLM-L12-v2`)
avoids per-query API cost and lets retrieval keep working even if the LLM
API is down (see "Limited connectivity" below). It's also multilingual out
of the box, so a Hindi or Hinglish query embeds close to the right scheme
without needing a separate translation step *before* retrieval.

## Eligibility reasoning: rule-based, not LLM-based

`src/eligibility.py` is a transparent, explainable heuristic layer that sits
between retrieval and generation. It looks at the user's extracted profile
against each retrieved scheme's stated criteria (occupation/category,
state, age range if parseable, income signal, disability requirement, land
ownership) and classifies each as matched, missing, or unmatched -- then
derives an honest match level (High / Medium / Needs More Information /
Low -- never "100% eligible").

This is deliberately NOT delegated to the LLM. An LLM asked to "decide
eligibility" can sound confident while being wrong; a rule-based layer is
auditable, testable (see `tests/test_eligibility.py`), and gives the LLM
pre-computed, structured facts to explain rather than judgments to invent.

## Hallucination reduction / source grounding

Three layers work together:
1. The eligibility engine only ever reasons over criteria that are
   literally present in the scheme record.
2. The LLM prompt (`src/prompt_engine.py`) explicitly forbids inventing
   scheme names, benefits, or eligibility criteria, and requires honest
   "may be eligible" language, never a certainty claim.
3. The UI always shows the official source link for every recommended
   scheme, so a citizen (or a judge) can verify independently -- the AI
   explanation is never the only source of truth on screen.

## Multilingual architecture

English and Hindi are fully wired for Phase 1 (`src/translator.py`, backed
by `deep-translator`, which needs no API key or billing setup -- important
under a hackathon deadline). The architecture is intentionally
language-agnostic beyond that: `config.SUPPORTED_LANGUAGES` is the single
place a new language gets added, and `config.PLANNED_LANGUAGES` documents
Bengali, Tamil, Telugu, Marathi, Gujarati, and Kannada as the next batch,
most naturally added via the Bhashini API (purpose-built for Indian
languages, and covers speech input/output too -- see the README roadmap).

## Limited connectivity

The scheme database and vector retrieval run **entirely locally** once the
index is built -- no network call is made for retrieval itself. The LLM
explanation step is the one part that needs external connectivity. If it's
unavailable (no API key, invalid key, timeout, or genuinely offline),
`src/recommender.py` falls back to a clearly-labelled, non-AI response
built directly from the local database matches -- it never pretends this
fallback is AI-generated. This is an honest description of what "works
offline": the database and search do, the LLM explanation doesn't (yet).

## Scalability

- **More schemes**: the dataset is a flat JSON file; re-running
  `python src/ingest.py` re-embeds and re-indexes in one step. Flat FAISS
  search comfortably scales into the low thousands of records.
- **More languages**: add a language to `config.SUPPORTED_LANGUAGES`
  (and, longer-term, swap the translation backend for Bhashini).
- **Voice input/output**: Bhashini also exposes speech-to-text and
  text-to-speech, which would let a low-literacy user speak their
  situation instead of typing it -- a natural next integration point,
  documented rather than half-built for Phase 1.
- **WhatsApp / SMS front-end**: `src/recommender.py` is UI-agnostic --
  `app.py` is one consumer of it; a WhatsApp bot could call
  `get_recommendations()` directly without touching the pipeline.
