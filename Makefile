# ==============================================================================
# AI-Driven Sight-Reading Platform — Essential Developer Makefile
# Simplifies local development, testing, and Google Cloud Run deployment.
# Uses 'uv' for Python package management and 'pnpm' for Node.js frontend.
# ==============================================================================

.PHONY: help run-local run dev test test-local test-unit test-api lint setup-gcp deploy-gcp deploy install-backend run-backend install-frontend run-frontend build-frontend clean

# Default variables
GCP_PROJECT_ID ?= $(shell gcloud config get-value project 2>/dev/null || echo "your-gcp-project-id")
GCP_REGION     ?= us-central1
UV             ?= uv
PNPM           ?= pnpm
PYTHON         ?= python3
VENV_DIR       := backend/.venv

# Default target: show help
help:
	@echo "========================================================================="
	@echo "🎵 AI Sight-Reading Tool — Developer Makefile (UV & PNPM Enabled)"
	@echo "========================================================================="
	@echo "Local Full-Stack Application (Backend + Frontend Simultaneously):"
	@echo "  make run-local        - ⭐ Run the WHOLE app locally (FastAPI :8080 + Next.js :3000)"
	@echo "  make run / make dev   - Aliases for 'make run-local'"
	@echo ""
	@echo "Essential Testing & Linting:"
	@echo "  make test             - Run Python backend unit test suite via UV"
	@echo "  make test-local       - Run full local test suite (unit + lint + API check)"
	@echo "  make test-unit        - Run only ABC Validator & Healthcheck unit tests"
	@echo "  make test-api         - Run API & Health integration tests"
	@echo "  make lint             - Syntax and compilation check for backend & frontend"
	@echo ""
	@echo "Google Cloud Platform (Cloud Run, Vertex AI & Agent Registry):"
	@echo "  make setup-gcp                - Enable GCP APIs, create Gemini SA, and bind IAM roles"
	@echo "  make deploy-gcp               - Build containers via Cloud Build & deploy to Cloud Run"
	@echo "  make deploy-adk-agent-runtime - Deploy ADK agent to Vertex AI Agent Runtime (Reasoning Engine)"
	@echo "  make deploy-adk-cloud-run     - Deploy ADK agent as serverless container on Cloud Run (A2A)"
	@echo "  make deploy-agent-registry    - Publish agent to Google Agent Registry / Gemini Enterprise"
	@echo "  make list-agent-registry      - List agents registered in Google Cloud Agent Registry"
	@echo ""
	@echo "Individual Component Development:"
	@echo "  make install-backend  - Create Python venv and install dependencies using UV"
	@echo "  make run-backend      - Start ONLY FastAPI backend server (http://localhost:8080)"
	@echo "  make install-frontend - Install Next.js frontend dependencies via 'pnpm'"
	@echo "  make run-frontend     - Start ONLY Next.js frontend dev server (http://localhost:3000)"
	@echo "  make build-frontend   - Build production Next.js standalone bundle via 'pnpm'"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Clean up cache files, build artifacts, and venv"
	@echo "========================================================================="

# ------------------------------------------------------------------------------
# Local Full-Stack Application
# ------------------------------------------------------------------------------
run-local:
	@echo "🚀 Launching Full-Stack Application Locally (UV Backend + PNPM Frontend)..."
	@chmod +x scripts/run_local.sh
	@./scripts/run_local.sh

run: run-local
dev: run-local

# ------------------------------------------------------------------------------
# Testing & Linting
# ------------------------------------------------------------------------------
test: test-unit

test-local:
	@echo "🧪 Running complete local testing battery (unit, lint, API)..."
	@chmod +x scripts/test_local.sh
	@./scripts/test_local.sh --all

test-unit:
	@echo "🧪 Running backend unit test suite via UV..."
	@chmod +x scripts/test_local.sh
	@./scripts/test_local.sh --unit

test-api:
	@echo "🧪 Running API & integration test suite..."
	@chmod +x scripts/test_local.sh
	@./scripts/test_local.sh --api

lint:
	@echo "🔍 Running syntax and lint checks..."
	@chmod +x scripts/test_local.sh
	@./scripts/test_local.sh --lint

