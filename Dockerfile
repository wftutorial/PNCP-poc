# =============================================================================
# Root Dockerfile — proxy for services with Root Directory = /
# =============================================================================
# Railway worker service (bidiq-worker) looks for Dockerfile at repo root.
# This file builds the backend from the /backend subdirectory.
#
# Both bidiq-backend and bidiq-worker use the same image.
# PROCESS_TYPE env var (web/worker) controls behavior via start.sh.

FROM python:3.11-slim

LABEL build.timestamp="2026-02-25T14:00:00"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
