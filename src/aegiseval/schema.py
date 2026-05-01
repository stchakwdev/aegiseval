from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ArtifactSpec(BaseModel):
    path: str
    kind: str
    required: bool = True

    @field_validator("path")
    @classmethod
    def path_must_be_workspace_relative(cls, value: str) -> str:
        path = Path(value)
        if not value.strip() or path.is_absolute() or ".." in path.parts:
            raise ValueError("artifact path must be a non-empty workspace-relative path")
        return value


class GraderSpec(BaseModel):
    name: str
    kind: Literal["code", "model", "hybrid"] = "code"
    config: dict[str, Any] = Field(default_factory=dict)


class ToolSpec(BaseModel):
    name: str
    description: str = ""


class TaskSpec(BaseModel):
    id: str
    version: str
    domain: str
    instruction: str
    expected_artifacts: list[ArtifactSpec]
    grader: GraderSpec
    tools: list[ToolSpec] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("expected_artifacts")
    @classmethod
    def expected_artifacts_must_not_be_empty(cls, value: list[ArtifactSpec]) -> list[ArtifactSpec]:
        if not value:
            raise ValueError("expected_artifacts must contain at least one artifact")
        return value


class ArtifactRecord(BaseModel):
    path: str
    exists: bool
    sha256: str | None = None
    size_bytes: int | None = None


class GraderResult(BaseModel):
    passed: bool
    score: float
    issues: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class TrialResult(BaseModel):
    task_id: str
    passed: bool
    score: float
    issues: list[str] = Field(default_factory=list)
    artifacts: list[ArtifactRecord] = Field(default_factory=list)
    trace_path: str
    workspace_path: str
