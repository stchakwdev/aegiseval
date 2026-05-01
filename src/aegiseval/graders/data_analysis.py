from __future__ import annotations

import json
from pathlib import Path

from aegiseval.schema import GraderResult

EXPECTED = {"clean_rows": 4, "total_revenue": 750.0, "top_region": "North"}


def grade_data_analysis(workspace: Path) -> GraderResult:
    answer_path = workspace / "answer.json"
    report_path = workspace / "report.md"
    issues: list[str] = []
    if not answer_path.exists():
        return GraderResult(passed=False, score=0.0, issues=["missing answer.json"])
    try:
        answer = json.loads(answer_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GraderResult(passed=False, score=0.0, issues=[f"invalid answer.json: {exc}"])

    correct = 0
    if answer.get("clean_rows") == EXPECTED["clean_rows"]:
        correct += 1
    else:
        issues.append("clean_rows mismatch")
    if abs(float(answer.get("total_revenue", -1)) - EXPECTED["total_revenue"]) < 1e-6:
        correct += 1
    else:
        issues.append("total_revenue mismatch")
    if answer.get("top_region") == EXPECTED["top_region"]:
        correct += 1
    else:
        issues.append("top_region mismatch")
    if report_path.exists() and "North" in report_path.read_text(encoding="utf-8"):
        correct += 1
    else:
        issues.append("report missing North explanation")

    score = correct / 4
    return GraderResult(passed=not issues, score=round(score, 3), issues=issues, details={"expected": EXPECTED, "answer": answer})
