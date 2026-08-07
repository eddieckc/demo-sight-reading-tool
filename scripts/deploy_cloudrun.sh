#!/usr/bin/env bash
# ==============================================================================
# Cloud Run Deployment Script for AI Sight-Reading Platform
# Builds container images using Cloud Build and deploys Backend & Frontend services.
# ==============================================================================
set -euo pipefail

GCP_PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
GCP_REGION="${GCP_REGION:-us-central1}"
BACKEND_SA_NAME="ai-sight-reader-backend-sa"
BACKEND_SA_EMAIL="${BACKEND_SA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
FRONTEND_SA_NAME="ai-sight-reader-frontend-sa"
FRONTEND_SA_EMAIL="${FRONTEND_SA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

REPO_NAME="ai-sight-reader-repo"
BACKEND_SERVICE="ai-sight-reader-backend"
FRONTEND_SERVICE="ai-sight-reader-frontend"
GEMINI_MODEL="${GEMINI_MODEL:-gemini-3.5-flash}"

if [ -z "${GCP_PROJECT_ID}" ]; then
  echo "❌ Error: GCP_PROJECT_ID is not set. Please export GCP_PROJECT_ID='your-project-id'"
  exit 1
fi

IMAGE_PREFIX="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO_NAME}"

echo "============================================================"
echo "🚀 Deploying AI Sight-Reading Tool to Google Cloud Run"
echo "Project: ${GCP_PROJECT_ID} | Region: ${GCP_REGION}"
echo "============================================================"

# 0. Ensure Artifact Registry repository exists
echo "0️⃣  Verifying Artifact Registry repository (${REPO_NAME})..."
if ! gcloud artifacts repositories describe "${REPO_NAME}" --location="${GCP_REGION}" --project="${GCP_PROJECT_ID}" >/dev/null 2>&1; then
  echo "📦 Creating Artifact Registry repository '${REPO_NAME}' in ${GCP_REGION}..."
  gcloud artifacts repositories create "${REPO_NAME}" \
    --repository-format=docker \
    --location="${GCP_REGION}" \
    --description="Docker repository for AI Sight-Reading Platform" \
    --project="${GCP_PROJECT_ID}"
  echo "✅ Artifact Registry repository created."
else
  echo "✅ Artifact Registry repository is ready."
fi

# Ensure Backend & Frontend Service Accounts exist
echo "🔑 Verifying IAM Service Accounts..."
if ! gcloud iam service-accounts describe "${BACKEND_SA_EMAIL}" --project="${GCP_PROJECT_ID}" >/dev/null 2>&1; then
  echo "Creating Backend Service Account '${BACKEND_SA_EMAIL}'..."
  gcloud iam service-accounts create "${BACKEND_SA_NAME}" \
    --display-name="AI Sight Reader Backend SA" \
    --project="${GCP_PROJECT_ID}"
  gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
    --member="serviceAccount:${BACKEND_SA_EMAIL}" \
    --role="roles/aiplatform.user" \
    --condition=None \
    --quiet
  echo "✅ Backend Service Account created."
fi

if ! gcloud iam service-accounts describe "${FRONTEND_SA_EMAIL}" --project="${GCP_PROJECT_ID}" >/dev/null 2>&1; then
  echo "Creating Frontend Service Account '${FRONTEND_SA_EMAIL}'..."
  gcloud iam service-accounts create "${FRONTEND_SA_NAME}" \
    --display-name="AI Sight Reader Frontend SA" \
    --project="${GCP_PROJECT_ID}"
  gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
    --member="serviceAccount:${FRONTEND_SA_EMAIL}" \
    --role="roles/run.invoker" \
    --condition=None \
    --quiet
  echo "✅ Frontend Service Account created."
fi

# 1. Build and deploy Python FastAPI Backend (Private Internal Cloud Run Service)
echo "1️⃣  Building Backend container image via Google Cloud Build..."
gcloud builds submit backend \
  --tag="${IMAGE_PREFIX}/${BACKEND_SERVICE}:latest" \
  --project="${GCP_PROJECT_ID}"

echo "2️⃣  Deploying Backend to Google Cloud Run (Secure Internal Service Account: ${BACKEND_SA_EMAIL})..."
gcloud run deploy "${BACKEND_SERVICE}" \
  --image="${IMAGE_PREFIX}/${BACKEND_SERVICE}:latest" \
  --region="${GCP_REGION}" \
  --platform="managed" \
  --service-account="${BACKEND_SA_EMAIL}" \
  --no-allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=${GCP_PROJECT_ID},GCP_LOCATION=${GCP_REGION},GEMINI_MODEL=${GEMINI_MODEL},ENVIRONMENT=production" \
  --project="${GCP_PROJECT_ID}"

# Authorize Frontend Service Account to invoke Backend
gcloud run services add-iam-policy-binding "${BACKEND_SERVICE}" \
  --member="serviceAccount:${FRONTEND_SA_EMAIL}" \
  --role="roles/run.invoker" \
  --region="${GCP_REGION}" \
  --project="${GCP_PROJECT_ID}" \
  --quiet

BACKEND_URL=$(gcloud run services describe "${BACKEND_SERVICE}" --region="${GCP_REGION}" --project="${GCP_PROJECT_ID}" --format="value(status.url)")
echo "✅ Private Backend service deployed at: ${BACKEND_URL}"

# 2. Build and deploy Next.js Frontend (Server-Side Internal Proxy)
echo "3️⃣  Building Frontend container image via Google Cloud Build..."
gcloud builds submit frontend \
  --tag="${IMAGE_PREFIX}/${FRONTEND_SERVICE}:latest" \
  --project="${GCP_PROJECT_ID}"

echo "4️⃣  Deploying Frontend to Google Cloud Run (Public Web UI with internal backend proxy)..."
gcloud run deploy "${FRONTEND_SERVICE}" \
  --image="${IMAGE_PREFIX}/${FRONTEND_SERVICE}:latest" \
  --region="${GCP_REGION}" \
  --platform="managed" \
  --service-account="${FRONTEND_SA_EMAIL}" \
  --allow-unauthenticated \
  --set-env-vars="BACKEND_URL=${BACKEND_URL}" \
  --project="${GCP_PROJECT_ID}"

FRONTEND_URL=$(gcloud run services describe "${FRONTEND_SERVICE}" --region="${GCP_REGION}" --project="${GCP_PROJECT_ID}" --format="value(status.url)")

echo "============================================================"
echo "🎉 Deployment Successfully Completed!"
echo "🎵 Web UI (Frontend):  ${FRONTEND_URL}"
echo "⚡ Backend API Docs:   ${BACKEND_URL}/docs"
echo "============================================================"
