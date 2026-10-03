from typing import Literal

from pydantic import BaseModel, Field


Confidence = Literal["low", "medium", "high"]


class AgentFinding(BaseModel):
    agent: str
    status: Literal["completed", "needs_review", "skipped"] = "completed"
    finding: str
    evidence: list[str] = Field(default_factory=list)
    calculation: dict[str, float | str] = Field(default_factory=dict)
    confidence: Confidence = "medium"
    limitations: list[str] = Field(default_factory=list)
    recommended_action: str = ""
    sources: list[str] = Field(default_factory=list)


class FieldAssessment(BaseModel):
    crop: str
    crop_stage: str
    field_area_acres: float
    soil_moisture_pct: float
    recent_rain_mm: float
    forecast_rain_mm: float
    temperature_c: float
    wind_kph: float
    location: str = ""
    image_bytes: bytes | None = None
    notes: str = ""


class AssessmentResult(BaseModel):
    findings: list[AgentFinding]
    priority: Literal["routine", "soon", "urgent"]
    summary: str
    actions: list[str]
    evidence: list[str]
    assumptions: list[str]
    limitations: list[str]
    review_flags: list[str]