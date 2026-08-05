from typing import Optional
from pydantic import BaseModel, Field


class ExerciseRequest(BaseModel):
    """
    Request schema for generating a sight-reading musical exercise.
    """
    difficulty: str = Field(
        default="intermediate",
        description="Difficulty level: beginner, intermediate, advanced, or expert.",
        examples=["intermediate"]
    )
    key_signature: str = Field(
        default="C",
        description="Musical key signature (e.g., C, G, F, Am, D, Bb).",
        examples=["G"]
    )
    instrument: str = Field(
        default="piano",
        description="Target instrument for clef and range selection (e.g., piano, violin, flute, saxophone, guitar, cello).",
        examples=["saxophone"]
    )
    time_signature: str = Field(
        default="4/4",
        description="Time signature / meter (e.g., 4/4, 3/4, 2/4, 6/8).",
        examples=["4/4"]
    )
    tempo: int = Field(
        default=110,
        ge=40,
        le=240,
        description="Tempo in Beats Per Minute (BPM).",
        examples=[110]
    )
    bars: int = Field(
        default=4,
        ge=2,
        le=16,
        description="Number of measures/bars to generate.",
        examples=[4]
    )


class ExerciseResponse(BaseModel):
    """
    Response schema returning the synthesized ABC Notation string and metadata.
    """
    abc_notation: str = Field(
        ...,
        description="Valid ABC Notation string ready for abcjs rendering and audio synthesis."
    )
    difficulty: str
    key_signature: str
    instrument: str
    time_signature: str
    tempo: int
    bars: int
    token_usage: Optional[int] = Field(
        default=None,
        description="Total AI tokens consumed to compose this musical exercise."
    )
    estimated_cost_usd: Optional[float] = Field(
        default=None,
        description="Estimated AI API generation cost in USD."
    )


class ErrorResponse(BaseModel):
    """
    Structured error response schema.
    """
    error: str = Field(..., description="Error message describing the failure reason.")
    detail: Optional[str] = Field(None, description="Optional technical diagnostic detail.")
