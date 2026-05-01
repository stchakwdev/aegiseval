from __future__ import annotations

from pathlib import Path

from aegiseval.graders.contradiction_review import grade_contradiction_review
from aegiseval.graders.data_analysis import grade_data_analysis
from aegiseval.graders.doc_synthesis import grade_doc_synthesis
from aegiseval.graders.incident_analysis import grade_incident_analysis
from aegiseval.graders.policy_decision import grade_policy_decision
from aegiseval.schema import GraderResult, TaskSpec

GRADERS = {
    "contradiction_review": grade_contradiction_review,
    "data_analysis": grade_data_analysis,
    "doc_synthesis": grade_doc_synthesis,
    "incident_analysis": grade_incident_analysis,
    "policy_decision": grade_policy_decision,
}


def grade(task: TaskSpec, workspace: Path) -> GraderResult:
    try:
        grader = GRADERS[task.grader.name]
    except KeyError as exc:
        raise ValueError(f"unknown grader: {task.grader.name}") from exc
    return grader(workspace)
