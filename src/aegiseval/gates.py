from __future__ import annotations

from pydantic import BaseModel, Field


class GateConfig(BaseModel):
    max_pass_rate_drop: float = 0.05
    max_flake_tasks: int = 0


class GateResult(BaseModel):
    passed: bool
    issues: list[str] = Field(default_factory=list)


def evaluate_gate(baseline: dict, candidate: dict, config: GateConfig) -> GateResult:
    issues: list[str] = []
    baseline_pass = float(baseline.get("pass_rate", 0.0))
    candidate_pass = float(candidate.get("pass_rate", 0.0))
    drop = baseline_pass - candidate_pass
    if drop > config.max_pass_rate_drop:
        issues.append(f"pass_rate dropped by {drop:.3f}, threshold {config.max_pass_rate_drop:.3f}")
    flakes = list(candidate.get("flake_tasks", []))
    if len(flakes) > config.max_flake_tasks:
        issues.append(f"flake task count {len(flakes)} exceeds threshold {config.max_flake_tasks}: {flakes}")
    return GateResult(passed=not issues, issues=issues)
