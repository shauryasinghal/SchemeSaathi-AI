# --- Stage 1: build the React frontend ---
    FROM node:20-slim AS frontend-build
    WORKDIR /frontend
    COPY frontend/package.json ./
    RUN npm install
    COPY frontend/ ./
    RUN npm run build
    
    # --- Stage 2: Python runtime, serves API + built frontend ---
    FROM python:3.11-slim
    WORKDIR /app
    
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        && rm -rf /var/lib/apt/lists/*
    
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    COPY . .
    COPY --from=frontend-build /frontend/dist ./frontend/dist
    
    # Build the vector index at image-build time so the container starts
    # ready to serve.
    RUN python src/ingest.py
    
    EXPOSE 7860
    
    HEALTHCHECK CMD curl --fail http://localhost:7860/api/health || exit 1
    
    ENTRYPOINT ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]