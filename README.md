# AI Sight-Reading Studio — Dynamic Musical Practice Platform

An interactive, AI-powered web application capable of dynamically composing, rendering, and synthesizing playable musical sight-reading exercises tailored to any instrument, key signature, meter, and skill level. Built for musicians, music students, and educators.

---

## 🎵 Public Features & Studio Experience
*   **Dynamic Sight-Reading Exercises**: Generates fresh, musically coherent exercises on demand using Google Gemini AI—never practice the same piece twice.
*   **Interactive Web Audio Playback**: High-precision Web Audio synthesizer (`abcjs.synth`) with tempo control and sample soundfonts so you can listen to how any exercise sounds.
*   **Vector Sheet Music Score**: Crisp SVG sheet music rendering that looks beautiful on any device or screen size.
*   **Musician-First UI**: Premium dark-mode glassmorphism interface inspired by modern audio workstations.

---

## 🏗 System Architecture (Developer Reference)

```
+--------------------------------------------------------------------------------+
|                             Google Cloud Platform                              |
|                                                                                |
|  +--------------------+         +---------------------+    +----------------+  |
|  | Cloud Run Frontend |  HTTPS  |  Cloud Run Backend  |    |   Vertex AI    |  |
|  | (Next.js / abcjs)  | ------> |  (FastAPI / Python) | -> | (Gemini Model) |  |
|  +--------------------+  POST   +---------------------+    +----------------+  |
|            ^                               |                                   |
|            |                         Service Account                           |
|            +------------------------- (IAM Auth - ADC)                         |
+--------------------------------------------------------------------------------+
```

### Key Highlights
*   **Zero API Keys in Production**: The Cloud Run backend authenticates natively with Google Cloud Vertex AI via a dedicated **Service Account** (`ai-sight-reader-backend-sa`) using Application Default Credentials (ADC).
*   **Serverless Scaling**: Hosted on Google Cloud Run with scale-to-zero capability for optimal efficiency and performance.
*   **Standardized Tooling**: Uses **UV** for lightning-fast Python dependency management and **PNPM** for Next.js frontend package management.

---

## 📁 Project Structure

```
.
├── Makefile          # Essential developer movement & command shortcuts
├── backend/          # Python 3.11 FastAPI backend service (UV + Vertex AI Gemini SA auth)
├── frontend/         # Next.js 15 TypeScript frontend (PNPM + abcjs rendering & Web Audio)
├── infra/            # Terraform Infrastructure as Code for GCP
├── scripts/          # Shell scripts for GCP setup, Cloud Run deployment & local dev/test
├── docs/
│   ├── Design.md     # Full architectural specification & GCP Cloud-Native design
│   └── Plan.md       # Phased implementation & verification plan
└── docker-compose.yml # Multi-container local development stack (optional)
```

---

## ⚡ Essential Developer Movement (`Makefile`)

We provide a root `Makefile` to simplify all common development, testing, and GCP deployment workflows using **UV** and **PNPM**:

| Command | Description |
| :--- | :--- |
| **`make run-local`** | **⭐ Run the WHOLE application locally (`FastAPI` on 8080 + `Next.js` on 3000 concurrently)** |
| **`make run` / `make dev`** | **Aliases for `make run-local`** |
| `make help` | View all available targets and descriptions |
| `make test` | Run backend unit test suite via UV (`make test-unit`) |
| `make test-local` | Run comprehensive local testing battery (Unit + Lint + API integration) |
| `make test-unit` | Run ABC Validator & Healthcheck unit tests via UV |
| `make test-api` | Run API integration checks against local server (or in-memory via UV) |
| `make lint` | Syntax check and compilation verification for backend & frontend via PNPM |
| `make setup-gcp` | Enable GCP APIs, create Gemini Service Account, and bind IAM roles |
| `make deploy-gcp` | Build containers via Google Cloud Build and deploy to Cloud Run |
| `make install-backend` | Create `.venv` and install Python backend requirements using **UV** |
| `make run-backend` | Start ONLY FastAPI backend server locally on port 8080 via `uv run` |
| `make install-frontend` | Install Next.js frontend dependencies via **PNPM** (`pnpm install`) |
| `make run-frontend` | Start ONLY Next.js frontend dev server locally on port 3000 (`pnpm dev`) |
| `make build-frontend` | Build standalone production Next.js bundle (`pnpm build`) |
| `make clean` | Remove build artifacts, cache files, and virtual environments |

