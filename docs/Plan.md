# Engineering & Execution Plan: AI-Driven Sight-Reading Tool (GCP Cloud Run & Vertex AI)

This document provides the step-by-step implementation plan, verification milestones, and testing criteria for building, running locally, and deploying the AI-Driven Sight-Reading Tool to Google Cloud Platform (GCP).

---

## 1. Project Architecture Checklist

- [x] **Architecture Design**: Decoupled Next.js Frontend + FastAPI Backend deployed on Google Cloud Run.
- [x] **Auth & AI Integration**: Vertex AI Gemini (`gemini-2.5-flash` / `gemini-2.5-pro`) using `google-genai` SDK with Google Cloud Service Account (ADC - zero API keys required).
- [x] **Infrastructure as Code**: Full Terraform suite in `infra/` for reproducible provisioning.
- [x] **Automation Scripts**: Shell scripts in `scripts/` for setup, deployment, and local dev.
- [x] **Frontend Engineering**: Next.js 15 + TypeScript + Tailwind CSS + `abcjs` (SVG rendering and Web Audio synthesis).

---

## 2. Milestone Execution Plan

### Milestone 1: Foundations & Infrastructure Bootstrapping
1.  **GCP Setup Script (`scripts/setup_gcp.sh`)**:
    *   Enables required GCP APIs (`aiplatform.googleapis.com`, `run.googleapis.com`, `artifactregistry.googleapis.com`, `cloudbuild.googleapis.com`).
    *   Creates dedicated Cloud Run Service Account: `ai-sight-reader-backend-sa`.
    *   Grants `roles/aiplatform.user` for Vertex AI model access.
2.  **Terraform Configuration (`infra/`)**:
    *   Defines IAM Service Accounts, Artifact Registry repositories, and Cloud Run services (`backend` and `frontend`).
    *   Configures secure service-to-service CORS and environment variables.

### Milestone 2: Python FastAPI Backend Service (`backend/`)
1.  **Configuration & Schemas**:
    *   Pydantic BaseSettings loading GCP project ID, region, and Gemini model name.
    *   Strongly typed request payload (`ExerciseRequest`: difficulty, key signature, instrument, time signature, tempo).
2.  **Gemini Service Account Authentication (`services/gemini_service.py`)**:
    *   Uses official Google GenAI SDK (`google-genai` with `vertexai=True`).
    *   System prompt engineering to force raw ABC Notation output starting with `X:`.
3.  **ABC Validation Layer (`utils/abc_validator.py`)**:
    *   Validates ABC structural headers (`X:`, `T:`, `K:`, `M:`, `L:`) and cleans stray markdown backticks.
4.  **FastAPI Routing & Containerization**:
    *   `/api/generate-exercise` POST endpoint and `/health` healthcheck.
    *   Optimized multi-stage Python 3.11 Dockerfile for Cloud Run.

### Milestone 3: Next.js Frontend Studio (`frontend/`)
1.  **Design System & UI Components**:
    *   Sleek dark-mode glassmorphism interface with Tailwind CSS.
    *   Interactive parameter control dashboard (`<ControlDashboard />`).
2.  **abcjs Notation & Audio Integration**:
    *   Responsive SVG sheet music rendering (`<SheetMusicDisplay />`) via `abcjs.renderAbc`.
    *   Web Audio API playback controls (`<AudioPlayer />`) using `abcjs.synth.CreateSynth()`.
3.  **Standalone Containerization**:
    *   Next.js standalone build Dockerfile for Cloud Run.

### Milestone 4: End-to-End Testing & Automated Deployment
1.  **Local Simulation**:
    *   `docker-compose.yml` to run frontend and backend locally.
    *   `scripts/dev_local.sh` for fast iterative local development.
2.  **Cloud Run Deployment Script (`scripts/deploy_cloudrun.sh`)**:
    *   Builds containers using Google Cloud Build and pushes to Artifact Registry.
    *   Deploys Backend Service with Service Account attachment.
    *   Deploys Frontend Service with environment variable `NEXT_PUBLIC_BACKEND_URL`.

---

## 3. Verification & Testing Criteria

### 3.1 Backend Verification
*   **Healthcheck**: `curl http://localhost:8080/health` -> `{"status":"ok"}`
*   **Exercise Generation Test**:
    ```bash
    curl -X POST http://localhost:8080/api/generate-exercise \
      -H "Content-Type: application/json" \
      -d '{"difficulty":"intermediate", "key_signature":"G", "instrument":"piano", "time_signature":"4/4"}'
    ```
    *Must return JSON payload with structurally valid `abc_notation` starting with `X:1`.*

### 3.2 Frontend Verification
*   Verify UI renders smoothly without console errors.
*   Verify clicking **"Generate Exercise"** invokes `/api/generate-exercise` and displays vector SVG notation.
*   Verify clicking **"Play"** initializes Web Audio synth after user click and synthesizes notes cleanly.

### 3.3 GCP Cloud Run Production Verification
*   Verify Cloud Run Backend authenticates with Vertex AI without API keys via the attached Service Account.
*   Verify CORS headers allow cross-origin requests from the Cloud Run Frontend URL.
