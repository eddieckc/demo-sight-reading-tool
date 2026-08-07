import json
import re
import time
import uuid
from typing import Tuple, Dict, Any
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from app.schemas.exercise import ExerciseRequest, ExerciseResponse, ErrorResponse
from app.agent import adk_composer_engine

router = APIRouter()


def _extract_request_payload(body: dict) -> Tuple[str, dict, str, str, str]:
    """
    Extracts class_method, merged input dictionary, session_id, user_id, and invocation_id
    from the Reasoning Engine request body.
    Supports raw input dicts, 'request_json' strings from Gemini Enterprise / AgentSpace,
    and direct API invocations.
    """
    if not isinstance(body, dict):
        return "streaming_agent_run_with_events", {}, str(uuid.uuid4()), "default_user", ""

    class_method = body.get("class_method", "streaming_agent_run_with_events")
    input_data = body.get("input", {})
    if not isinstance(input_data, dict):
        input_data = {}

    # Gemini Enterprise sends request parameters wrapped in 'request_json' JSON string
    if "request_json" in input_data:
        raw_req_json = input_data["request_json"]
        if isinstance(raw_req_json, str):
            try:
                parsed_json = json.loads(raw_req_json)
                if isinstance(parsed_json, dict):
                    # Merge parsed_json into input_data
                    input_data = {**input_data, **parsed_json}
            except Exception:
                pass
        elif isinstance(raw_req_json, dict):
            input_data = {**input_data, **raw_req_json}

    session_id = str(input_data.get("session_id") or input_data.get("sessionId") or uuid.uuid4())
    user_id = str(input_data.get("user_id") or input_data.get("userId") or "default_user")
    invocation_id = str(input_data.get("invocation_id") or input_data.get("invocationId") or "")

    return class_method, input_data, session_id, user_id, invocation_id


