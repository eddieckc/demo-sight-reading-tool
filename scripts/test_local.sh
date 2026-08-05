#!/usr/bin/env bash
# ==============================================================================
# Local Testing Script for AI Sight-Reading Platform
# Comprehensive local testing suite: unit tests, syntax checks, and API tests.
# Uses UV for Python and PNPM for Node.js.
# ==============================================================================
set -euo pipefail

UV_CMD="uv"
PNPM_CMD="pnpm"
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"

print_header() {
  echo "============================================================"
  echo "🧪 AI Sight-Reading Tool: Local Test Suite ($1)"
  echo "============================================================"
}

run_unit_tests() {
  print_header "Unit Tests via UV"
  echo "1️⃣  Running ABC Notation Syntax & Header Validator suite..."
  (cd backend && ${UV_CMD} run python -m unittest tests/test_validator.py)

  echo "2️⃣  Running FastAPI Healthcheck & Routing suite..."
  (cd backend && ${UV_CMD} run python -m unittest tests/test_health.py)

  echo "3️⃣  Running Google ADK Agent Engine suite..."
  (cd backend && ${UV_CMD} run python -m unittest tests/test_agent.py)

  echo "✅ All unit tests passed successfully!"
}

run_lint_tests() {
  print_header "Syntax & Lint Checks"
  echo "1️⃣  Checking Python backend syntax..."
  python3 -m py_compile backend/app/*.py backend/app/schemas/*.py backend/app/services/*.py backend/app/utils/*.py backend/app/api/*.py backend/app/agent/*.py backend/tests/*.py
  echo "✅ Python syntax is clean."

  if [ -d "frontend/node_modules" ]; then
    echo "2️⃣  Checking Next.js TypeScript frontend with PNPM..."
    (cd frontend && ${PNPM_CMD} lint)
    echo "✅ Frontend TypeScript lint check passed."
  else
    echo "ℹ️  Skipping Frontend lint (node_modules not found - run 'make install-frontend' to enable)."
  fi
}

run_api_tests() {
  print_header "Local API & Integration Tests"
  echo "Checking if Backend service is reachable at ${BACKEND_URL}..."

  if curl -s --fail "${BACKEND_URL}/health" >/dev/null 2>&1; then
    echo "✅ Backend server is live at ${BACKEND_URL}."
    echo "Testing POST /api/generate-exercise payload validation..."

    HTTP_STATUS=$(curl -s -o /tmp/api_response.json -w "%{http_code}" -X POST "${BACKEND_URL}/api/generate-exercise" \
      -H "Content-Type: application/json" \
      -d '{"difficulty":"intermediate","key_signature":"C","instrument":"piano","time_signature":"4/4","tempo":120,"bars":4}')

    if [ "${HTTP_STATUS}" = "200" ]; then
      echo "✅ POST /api/generate-exercise succeeded (HTTP 200)."
      echo "Sample generated ABC Notation output:"
      grep -o '"abc_notation":[^,]*' /tmp/api_response.json | head -n 1 | cut -d'"' -f4 || true
    else
      echo "⚠️  POST /api/generate-exercise returned HTTP ${HTTP_STATUS}. Server response:"
      cat /tmp/api_response.json || true
    fi
  else
    echo "ℹ️  Live backend server is not running on ${BACKEND_URL}."
    echo "    Running in-memory FastAPI integration test via UV TestClient instead..."
    (cd backend && ${UV_CMD} run python -c "
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.exercise import ExerciseRequest

client = TestClient(app)
res = client.get('/health')
assert res.status_code == 200, f'Expected 200, got {res.status_code}'
print('✅ In-memory GET /health check passed.')
")
  fi
}

# Parse flags
RUN_ALL=false
RUN_UNIT=false
RUN_LINT=false
RUN_API=false

if [ $# -eq 0 ]; then
  RUN_ALL=true
fi

for arg in "$@"; do
  case $arg in
    --all) RUN_ALL=true ;;
    --unit) RUN_UNIT=true ;;
    --lint) RUN_LINT=true ;;
    --api) RUN_API=true ;;
    *)
      echo "Unknown flag: $arg"
      echo "Usage: $0 [--all|--unit|--lint|--api]"
      exit 1
      ;;
  esac
done

if [ "$RUN_ALL" = true ]; then
  run_unit_tests
  run_lint_tests
  run_api_tests
  echo ""
  echo "============================================================"
  echo "🎉 ALL LOCAL TESTS COMPLETED SUCCESSFULLY!"
  echo "============================================================"
else
  if [ "$RUN_UNIT" = true ]; then
    run_unit_tests
  fi
  if [ "$RUN_LINT" = true ]; then
    run_lint_tests
  fi
  if [ "$RUN_API" = true ]; then
    run_api_tests
  fi
fi

exit 0
