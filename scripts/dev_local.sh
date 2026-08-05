#!/usr/bin/env bash
# ==============================================================================
# Local Development & Deployment Helper Script
# Uses UV for all Python operations and PNPM for all Node.js operations.
# ==============================================================================
set -euo pipefail

UV_CMD="uv"
PNPM_CMD="pnpm"

echo "============================================================"
echo "🎵 AI Sight-Reading Tool: Development & Deployment Guide"
echo "============================================================"

# Handle option for Cloud Run deployment
if [ "${1:-}" = "--deploy" ] || [ "${1:-}" = "--cloudrun" ]; then
  echo "☁️  Deploying directly to Google Cloud Run via Google Cloud Build (No local Docker needed)..."
  chmod +x scripts/deploy_cloudrun.sh
  ./scripts/deploy_cloudrun.sh
  exit 0
fi

# Handle option for unit tests
if [ "${1:-}" = "--test" ]; then
  echo "🧪 Running Python Backend unit tests via UV..."
  echo "1️⃣  Running ABC Notation Syntax & Header Validator suite..."
  (cd backend && ${UV_CMD} run python -m unittest tests/test_validator.py)

  echo "2️⃣  Running FastAPI API & Healthcheck suite..."
  (cd backend && ${UV_CMD} run python -m unittest tests/test_health.py)
  echo "✅ All unit tests completed successfully via UV!"
  exit 0
fi

echo "ℹ️  Note: This project is standardized on UV for Python and PNPM for Node.js."
echo ""
echo "------------------------------------------------------------"
echo "1️⃣  OPTION 1: Direct GCP Cloud Run Deployment (No Local Docker Needed)"
echo "------------------------------------------------------------"
echo "Build and deploy containers remotely using Google Cloud Build:"
echo "  export GCP_PROJECT_ID='your-gcp-project-id'"
echo "  export GCP_REGION='us-central1'"
echo "  make setup-gcp                  # Sets up Service Account & IAM"
echo "  make deploy-gcp                 # Builds via Cloud Build & Deploys"
echo ""
echo "------------------------------------------------------------"
echo "2️⃣  OPTION 2: Manual Local Development (No Containers)"
echo "------------------------------------------------------------"
echo "Run the backend and frontend in two separate terminal windows:"
echo ""
echo "Terminal 1 (Backend - FastAPI with UV):"
echo "  cd backend"
echo "  uv venv .venv && source .venv/bin/activate"
echo "  uv pip install -r requirements.txt"
echo "  uv run uvicorn app.main:app --reload --port 8080"
echo ""
echo "Terminal 2 (Frontend - Next.js with PNPM):"
echo "  cd frontend"
echo "  pnpm install"
echo "  pnpm dev"
echo ""
echo "------------------------------------------------------------"
echo "💡 Quick Commands:"
echo "  make test        # Run backend unit tests via UV"
echo "  make deploy-gcp  # Trigger GCP Cloud Run deployment"
echo "============================================================"
