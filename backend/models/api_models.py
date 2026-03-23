from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Metrics(BaseModel):
    trial_count: int = Field(ge=0)
    patent_count: int = Field(ge=0)
    web_finding_count: int = Field(ge=0)
    internal_insight_count: int = Field(ge=0)


class TimingMetrics(BaseModel):
    request_duration_ms: float = Field(ge=0)
    agents: dict[str, dict[str, float | str]] = Field(default_factory=dict)


class DataSources(BaseModel):
    trials: str
    patents: str
    guidelines: str
    internal_docs_uploaded: bool


class RunResponse(BaseModel):
    request_id: str
    summary: str
    report_path: str
    report_url: str | None = None
    molecule: str | None = None
    indication: str | None = None
    master_confidence: str = "unknown"
    query_plan: list[dict[str, Any]] = Field(default_factory=list)
    fto_risk: str = "unknown"
    risk_assumptions: list[str] = Field(default_factory=list)
    agent_errors: dict[str, dict[str, str]] = Field(default_factory=dict)
    metrics: Metrics
    timing_metrics: TimingMetrics
    data_sources: DataSources
    logs: list[str] = Field(default_factory=list)


class ArchivesResponse(BaseModel):
    runs: list[dict[str, Any]] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    mode: str = "mock"
    warnings: list[str] = Field(default_factory=list)
