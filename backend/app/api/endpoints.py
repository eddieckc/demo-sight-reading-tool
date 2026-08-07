import json
import re
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from app.schemas.exercise import ExerciseRequest, ExerciseResponse, ErrorResponse
from app.agent import adk_composer_engine

router = APIRouter()


def _parse_exercise_request(input_data: dict) -> ExerciseRequest:
    if not isinstance(input_data, dict):
        return ExerciseRequest()
    if "request" in input_data and isinstance(input_data["request"], dict):
        input_data = input_data["request"]

    valid_fields = ExerciseRequest.model_fields.keys()
    filtered_kwargs = {k: v for k, v in input_data.items() if k in valid_fields and v is not None}

    # Extract text from message/prompt if present (e.g. from Agent Playground chat input)
    text_prompt = ""
    message = input_data.get("message") or input_data.get("prompt")
    if isinstance(message, str):
        text_prompt = message
    elif isinstance(message, dict):
        parts = message.get("parts", [])
        text_prompt = " ".join([p.get("text", "") for p in parts if isinstance(p, dict)])

    if text_prompt:
        text_lower = text_prompt.lower()
        if "difficulty" not in filtered_kwargs:
            for diff in ["beginner", "intermediate", "advanced", "expert"]:
                if diff in text_lower:
                    filtered_kwargs["difficulty"] = diff
                    break
        if "instrument" not in filtered_kwargs:
            for inst in ["piano", "violin", "flute", "saxophone", "guitar", "cello"]:
                if inst in text_lower:
                    filtered_kwargs["instrument"] = inst
                    break
        if "key_signature" not in filtered_kwargs:
            key_match = re.search(r'\bin ([a-g][b#]?m?)\b', text_prompt, re.IGNORECASE)
            if key_match:
                filtered_kwargs["key_signature"] = key_match.group(1).upper()
        if "time_signature" not in filtered_kwargs:
            time_match = re.search(r'\b(\d/\d)\b', text_prompt)
            if time_match:
                filtered_kwargs["time_signature"] = time_match.group(1)
        if "bars" not in filtered_kwargs:
            bars_match = re.search(r'\b(\d+)\s*bars?\b', text_lower)
            if bars_match:
                filtered_kwargs["bars"] = int(bars_match.group(1))
        if "tempo" not in filtered_kwargs:
            tempo_match = re.search(r'\b(\d+)\s*(bpm|tempo)\b', text_lower)
            if tempo_match:
                filtered_kwargs["tempo"] = int(tempo_match.group(1))

    return ExerciseRequest(**filtered_kwargs)


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
        "agent_runtime_endpoints": [
            "/api/stream_reasoning_engine",
            "/api/reasoning_engine"
        ],
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


@router.post(
    "/api/stream_reasoning_engine",
    summary="Agent Runtime Streaming Endpoint",
    description="Stream Reasoning Engine endpoint invoked by Vertex AI Agent Runtime and SDK."
)
async def stream_reasoning_engine(request: Request) -> StreamingResponse:
    try:
        body = await request.json()
    except Exception:
        body = {}

    input_data = body.get("input", {}) if isinstance(body, dict) else {}
    exercise_req = _parse_exercise_request(input_data)

    async def event_generator():
        try:
            result = await adk_composer_engine.generate_sight_reading_exercise(exercise_req)
            abc_notation = result.get("abc_notation", "")
            # Return ADK Event structure so Vertex AI Agent Playground renders chat UI
            event = {
                "author": "sight_reading_composer",
                "content": {
                    "role": "model",
                    "parts": [{"text": abc_notation}]
                },
                "output": result
            }
            yield json.dumps(event) + "\n"
        except Exception as exc:
            yield json.dumps({"error": str(exc)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/json")


@router.post(
    "/api/reasoning_engine",
    summary="Agent Runtime Sync Endpoint",
    description="Sync Reasoning Engine endpoint invoked by Vertex AI Agent Runtime and SDK."
)
async def reasoning_engine(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except Exception:
        body = {}

    input_data = body.get("input", {}) if isinstance(body, dict) else {}
    exercise_req = _parse_exercise_request(input_data)

    try:
        result = await adk_composer_engine.generate_sight_reading_exercise(exercise_req)
        abc_notation = result.get("abc_notation", "")
        return JSONResponse(content={
            "author": "sight_reading_composer",
            "content": {
                "role": "model",
                "parts": [{"text": abc_notation}]
            },
            "output": result
        })
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        ) from exc


