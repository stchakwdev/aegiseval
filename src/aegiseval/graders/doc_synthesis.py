from __future__ import annotations

import re
from pathlib import Path

from aegiseval.schema import GraderResult

REQUIRED_CLAIMS = [
    "reduced search time by 35%",
    "fabricated citations",
]
CITATION_RE = re.compile(r"\[([^\[\]]+\.md)\]")


def grade_doc_synthesis(workspace: Path) -> GraderResult:
    final = workspace / "final.md"
    issues: list[str] = []
    if not final.exists():
        return GraderResult(passed=False, score=0.0, issues=["missing final.md"])

    text = final.read_text(encoding="utf-8")
    lowered = text.lower()
    for claim in REQUIRED_CLAIMS:
        if claim.lower() not in lowered:
            issues.append(f"missing required claim: {claim}")

    citations = CITATION_RE.findall(text)
    if not citations:
        issues.append("missing citations")
    for citation in citations:
        if not (workspace / "sources" / citation).exists():
            issues.append(f"fabricated or unresolved citation: {citation}")

    score_parts = 0
    score_parts += sum(1 for claim in REQUIRED_CLAIMS if claim.lower() in lowered)
    score_parts += 1 if citations and not any("citation" in issue for issue in issues) else 0
    score = score_parts / (len(REQUIRED_CLAIMS) + 1)
    return GraderResult(passed=not issues, score=round(score, 3), issues=issues, details={"citations": citations})
