"""
FastAPI application entrypoint.

Serves two things from one process, deliberately -- a single deployable
service is far more reliable to actually get live before a hackathon
deadline than coordinating two separate hosted services:

  1. The JSON API, under /api/*  (see routes.py)
  2. The built React frontend (frontend/dist), for every other path

In local development, run the frontend separately with
`npm run dev` (Vite's dev server, with hot reload) and this API with
`uvicorn api.main:app --reload` -- Vite is configured to proxy /api
requests to this server (see frontend/vite.config.js). For production,
run `npm run build` once, then this single process serves everything.

If frontend/dist doesn't exist yet (e.g. you haven't run `npm run
build`), the static mount is skipped so the API still comes up cleanly
-- convenient for API-only development and for the automated tests.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router

app = FastAPI(title="SchemeSaathi AI API", version="1.0.0")

# Permissive CORS is fine here: this is a read-mostly public information
# tool with no auth/session state, and the dev server (Vite on a
# different port) needs it. Tighten to specific origins if you add
# authenticated features later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIST), html=True), name="frontend")
