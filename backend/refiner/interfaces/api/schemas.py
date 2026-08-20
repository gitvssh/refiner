from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    storage: str = "ephemeral-memory"


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    coverage_score: int = Field(ge=0, le=100)
    matched_keywords: list[str]
    missing_keywords: list[str]
    strengths: list[str]


class RefinementResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis: AnalysisResponse
    rewritten_resume: str
    export_token: str
    export_expires_in_seconds: int = Field(gt=0, le=3600)
