from fastapi import APIRouter, HTTPException, status
from app.schemas.exercise import ExerciseRequest, ExerciseResponse, ErrorResponse
from app.agent import adk_composer_engine

router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="API Root & Status",
    description="Returns metadata and available endpoints for the AI Sight-Reading Tool backend API."
)
async def root():
    return {
        "service": "ai-sight-reader-backend",
        "status": "online",
        "documentation": "/docs",
        "health": "/health",
        "generate_endpoint": "/api/generate-exercise",
        "description": "FastAPI backend & ADK Agent Engine. Access the Next.js frontend web app for the interactive UI."
    }


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    description="Returns JSON status indicating the Cloud Run backend is healthy."
)
async def health_check():
    return {"status": "ok", "service": "ai-sight-reader-backend"}


@router.post(
    "/api/generate-exercise",
    response_model=ExerciseResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters or generated notation"},
        500: {"model": ErrorResponse, "description": "AI generation service error"}
    },
    summary="Generate Musical Sight-Reading Exercise",
    description="Invokes Google ADK Agent on Vertex AI to generate a playable musical exercise in ABC notation."
)
async def generate_exercise(request: ExerciseRequest) -> ExerciseResponse:
    try:
        composition_result = await adk_composer_engine.generate_sight_reading_exercise(request)
        return ExerciseResponse(
            abc_notation=composition_result["abc_notation"],
            difficulty=request.difficulty,
            key_signature=request.key_signature,
            instrument=request.instrument,
            time_signature=request.time_signature,
            tempo=request.tempo,
            bars=request.bars,
            token_usage=composition_result.get("token_usage"),
            estimated_cost_usd=composition_result.get("estimated_cost_usd"),
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        ) from val_err
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate exercise: {str(exc)}"
        ) from exc
