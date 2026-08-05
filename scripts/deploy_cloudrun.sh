#!/usr/bin/env bash
# ==============================================================================
# Cloud Run Deployment Script for AI Sight-Reading Platform
# Builds container images using Cloud Build and deploys Backend & Frontend services.
# ==============================================================================
set -euo pipefail

GCP_PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
GCP_REGION="${GCP_REGION:-us-central1}"
SA_NAME="ai-sight-reader-backend-sa"
SA_EMAIL="${SA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
REPO_NAME="ai-sight-reader-repo"
BACKEND_SERVICE="ai-sight-reader-backend"
FRONTEND_SERVICE="ai-sight-reader-frontend"
GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"

if [ -z "${GCP_PROJECT_ID}" ]; then
  echo "❌ Error: GCP_PROJECT_ID is not set. Please export GCP_PROJECT_ID='your-project-id'"
  exit 1
fi

IMAGE_PREFIX="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO_NAME}"

echo "============================================================"
echo "🚀 Deploying AI Sight-Reading Tool to Google Cloud Run"
echo "Project: ${GCP_PROJECT_ID} | Region: ${GCP_REGION}"
echo "============================================================"

# 1. Build and deploy Python FastAPI Backend
echo "1️⃣  Building Backend container image via Google Cloud Build..."
gcloud builds submit backend \
  --tag="${IMAGE_PREFIX}/${BACKEND_SERVICE}:latest" \
  --project="${GCP_PROJECT_ID}"

echo "2️⃣  Deploying Backend to Google Cloud Run (using Service Account: ${SA_EMAIL})..."
gcloud run deploy "${BACKEND_SERVICE}" \
  --image="${IMAGE_PREFIX}/${BACKEND_SERVICE}:latest" \
  --region="${GCP_REGION}" \
  --platform="managed" \
  --service-account="${SA_EMAIL}" \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=${GCP_PROJECT_ID},GCP_LOCATION=${GCP_REGION},GEMINI_MODEL=${GEMINI_MODEL},ENVIRONMENT=production" \
  --project="${GCP_PROJECT_ID}"

BACKEND_URL=$(gcloud run services describe "${BACKEND_SERVICE}" --region="${GCP_REGION}" --project="${GCP_PROJECT_ID}" --format="value(status.url)")
echo "✅ Backend deployed at: ${BACKEND_URL}"

# 2. Build and deploy Next.js Frontend
echo "3️⃣  Building Frontend container image via Google Cloud Build..."
gcloud builds submit frontend \
  --tag="${IMAGE_PREFIX}/${FRONTEND_SERVICE}:latest" \
  --project="${GCP_PROJECT_ID}"

echo "4️⃣  Deploying Frontend to Google Cloud Run..."
gcloud run deploy "${FRONTEND_SERVICE}" \
  --image="${IMAGE_PREFIX}/${FRONTEND_SERVICE}:latest" \
  --region="${GCP_REGION}" \
  --platform="managed" \
  --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_BACKEND_URL=${BACKEND_URL}" \
  --project="${GCP_PROJECT_ID}"

FRONTEND_URL=$(gcloud run services describe "${FRONTEND_SERVICE}" --region="${GCP_REGION}" --project="${GCP_PROJECT_ID}" --format="value(status.url)")

echo "============================================================"
echo "🎉 Deployment Successfully Completed!"
echo "🎵 Web UI (Frontend):  ${FRONTEND_URL}"
echo "⚡ Backend API Docs:   ${BACKEND_URL}/docs"
echo "============================================================"
