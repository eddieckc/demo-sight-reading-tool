#!/usr/bin/env bash
# ==============================================================================
# Run Full-Stack Application Locally (Backend + Frontend Concurrently)
# Uses UV for FastAPI backend (port 8080) and PNPM for Next.js frontend (port 3000).
# ==============================================================================
set -euo pipefail

UV_CMD="uv"
PNPM_CMD="pnpm"

echo "============================================================"
echo "🎵 AI Sight-Reading Tool: Starting Local Full-Stack App"
echo "============================================================"

# 0. Check and install dependencies if missing
if [ ! -d "backend/.venv" ]; then
  echo "⚡ Installing Backend Python dependencies via UV..."
  (cd backend && ${UV_CMD} venv .venv && ${UV_CMD} pip install -r requirements.txt)
fi

if [ ! -d "frontend/node_modules" ]; then
  echo "⚡ Installing Frontend Node dependencies via PNPM..."
  (cd frontend && ${PNPM_CMD} install)
fi

# Define cleanup handler so Ctrl+C (SIGINT / SIGTERM) stops both background servers cleanly
cleanup() {
  echo ""
  echo "⏹️  Stopping local development servers..."
  kill $(jobs -p) 2>/dev/null || true
  echo "✅ Both Backend (port 8080) and Frontend (port 3000) servers stopped."
  exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Start Python FastAPI Backend in background
echo "🚀 [1/2] Starting Python FastAPI Backend on http://localhost:8080 (via UV)..."
(
  cd backend
  ${UV_CMD} run uvicorn app.main:app --reload --port 8080 --host 0.0.0.0
) &
BACKEND_PID=$!

# Wait a brief moment for backend to initialize
sleep 2

# 2. Start Next.js Frontend in background
echo "🚀 [2/2] Starting Next.js Frontend on http://localhost:3000 (via PNPM)..."
(
  cd frontend
  ${PNPM_CMD} dev
) &
FRONTEND_PID=$!

echo "============================================================"
echo "🎉 Full-Stack Application is running locally!"
echo "🎵 Web UI (Frontend):   http://localhost:3000"
echo "⚡ Backend API Docs:    http://localhost:8080/docs"
echo "👉 Press Ctrl+C at any time to stop both servers."
echo "============================================================"

# Keep script alive and stream logs until Ctrl+C is pressed
wait "${BACKEND_PID}" "${FRONTEND_PID}"
