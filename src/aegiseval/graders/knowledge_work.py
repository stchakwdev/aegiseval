from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from aegiseval.schema import GraderResult, TaskSpec


def grade_knowledge_work(task: TaskSpec, workspace: Path) -> GraderResult:
    checks = task.grader.config.get("checks", {})
    issues: list[str] = []
    passed_parts = 0
    total_parts = 0

    for artifact in task.expected_artifacts:
        total_parts += 1
        path = workspace / artifact.path
        if not path.exists():
            issues.append(f"missing {artifact.path}")
            continue
        passed_parts += 1

    for path, spec in checks.get("markdown", {}).items():
        text = _read_text(workspace / path)
        lowered = text.lower()
        for phrase in spec.get("required_phrases", []):
            total_parts += 1
            if phrase.lower() in lowered:
                passed_parts += 1
            else:
                issues.append(f"{path} missing phrase: {phrase}")
        for phrase in spec.get("forbidden_phrases", []):
            total_parts += 1
            if phrase.lower() not in lowered:
                passed_parts += 1
            else:
                issues.append(f"{path} contains forbidden phrase: {phrase}")

    for path, spec in checks.get("json", {}).items():
        payload = _read_json(workspace / path, issues, path)
        if payload is None:
            continue
        for key, expected in spec.get("equals", {}).items():
            total_parts += 1
            actual = _get_path(payload, key)
            if actual == expected:
                passed_parts += 1
            else:
                issues.append(f"{path} {key} mismatch: expected {expected!r}, got {actual!r}")
        for key, expected_values in spec.get("contains", {}).items():
            actual = _get_path(payload, key)
            actual_values = actual if isinstance(actual, list) else []
            for expected in expected_values:
                total_parts += 1
                if expected in actual_values:
                    passed_parts += 1
                else:
                    issues.append(f"{path} {key} missing value: {expected!r}")

    for path, spec in checks.get("csv", {}).items():
        rows = _read_csv(workspace / path, issues, path)
        if rows is None:
            continue
        if "row_count" in spec:
            total_parts += 1
            if len(rows) == spec["row_count"]:
                passed_parts += 1
            else:
                issues.append(f"{path} row_count mismatch: expected {spec['row_count']}, got {len(rows)}")
        for required in spec.get("required_rows", []):
            total_parts += 1
            if any(all(str(row.get(k, "")) == str(v) for k, v in required.items()) for row in rows):
                passed_parts += 1
            else:
                issues.append(f"{path} missing row: {required}")

    score = round(passed_parts / total_parts, 3) if total_parts else 0.0
    return GraderResult(passed=not issues, score=score, issues=issues, details={"passed_parts": passed_parts, "total_parts": total_parts})


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _read_json(path: Path, issues: list[str], label: str) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(f"invalid {label}: {exc}")
        return None


def _read_csv(path: Path, issues: list[str], label: str) -> list[dict[str, str]] | None:
    if not path.exists():
        return None
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except csv.Error as exc:
        issues.append(f"invalid {label}: {exc}")
        return None


def _get_path(payload: Any, path: str) -> Any:
    current = payload
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current
