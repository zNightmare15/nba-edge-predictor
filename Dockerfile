# ==============================================================================
# Multi-Stage Dockerfile for Zero-Cost Production Deployment (Render / Fly.io / Railway)
# Stage 1: Build modern React frontend
# Stage 2: Minimalist Python runtime serving both API and static UI
# ==============================================================================

# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci --silent

COPY frontend/ ./
RUN npm run build

# Stage 2: Python production server
FROM python:3.12-slim AS runner

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8050 \
    ENVIRONMENT=production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and config
COPY config/ ./config/
COPY src/ ./src/
COPY main.py .
COPY Logica_y_Aprendizaje_del_Modelo_NBA.pdf .

# Copy compiled frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ensure cache and data directories exist with non-root permissions
RUN mkdir -p data/cache data/models \
    && useradd -u 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8050

# Run FastAPI with uvicorn bound to dynamic cloud host and port
CMD ["sh", "-c", "uvicorn src.dashboard.app:app --host 0.0.0.0 --port ${PORT}"]

