"""
Service orchestrator for the Google ADK Sight-Reading Composer Agent Engine.
Connects the modular ADK Agent, prompts, and tools with self-healing retry logic
and token/cost accounting.
"""
import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai import types

from app.config import settings
from app.schemas.exercise import ExerciseRequest
from app.agent.agent import create_sight_reading_agent
from app.agent.prompt import build_composition_prompt, SYSTEM_INSTRUCTION
from app.agent.tools import validate_abc_score_tool

logger = logging.getLogger(__name__)


class SightReadingAgentEngine:
    """
    Google ADK Agent Engine orchestrating music composition requests.
    Separates prompt generation, tool validation, and agent definition into modular files,
    while tracking token usage and estimating generation cost.
    """

    def __init__(self) -> None:
        self.project_id = settings.gcp_project_id
        self.location = settings.gcp_location
        self.model_name = settings.gemini_model
        self.adk_agent = create_sight_reading_agent(model=self.model_name)
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            logger.info(
                f"Initializing ADK Agent Vertex AI Client (Project: {self.project_id}, "
                f"Location: {self.location}, Model: {self.model_name})"
            )
            self._client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
        return self._client

    async def generate_sight_reading_exercise(
        self, request: ExerciseRequest, max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Orchestrates music composition using the ADK agent engine, prompts, and tools.
        Includes automatic self-healing retries for incomplete or un-validated responses,
        and returns ABC notation along with token usage and estimated USD cost.
        """
        last_error = ""
        for attempt in range(1, max_retries + 1):
            try:
                user_prompt = build_composition_prompt(request, previous_error=last_error)

                # Set max_output_tokens=8192 so reasoning models generating 16-bar scores
                # have ample token budget for both internal reasoning and full ABC notation output.
                config = types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.7 + (attempt - 1) * 0.1,
                    max_output_tokens=8192,
                )

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=config,
                )

                # Extract token accounting from usage metadata
                prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                candidates_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                total_tokens = getattr(response.usage_metadata, "total_token_count", 0) or (
                    prompt_tokens + candidates_tokens
                )

                # Estimate cost in USD using Gemini Flash pricing ($0.075 / 1M input, $0.30 / 1M output)
                cost_usd = round((prompt_tokens * 0.000000075) + (candidates_tokens * 0.00000030), 6)

                raw_text = response.text or ""
                validation_result = validate_abc_score_tool(
                    raw_abc=raw_text,
                    default_title=f"{request.difficulty.title()} {request.instrument.title()} Exercise",
                    default_key=request.key_signature,
                    default_meter=request.time_signature,
                    default_tempo=request.tempo,
                    expected_bars=request.bars,
                    instrument=request.instrument,
                    difficulty=request.difficulty,
                )

                if validation_result["is_valid"]:
                    if attempt > 1:
                        logger.info(f"ADK Agent successfully composed valid ABC notation on attempt {attempt}.")
                    return {
                        "abc_notation": validation_result["cleaned_abc"],
                        "token_usage": total_tokens,
                        "estimated_cost_usd": cost_usd,
                    }

                error_msg = validation_result["error_message"]
                logger.warning(
                    f"ADK Agent attempt {attempt}/{max_retries} failed validation: {error_msg}. Raw output: {raw_text}"
                )
                last_error = error_msg

            except Exception as exc:
                logger.warning(f"ADK Agent attempt {attempt}/{max_retries} encountered exception: {str(exc)}")
                last_error = str(exc)

        logger.error(f"All {max_retries} attempts failed in ADK Agent Engine. Last error: {last_error}")
        raise ValueError(f"Could not generate a valid musical score after {max_retries} attempts: {last_error}")


adk_composer_engine = SightReadingAgentEngine()
