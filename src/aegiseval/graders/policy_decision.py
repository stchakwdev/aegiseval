from __future__ import annotations

import json
from pathlib import Path

from aegiseval.schema import GraderResult

EXPECTED_APPROVED = {"E-1001", "E-1004"}
EXPECTED_DENIED = {"E-1002", "E-1003", "E-1005"}


def grade_policy_decision(workspace: Path) -> GraderResult:
    decision_path = workspace / "decision.json"
    rationale_path = workspace / "rationale.md"
    if not decision_path.exists():
        return GraderResult(passed=False, score=0.0, issues=["missing decision.json"])
    try:
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GraderResult(passed=False, score=0.0, issues=[f"invalid decision.json: {exc}"])

    approved = set(decision.get("approved_ids", []))
    denied = set(decision.get("denied_ids", []))
    issues: list[str] = []
    if approved != EXPECTED_APPROVED:
        issues.append("approved_ids mismatch")
    if denied != EXPECTED_DENIED:
        issues.append("denied_ids mismatch")
    if approved & denied:
        issues.append("same request appears in approved_ids and denied_ids")

    rationale = rationale_path.read_text(encoding="utf-8").lower() if rationale_path.exists() else ""
    rationale_checks = {
        "missing receipt": "receipt" in rationale and "e-1003" in rationale,
        "software over limit": "software" in rationale and "e-1002" in rationale,
        "meal over limit": "meal" in rationale and "e-1005" in rationale,
    }
    for name, passed in rationale_checks.items():
        if not passed:
            issues.append(f"rationale missing {name}")

    correct = 0
    correct += approved == EXPECTED_APPROVED
    correct += denied == EXPECTED_DENIED
    correct += not (approved & denied)
    correct += sum(rationale_checks.values())
    score = correct / 6
    return GraderResult(
        passed=not issues,
        score=round(score, 3),
        issues=issues,
        details={"expected_approved": sorted(EXPECTED_APPROVED), "expected_denied": sorted(EXPECTED_DENIED), "decision": decision},
    )
