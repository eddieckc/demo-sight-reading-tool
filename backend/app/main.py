import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.endpoints import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_sight_reader")

app = FastAPI(
    title="AI Sight-Reading Tool API",
    description="FastAPI service generating musical sight-reading exercises via Gemini on Vertex AI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure Cross-Origin Resource Sharing (CORS) for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    logger.info("AI Sight-Reading Tool Backend startup initiated.")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"GCP Project: {settings.gcp_project_id} | Location: {settings.gcp_location}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("AI Sight-Reading Tool Backend shutting down.")
