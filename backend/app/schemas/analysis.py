from typing import Literal

from pydantic import BaseModel, Field


QualityStatus = Literal["acceptable", "warning", "ungradable"]
ScreeningClass = Literal["normal", "abnormal", "uncertain", "ungradable"]
FindingStatus = Literal["detected", "suspected", "not_evaluated"]


class ImageQuality(BaseModel):
    status: QualityStatus
    width: int
    height: int
    warnings: list[str] = Field(default_factory=list)


class Score(BaseModel):
    label: str
    value: float = Field(ge=0, le=1)


class Finding(BaseModel):
    name: str
    status: FindingStatus
    explanation: str
    significance: str
    region: list[int] | None = None


class AnalysisResult(BaseModel):
    analysis_id: str
    image_quality: ImageQuality
    screening_class: ScreeningClass | None = None
    predicted_class: str | None = None
    scores: list[Score] = Field(default_factory=list)
    dr_grade: int | None = Field(default=None, ge=0, le=4)
    findings: list[Finding] = Field(default_factory=list)
    explanation_available: bool = False
    explanation_message: str
    model_available: bool
    model_name: str
    model_version: str
    limitations: list[str] = Field(default_factory=list)
    follow_up: str


class ModelInfo(BaseModel):
    name: str
    version: str
    architecture: str
    supported_tasks: list[str]
    supported_classes: list[str]
    input_dimensions: list[int]
    dataset: str | None
    model_available: bool
    limitations: list[str]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_available: bool
