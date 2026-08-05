"""
Backwards-compatible wrapper re-exporting the Google ADK Agent Engine.
All core prompt, tool, and agent logic has been modularized under app.agent.
"""
from app.agent import adk_composer_engine as gemini_service, SightReadingAgentEngine as GeminiService

__all__ = ["gemini_service", "GeminiService"]
