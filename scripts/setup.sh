#!/usr/bin/env bash
# One-command environment setup. Run from the project root:
#   bash scripts/setup.sh
set -euo pipefail

echo "Setting up Python backend..."
python3 -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
    echo "Creating .env from .env.example -- fill in your API key before running."
    cp .env.example .env
fi

echo "Building the vector index..."
python src/ingest.py

echo ""
echo "Setting up React frontend..."
cd frontend
npm install
cd ..

echo ""
echo "Setup complete. Next steps:"
echo "  1. Edit .env and add your GEMINI_API_KEY (or set LLM_PROVIDER=openai and OPENAI_API_KEY)"
echo "  2. Run: bash scripts/run.sh"
