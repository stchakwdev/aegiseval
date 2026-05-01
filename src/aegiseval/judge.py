from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from aegiseval.agents.openai_compatible import _loads_json_object
from aegiseval.schema import GraderResult, TaskSpec


class JudgeDimension(BaseModel):
    score: float
    rationale: str = ""


class JudgeResult(BaseModel):
    score: float
    passed: bool
    dimensions: dict[str, Any] = Field(default_factory=dict)
    critical_failures: list[str] = Field(default_factory=list)
    summary: str = ""


def apply_hybrid_score(
    code_passed: bool,
    code_score: float,
    code_issues: list[str],
    judge: JudgeResult,
    judge_threshold: float = 0.70,
) -> GraderResult:
    blended = round((0.70 * code_score) + (0.30 * judge.score), 3)
    final_score = min(round(code_score, 3), blended)
    issues = list(code_issues)
    if judge.score < judge_threshold:
        issues.append("judge below threshold")
    for failure in judge.critical_failures:
        issues.append(f"judge critical failure: {failure}")
    passed = bool(code_passed and judge.score >= judge_threshold and not judge.critical_failures)
    return GraderResult(
        passed=passed,
        score=final_score,
        issues=issues,
        details={
            "code_score": code_score,
            "code_passed": code_passed,
            "judge": judge.model_dump(),
            "hybrid_formula": "min(code_score, 0.70 * code_score + 0.30 * judge_score)",
        },
    )


def judge_with_openai_compatible(
    task: TaskSpec,
    workspace: Path,
    code_result: GraderResult,
    model: str,
    base_url: str,
    api_key_env: str,
    timeout: int = 120,
) -> JudgeResult:
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError(f"missing judge API key environment variable: {api_key_env}")
    prompt = _build_judge_prompt(task, workspace, code_result)
    payload = {
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict evaluator for realistic business knowledge-work artifacts. "
                    "Return ONLY JSON with keys: score, passed, dimensions, critical_failures, summary. "
                    "Score from 0 to 1. Do not reward generic writing or unsupported claims."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json", "authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - user-configured judge endpoint
        body = json.loads(response.read().decode("utf-8"))
    content = str(body["choices"][0]["message"].get("content") or "")
    return JudgeResult.model_validate(_loads_json_object(content))


def _build_judge_prompt(task: TaskSpec, workspace: Path, code_result: GraderResult) -> str:
    artifact_sections = []
    for artifact in task.expected_artifacts:
        path = workspace / artifact.path
        text = path.read_text(encoding="utf-8", errors="replace")[:3000] if path.exists() else "<missing>"
        artifact_sections.append(f"--- {artifact.path} ---\n{text}")
    return (
        f"Task id: {task.id}\n"
        f"Instruction: {task.instruction}\n\n"
        f"Code grader passed: {code_result.passed}\n"
        f"Code grader score: {code_result.score}\n"
        f"Code grader issues: {code_result.issues}\n\n"
        "Judge dimensions: factuality, completeness, decision_usefulness, specificity, risk_awareness, format_following, professional_tone.\n"
        "Critical failures include fabricated evidence, missing required artifact, unsafe recommendation, or unsupported numeric claim.\n\n"
        "Artifacts:\n"
        + "\n\n".join(artifact_sections)
    )


def local_judge_from_code_result(code_result: GraderResult) -> JudgeResult:
    """Deterministic fallback judge for offline tests and cheap comparison runs.

    It is intentionally conservative: objective failures lower the subjective score,
    but it does not invent qualitative praise. Live-model judging can be layered on
    later using the same JudgeResult schema.
    """
    score = max(0.0, min(1.0, code_result.score - 0.05 * len(code_result.issues)))
    critical_failures = [issue for issue in code_result.issues if "fabricated" in issue or "missing" in issue]
    return JudgeResult(
        score=round(score, 3),
        passed=score >= 0.70 and not critical_failures,
        dimensions={
            "factuality": {"score": round(score, 3), "rationale": "derived from deterministic artifact checks"},
            "decision_usefulness": {"score": round(score, 3), "rationale": "offline proxy; use live judge for subjective review"},
        },
        critical_failures=critical_failures,
        summary="local deterministic judge proxy",
    )
