# ==============================================================================
# Cloud Run Optimized Dockerfile for Python FastAPI Backend (Powered by UV)
# Uses slim base image, UV package installer, non-root user, and Uvicorn server.
# ==============================================================================
FROM python:3.11-slim as builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install UV for lightning-fast Python package resolution and installation
RUN pip install --no-cache-dir uv

COPY requirements.txt .
# Use UV to install dependencies directly into system site-packages
RUN uv pip install --system --no-cache -r requirements.txt

# Final production image
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Create non-root user for Cloud Run security best practices
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=appuser:appuser app/ /app/app/

USER appuser

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
