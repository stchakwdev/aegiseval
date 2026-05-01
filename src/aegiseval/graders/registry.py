from __future__ import annotations

from pathlib import Path

from aegiseval.graders.data_analysis import grade_data_analysis
from aegiseval.graders.doc_synthesis import grade_doc_synthesis
from aegiseval.schema import GraderResult, TaskSpec


def grade(task: TaskSpec, workspace: Path) -> GraderResult:
    if task.grader.name == "doc_synthesis":
        return grade_doc_synthesis(workspace)
    if task.grader.name == "data_analysis":
        return grade_data_analysis(workspace)
    raise ValueError(f"unknown grader: {task.grader.name}")
