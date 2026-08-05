#!/usr/bin/env bash
# ==============================================================================
# GCP Environment Setup Script for AI Sight-Reading Platform
# Provisions required GCP APIs, Artifact Registry, Service Account, and IAM roles.
# ==============================================================================
set -euo pipefail

GCP_PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
GCP_REGION="${GCP_REGION:-us-central1}"
SA_NAME="ai-sight-reader-backend-sa"
SA_EMAIL="${SA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
REPO_NAME="ai-sight-reader-repo"

if [ -z "${GCP_PROJECT_ID}" ]; then
  echo "❌ Error: GCP_PROJECT_ID is not set. Please export GCP_PROJECT_ID='your-project-id'"
  exit 1
fi

echo "============================================================"
echo "🚀 Setting up GCP Project: ${GCP_PROJECT_ID} in region ${GCP_REGION}"
echo "============================================================"

# 1. Enable required Google Cloud APIs
echo "1️⃣  Enabling required Google Cloud APIs..."
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  --project="${GCP_PROJECT_ID}"

# 2. Create Artifact Registry Docker Repository
echo "2️⃣  Configuring Artifact Registry Docker repository (${REPO_NAME})..."
if ! gcloud artifacts repositories describe "${REPO_NAME}" --location="${GCP_REGION}" --project="${GCP_PROJECT_ID}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${REPO_NAME}" \
    --repository-format=docker \
    --location="${GCP_REGION}" \
    --description="Docker container repository for AI Sight-Reading Tool" \
    --project="${GCP_PROJECT_ID}"
  echo "✅ Created Artifact Registry repository: ${REPO_NAME}"
else
  echo "ℹ️  Artifact Registry repository ${REPO_NAME} already exists. Skipping."
fi

# 3. Create Backend Service Account for Cloud Run
echo "3️⃣  Checking Service Account (${SA_NAME})..."
if ! gcloud iam service-accounts describe "${SA_EMAIL}" --project="${GCP_PROJECT_ID}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="AI Sight Reader Backend Service Account (Vertex AI Gemini Auth)" \
    --description="Used by Cloud Run Backend to call Gemini on Vertex AI without API keys." \
    --project="${GCP_PROJECT_ID}"
  echo "✅ Created Service Account: ${SA_EMAIL}"
else
  echo "ℹ️  Service Account ${SA_EMAIL} already exists. Skipping."
fi

# 4. Grant Vertex AI User IAM Role to Service Account
echo "4️⃣  Granting roles/aiplatform.user to ${SA_EMAIL}..."
gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user" \
  --condition=None \
  --quiet

echo "============================================================"
echo "🎉 GCP Infrastructure & Service Account Setup Complete!"
echo "Service Account Email: ${SA_EMAIL}"
echo "Next step: Run './scripts/deploy_cloudrun.sh' to deploy services."
echo "============================================================"
