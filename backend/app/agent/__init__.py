"""
Google ADK (Agent Development Kit) engine for the AI Sight-Reading tool.
Separates prompts, tools, and agent definitions into modular, extensible files.
"""
from .agent import create_sight_reading_agent
from .prompt import SYSTEM_INSTRUCTION, build_composition_prompt
from .tools import validate_abc_score_tool
from .service import SightReadingAgentEngine, adk_composer_engine
from .instruments import get_instrument_profile, get_instrument_config, INSTRUMENT_CONFIGS

__all__ = [
    "create_sight_reading_agent",
    "SYSTEM_INSTRUCTION",
    "build_composition_prompt",
    "validate_abc_score_tool",
    "SightReadingAgentEngine",
    "adk_composer_engine",
    "get_instrument_profile",
    "get_instrument_config",
    "INSTRUMENT_CONFIGS",
]