---

## 🚀 How to Run & Deploy

> [!NOTE]
> **Why did `docker compose up` fail?**  
> If you received an error like `exec: "docker-compose": executable file not found in $PATH` or `looking up compose provider failed`, your environment has Docker/Podman installed without the `docker-compose` CLI plugin or rootless networking (`pasta`).  
> **Good news:** You do **not** need local Docker Compose to develop or deploy this project! Follow one of the two recommended methods below.

### Method 1: Local Full-Stack Development (No Containers Needed)
You can run the entire application locally with one command:
```bash
make run-local
# (or simply: make run / make dev)
```
*   **What it does:**
    1. Automatically creates the Python virtualenv and installs backend dependencies via **UV** (if needed).
    2. Automatically installs frontend dependencies via **PNPM** (if needed).
    3. Starts the **FastAPI Backend** on `http://localhost:8080` in the background.
    4. Starts the **Next.js Frontend** on `http://localhost:3000` in the background.
    5. Streams logs from both servers and stops both cleanly when you press **`Ctrl+C`**.

---

### Method 2: Direct Cloud Run Deployment via Google Cloud Build (Recommended for GCP)
Since this project is designed for GCP, you can build container images remotely using **Google Cloud Build** and deploy directly to **Google Cloud Run** without needing local Docker or Compose:

1.  **Set your GCP Project ID & Region**:
    ```bash
    export GCP_PROJECT_ID="your-gcp-project-id"
    export GCP_REGION="us-central1"
    ```
2.  **Enable APIs & Provision the Gemini Service Account**:
    ```bash
    make setup-gcp
    ```
3.  **Build via Cloud Build & Deploy to Cloud Run**:
    ```bash
    make deploy-gcp
    ```
    *Cloud Build builds your containers in Google Cloud and deploys both the backend and frontend automatically.*

### 3. Deploying to AI Agent Runtime & Registering in Google Agent Registry
The modular Google ADK Agent Engine (`backend/app/agent/`) can be deployed directly to Vertex AI Agent Runtime (Reasoning Engine) or Cloud Run using our automated `Makefile` targets:

```bash
# 1. Deploy ADK Agent to Vertex AI Agent Runtime (Managed Reasoning Engine)
make deploy-adk-agent-runtime

# 2. Or Deploy ADK Agent as Serverless Container on Cloud Run (A2A Protocol)
make deploy-adk-cloud-run
```

Once deployed, publish your agent to **Agent Registry / Gemini Enterprise** for organization-wide discovery:

```bash
# 1. Publish Agent Runtime Deployment (ADK Native Mode - auto-registered in Agent Registry)
agents-cli publish gemini-enterprise \
  --registration-type adk \
  --agent-runtime-id projects/$GCP_PROJECT_ID/locations/$GCP_REGION/reasoningEngines/<ENGINE_ID> \
  --gemini-enterprise-app-id projects/$GCP_PROJECT_ID/locations/global/collections/default_collection/engines/<APP_ID> \
  --display-name "Sight-Reading Composer"

# 2. Or Publish Cloud Run Service (A2A Protocol Mode)
agents-cli publish gemini-enterprise \
  --registration-type a2a \
  --agent-card-url https://<your-cloudrun-url>.run.app/a2a/app/.well-known/agent-card.json \
  --gemini-enterprise-app-id projects/$GCP_PROJECT_ID/locations/global/collections/default_collection/engines/<APP_ID>

# 3. Inspect registered agents in Google Cloud Agent Registry
gcloud alpha agent-registry agents list --project $GCP_PROJECT_ID --location $GCP_REGION
```

---

## ☁️ Infrastructure as Code (Terraform)
For automated reproducible GCP infrastructure provisioning:
```bash
cd infra
terraform init
terraform apply -var="project_id=your-gcp-project-id" -var="region=us-central1"
```

---

## 📚 Documentation
*   [Architectural Design Document](file:///usr/local/google/home/eddieckc/sight-reading-tool/docs/Design.md)
*   [Engineering & Execution Plan](file:///usr/local/google/home/eddieckc/sight-reading-tool/docs/Plan.md)