# ------------------------------------------------------------------------------
# Google Cloud Platform (Cloud Run & Vertex AI Gemini SA)
# ------------------------------------------------------------------------------
setup-gcp:
	@echo "☁️  Setting up GCP Project: $(GCP_PROJECT_ID) ($(GCP_REGION))..."
	@chmod +x scripts/setup_gcp.sh
	@GCP_PROJECT_ID=$(GCP_PROJECT_ID) GCP_REGION=$(GCP_REGION) ./scripts/setup_gcp.sh

deploy-gcp: deploy
deploy:
	@echo "🚀 Deploying Backend and Frontend to Google Cloud Run via Cloud Build..."
	@chmod +x scripts/deploy_cloudrun.sh
	@GCP_PROJECT_ID=$(GCP_PROJECT_ID) GCP_REGION=$(GCP_REGION) ./scripts/deploy_cloudrun.sh

deploy-adk-agent-runtime:
	@echo "🚀 Deploying Google ADK Agent to Vertex AI Agent Runtime (Managed Reasoning Engine)..."
	@cd backend && agents-cli deploy \
	  --project="$(GCP_PROJECT_ID)" \
	  --region="$(GCP_REGION)" \
	  --deployment-target=agent_runtime \
	  --service-name="sight-reading-composer"

deploy-adk-cloud-run:
	@echo "🚀 Deploying Google ADK Agent as a Serverless Container on Cloud Run (A2A Protocol)..."
	@cd backend && agents-cli deploy \
	  --project="$(GCP_PROJECT_ID)" \
	  --region="$(GCP_REGION)" \
	  --deployment-target=cloud_run \
	  --service-name="sight-reading-composer"

deploy-agent-registry:
	@echo "🚀 Registering and publishing agent to Google Agent Registry / Gemini Enterprise..."
	@if [ -z "$(GEMINI_ENTERPRISE_APP_ID)" ]; then \
		echo "⚠️  GEMINI_ENTERPRISE_APP_ID is not set. Listing available apps in project $(GCP_PROJECT_ID)..."; \
		agents-cli publish gemini-enterprise --list --project-id=$(GCP_PROJECT_ID) || true; \
		echo "Usage: GEMINI_ENTERPRISE_APP_ID=projects/... make deploy-agent-registry"; \
	else \
		agents-cli publish gemini-enterprise \
		  --gemini-enterprise-app-id="$(GEMINI_ENTERPRISE_APP_ID)" \
		  --display-name="Sight-Reading Composer" \
		  --description="Dynamic AI Sight-Reading Composer Agent" \
		  --project-id="$(GCP_PROJECT_ID)"; \
	fi

list-agent-registry:
	@echo "🔍 Listing agents registered in Google Cloud Agent Registry..."
	@gcloud alpha agent-registry agents list --project=$(GCP_PROJECT_ID) --location=$(GCP_REGION) || true

# ------------------------------------------------------------------------------
# Backend Development (Python FastAPI via UV)
# ------------------------------------------------------------------------------
install-backend:
	@echo "⚡ Installing Python backend dependencies using UV..."
	@cd backend && $(UV) venv .venv
	@cd backend && $(UV) pip install -r requirements.txt
	@echo "✅ Backend dependencies installed in $(VENV_DIR) via UV."

run-backend:
	@echo "🎵 Starting FastAPI Backend server on http://localhost:8080..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "ℹ️  Virtual environment not found. Creating and installing via UV..."; \
		$(MAKE) install-backend; \
	fi
	@cd backend && $(UV) run uvicorn app.main:app --reload --port 8080 --host 0.0.0.0

# ------------------------------------------------------------------------------
# Frontend Development (Next.js TypeScript via PNPM)
# ------------------------------------------------------------------------------
install-frontend:
	@echo "⚡ Installing Next.js frontend dependencies using PNPM..."
	@cd frontend && $(PNPM) install

run-frontend:
	@echo "🎵 Starting Next.js Frontend server on http://localhost:3000..."
	@cd frontend && $(PNPM) dev

build-frontend:
	@echo "🏗️  Building standalone Next.js production bundle with PNPM..."
	@cd frontend && $(PNPM) build

# ------------------------------------------------------------------------------
# Maintenance
# ------------------------------------------------------------------------------
clean:
	@echo "🧹 Cleaning up build artifacts, caches, and temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend/.venv 2>/dev/null || true
	@rm -rf frontend/.next frontend/out 2>/dev/null || true
	@echo "✅ Cleanup complete."
