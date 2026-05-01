from __future__ import annotations

import json
from pathlib import Path

from aegiseval.schema import GraderResult


def grade_incident_analysis(workspace: Path) -> GraderResult:
    incident_path = workspace / "incident.json"
    postmortem_path = workspace / "postmortem.md"
    if not incident_path.exists():
        return GraderResult(passed=False, score=0.0, issues=["missing incident.json"])
    try:
        incident = json.loads(incident_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GraderResult(passed=False, score=0.0, issues=[f"invalid incident.json: {exc}"])

    issues: list[str] = []
    checks = {
        "root_cause": "cache invalidation" in str(incident.get("root_cause", "")).lower(),
        "highest_severity": str(incident.get("highest_severity", "")).lower() == "sev1",
        "customer_impact_minutes": incident.get("customer_impact_minutes") == 47,
        "followups": any("circuit breaker" in str(item).lower() for item in incident.get("followups", [])),
    }
    for name, passed in checks.items():
        if not passed:
            issues.append(f"{name} mismatch")

    postmortem = postmortem_path.read_text(encoding="utf-8").lower() if postmortem_path.exists() else ""
    timeline_ok = "02:18" in postmortem and "03:05" in postmortem and "02:24" in postmortem
    if not timeline_ok:
        issues.append("postmortem missing key timeline entries")

    correct = sum(checks.values()) + int(timeline_ok)
    score = correct / 5
    return GraderResult(passed=not issues, score=round(score, 3), issues=issues, details={"checks": checks, "incident": incident})