def _parse_exercise_request(input_data: dict) -> ExerciseRequest:
    if not isinstance(input_data, dict):
        return ExerciseRequest()
    if "request" in input_data and isinstance(input_data["request"], dict):
        input_data = input_data["request"]

    valid_fields = ExerciseRequest.model_fields.keys()
    filtered_kwargs = {k: v for k, v in input_data.items() if k in valid_fields and v is not None}

    # Extract text from message/prompt if present (e.g. from Gemini Enterprise chat or Agent Playground)
    text_prompt = ""
    message = input_data.get("message") or input_data.get("prompt") or input_data.get("input") or input_data.get("query")
    if isinstance(message, str):
        text_prompt = message
    elif isinstance(message, dict):
        parts = message.get("parts", [])
        if isinstance(parts, list):
            text_prompt = " ".join([p.get("text", "") for p in parts if isinstance(p, dict)])
        elif "text" in message:
            text_prompt = str(message["text"])
    elif isinstance(message, list):
        extracted_parts = []
        for item in message:
            if isinstance(item, str):
                extracted_parts.append(item)
            elif isinstance(item, dict):
                for p in item.get("parts", []):
                    if isinstance(p, dict) and "text" in p:
                        extracted_parts.append(p["text"])
        text_prompt = " ".join(extracted_parts)

    if text_prompt:
        text_lower = text_prompt.lower()
        if "difficulty" not in filtered_kwargs:
            for diff in ["beginner", "intermediate", "advanced", "expert"]:
                if diff in text_lower:
                    filtered_kwargs["difficulty"] = diff
                    break
        if "instrument" not in filtered_kwargs:
            for inst in ["piano", "violin", "flute", "saxophone", "guitar", "cello", "clarinet", "trumpet"]:
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
    summary="Agent Runtime Streaming Endpoint (Gemini Enterprise & Vertex AI SDK)",
    description="Stream Reasoning Engine endpoint invoked by Gemini Enterprise, Vertex AI Agent Runtime, and SDK."
)
async def stream_reasoning_engine(request: Request) -> StreamingResponse:
    try:
        body = await request.json()
    except Exception:
        body = {}

    class_method, input_data, session_id, user_id, invocation_id = _extract_request_payload(body)
    exercise_req = _parse_exercise_request(input_data)

    async def event_generator():
        try:
            result = await adk_composer_engine.generate_sight_reading_exercise(exercise_req)
            abc_notation = result.get("abc_notation", "")

            # Formulate clear response text formatted with Markdown ABC block for Gemini Enterprise UI
            response_text = (
                f"Here is your {exercise_req.difficulty.title()} {exercise_req.instrument.title()} "
                f"sight-reading exercise in {exercise_req.key_signature} ({exercise_req.bars} bars):\n\n"
                f"```abc\n{abc_notation}\n```"
            )

            # Build Google ADK Event schema
            event_id = str(uuid.uuid4())
            adk_event = {
                "id": event_id,
                "author": "sight_reading_composer",
                "content": {
                    "role": "model",
                    "parts": [{"text": response_text}]
                },
                "invocation_id": invocation_id,
                "actions": {
                    "state_delta": {},
                    "artifact_delta": {},
                    "requested_auth_configs": {},
                    "requested_tool_confirmations": {}
                },
                "node_info": {"path": ""},
                "timestamp": time.time(),
                "output": result
            }

            # If invoked via Gemini Enterprise / AgentSpace (streaming_agent_run_with_events)
            if class_method == "streaming_agent_run_with_events":
                # GE strictly requires StreamingRunResponse structure with top-level 'events' list
                streaming_run_response = {
                    "events": [adk_event],
                    "artifacts": [],
                    "session_id": session_id
                }
                yield json.dumps(streaming_run_response) + "\n"
            else:
                # Vertex AI SDK / Console Playground stream_query contract
                # Yield both event dictionary and embedded events array for maximum compatibility
                yield json.dumps(adk_event) + "\n"

        except Exception as exc:
            error_event = {
                "id": str(uuid.uuid4()),
                "author": "sight_reading_composer",
                "content": {
                    "role": "model",
                    "parts": [{"text": f"Error generating sight-reading exercise: {str(exc)}"}]
                },
                "invocation_id": invocation_id,
                "timestamp": time.time()
            }
            if class_method == "streaming_agent_run_with_events":
                yield json.dumps({
                    "events": [error_event],
                    "artifacts": [],
                    "session_id": session_id,
                    "error": str(exc)
                }) + "\n"
            else:
                yield json.dumps({**error_event, "error": str(exc)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/json")


@router.post(
    "/api/reasoning_engine",
    summary="Agent Runtime Sync Endpoint (Gemini Enterprise & Vertex AI SDK)",
    description="Sync Reasoning Engine endpoint invoked by Gemini Enterprise, Vertex AI Agent Runtime, and SDK."
)
async def reasoning_engine(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except Exception:
        body = {}

    class_method, input_data, session_id, user_id, invocation_id = _extract_request_payload(body)
    exercise_req = _parse_exercise_request(input_data)

    try:
        result = await adk_composer_engine.generate_sight_reading_exercise(exercise_req)
        abc_notation = result.get("abc_notation", "")
        response_text = (
            f"Here is your {exercise_req.difficulty.title()} {exercise_req.instrument.title()} "
            f"sight-reading exercise in {exercise_req.key_signature} ({exercise_req.bars} bars):\n\n"
            f"```abc\n{abc_notation}\n```"
        )
        event_id = str(uuid.uuid4())
        adk_event = {
            "id": event_id,
            "author": "sight_reading_composer",
            "content": {
                "role": "model",
                "parts": [{"text": response_text}]
            },
            "invocation_id": invocation_id,
            "timestamp": time.time(),
            "output": result
        }
        return JSONResponse(content={
            "output": result,
            "response": response_text,
            "author": "sight_reading_composer",
            "content": {
                "role": "model",
                "parts": [{"text": response_text}]
            },
            "events": [adk_event],
            "session_id": session_id
        })
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        ) from exc


