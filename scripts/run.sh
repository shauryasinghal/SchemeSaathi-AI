#!/usr/bin/env bash
# Runs the app in DEV mode: FastAPI backend (with reload) + Vite dev
# server, in parallel, with hot reload on both sides. For a single
# production-style process instead, see the "Production" section in
# the README (build the frontend once, then just run uvicorn).
set -euo pipefail

# shellcheck disable=SC1091
if [ -d venv ]; then
    source venv/bin/activate
fi

if [ ! -f storage/index.faiss ]; then
    echo "No index found -- building it first..."
    python src/ingest.py
fi

echo "Starting FastAPI backend on :8000 and Vite dev server on :5173 ..."
echo "Open http://localhost:5173 in your browser."
echo "Press Ctrl+C to stop both."

trap 'kill 0' EXIT
uvicorn api.main:app --reload --port 8000 &
(cd frontend && npm run dev) &
wait
