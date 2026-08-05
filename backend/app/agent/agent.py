"""
Modular Google ADK Agent definition for the Sight-Reading Composer engine.
Separated from prompts and tools so that the agent configuration can be duplicated and extended easily.
"""
import logging
from typing import Optional
from google.adk.agents import Agent
from app.config import settings
from app.agent.prompt import SYSTEM_INSTRUCTION
from app.agent.tools import validate_abc_score_tool

logger = logging.getLogger(__name__)


def create_sight_reading_agent(
    name: str = "sight_reading_composer",
    model: Optional[str] = None,
    instruction: Optional[str] = None,
) -> Agent:
    """
    Factory function that creates a Google ADK Agent for sight-reading music composition.
    Extensible and easy to duplicate for new specialized composer agents.
    """
    agent_model = model or settings.gemini_model
    agent_instruction = instruction or SYSTEM_INSTRUCTION

    logger.info(f"Creating ADK Agent '{name}' with model '{agent_model}'")
    return Agent(
        name=name,
        model=agent_model,
        instruction=agent_instruction,
        description="An expert AI composer agent for sight-reading musical exercises in standard ABC notation.",
        tools=[validate_abc_score_tool],
    )
