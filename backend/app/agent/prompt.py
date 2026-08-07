"""
Modular prompt definitions for the Google ADK Sight-Reading Composer Agent.
Extensible and easy to duplicate for new instruments, pedagogical rules, or skills.
"""
from app.schemas.exercise import ExerciseRequest
from app.agent.instruments import get_instrument_profile

SYSTEM_INSTRUCTION = (
    "You are an expert music composer and educator. Compose playable musical sight-reading exercises "
    "in standard ABC notation format.\n\n"
    "CRITICAL COMPOSITION RULES:\n"
    "1. Always generate complete ABC notation: include the metadata headers (X:, T:, M:, L:, Q:, K:) and the full musical melody.\n"
    "2. You MUST include musical rests ('z', 'z2', or 'z4') in at least one measure so the student practices counting silences.\n"
    "3. Keep pitch range and clef idiomatic for the target instrument according to its pedagogical character profile.\n"
    "4. Do NOT include any trills ('tr', '~', 'T'), grace notes ('{...}'), turns, or ornamentation (no TR skill). "
    "Keep the notes and rests plain and clean for sight-reading practice.\n"
    "5. Always separate individual notes with a space (e.g. 'G2 A2 B2 c2 | d2 e2 F2 G2 |]') so notes are not beamed or linked together. Every note must have its own separate stem for clear sight-reading practice.\n"
    "6. Output ONLY raw ABC notation without markdown fenced blocks, backticks, commentary, or conversational text."
)


def get_measure_layout_plan(bars: int) -> str:
    """
    Generates an explicit line-by-line measure layout plan to guide accurate LLM measure counting.
    """
    if bars == 4:
        return (
            "MEASURE LAYOUT PLAN (EXACTLY 4 BARS REQUIRED):\n"
            "Line 1: bar 1 | bar 2 | bar 3 | bar 4 |]"
        )
    elif bars == 8:
        return (
            "MEASURE LAYOUT PLAN (EXACTLY 8 BARS REQUIRED - 4 bars per line):\n"
            "Line 1: bar 1 | bar 2 | bar 3 | bar 4 |\n"
            "Line 2: bar 5 | bar 6 | bar 7 | bar 8 |]"
        )
    elif bars == 12:
        return (
            "MEASURE LAYOUT PLAN (EXACTLY 12 BARS REQUIRED - 4 bars per line):\n"
            "Line 1: bar 1 | bar 2 | bar 3 | bar 4 |\n"
            "Line 2: bar 5 | bar 6 | bar 7 | bar 8 |\n"
            "Line 3: bar 9 | bar 10 | bar 11 | bar 12 |]"
        )
    elif bars == 16:
        return (
            "MEASURE LAYOUT PLAN (EXACTLY 16 BARS REQUIRED - 4 bars per line):\n"
            "You MUST generate all 16 measures across 4 lines of music:\n"
            "Line 1: bar 1 | bar 2 | bar 3 | bar 4 |\n"
            "Line 2: bar 5 | bar 6 | bar 7 | bar 8 |\n"
            "Line 3: bar 9 | bar 10 | bar 11 | bar 12 |\n"
            "Line 4: bar 13 | bar 14 | bar 15 | bar 16 |]"
        )
    else:
        return f"MEASURE LAYOUT PLAN (EXACTLY {bars} BARS REQUIRED): Generate exactly {bars} measures ending with '|]'."


def build_composition_prompt(request: ExerciseRequest, previous_error: str = "") -> str:
    """
    Builds the user prompt requesting the ADK Agent to compose a sight-reading exercise.
    Incorporates the individualized instrument character profile, exact measure layout plan,
    and self-healing feedback from previous failed attempts if any.
    """
    instrument_profile = get_instrument_profile(request.instrument, request.difficulty)
    measure_layout = get_measure_layout_plan(request.bars)

    error_feedback = ""
    if previous_error:
        error_feedback = (
            f"PREVIOUS ATTEMPT CORRECTION NEEDED:\n"
            f"Your previous attempt failed validation with error: {previous_error}\n"
            f"Please strictly fix this error: keep all pitches within the instrument's playable range, "
            f"use the correct clef, and ensure exact measure count.\n\n"
        )

    return (
        f"{error_feedback}"
        f"Write a {request.bars}-measure musical sight-reading exercise in standard ABC notation format "
        f"for {request.instrument} at {request.difficulty} difficulty in the key of {request.key_signature} "
        f"with {request.time_signature} meter at {request.tempo} BPM.\n\n"
        f"{instrument_profile}\n\n"
        f"{measure_layout}\n\n"
        "REQUIREMENTS:\n"
        f"1. Must have exactly {request.bars} measures of music separated by '|' bar lines and ending with '|]'.\n"
        f"2. Every note MUST be within the allowed pitch range for {request.instrument}. Do NOT exceed lowest or highest note boundaries.\n"
        "3. Include at least one musical rest ('z', 'z2', or 'z4') in the melody.\n"
        "4. Do not include any trills, grace notes, or ornamentation (no TR skill).\n"
        "5. Separate individual notes with a space so notes are not beamed or linked together.\n"
        "6. Do not use markdown backticks, bullet points, or explanations—output only the raw ABC notation headers and notes."
    )

