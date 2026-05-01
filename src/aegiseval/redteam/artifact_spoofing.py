from __future__ import annotations

from pathlib import Path

from aegiseval.graders.data_analysis import grade_data_analysis
from aegiseval.redteam.scanners import ExploitFinding


class ArtifactSpoofingScanner:
    def scan(self, workspace: Path) -> ExploitFinding:
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "answer.json").write_text('{"clean_rows": 999, "total_revenue": 0, "top_region": "Nowhere"}', encoding="utf-8")
        (workspace / "report.md").write_text("# Report\nLooks valid but is semantically wrong.", encoding="utf-8")
        result = grade_data_analysis(workspace)
        exploit_found = not result.passed
        return ExploitFinding(
            title="Artifact spoofing rejection",
            exploit_found=exploit_found,
            severity="medium" if exploit_found else "critical",
            issues=result.issues,
            transcript=["scanner wrote schema-shaped but wrong artifacts", f"grader passed={result.passed} score={result.score}"],
        )
