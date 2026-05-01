from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from aegiseval.schema import TaskSpec
from aegiseval.traces import TraceWriter


class DummyAgent:
    """Deterministic scripted agent for smoke tests and harness verification."""

    def run(self, task: TaskSpec, workspace: Path, trace: TraceWriter) -> None:
        trace.write("agent_message", {"agent": "dummy", "content": f"Solving {task.id}"})
        if task.domain == "document_synthesis":
            self._solve_doc(workspace, trace)
        elif task.domain == "data_analysis":
            self._solve_data(workspace, trace)
        else:
            raise ValueError(f"dummy agent does not support domain: {task.domain}")

    def _solve_doc(self, workspace: Path, trace: TraceWriter) -> None:
        final = workspace / "final.md"
        final.write_text(
            "# Project Aurora memo\n\n"
            "Project Aurora reduced search time by 35% [memo_a.md]. "
            "The key rollout risk is fabricated citations [memo_b.md].\n",
            encoding="utf-8",
        )
        trace.write("artifact_written", {"path": "final.md"})

    def _solve_data(self, workspace: Path, trace: TraceWriter) -> None:
        data_path = workspace / "data.csv"
        totals: dict[str, float] = defaultdict(float)
        clean_rows = 0
        with data_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                try:
                    revenue = float(row["revenue"])
                except (KeyError, ValueError):
                    continue
                if revenue < 0 or not row.get("region"):
                    continue
                clean_rows += 1
                totals[row["region"]] += revenue
        top_region = max(totals.items(), key=lambda item: item[1])[0]
        total_revenue = sum(totals.values())
        (workspace / "answer.json").write_text(
            json.dumps({"clean_rows": clean_rows, "total_revenue": total_revenue, "top_region": top_region}, indent=2),
            encoding="utf-8",
        )
        (workspace / "report.md").write_text(
            f"# Revenue report\n\n{top_region} leads revenue after cleaning invalid rows. Total revenue: {total_revenue}.\n",
            encoding="utf-8",
        )
        trace.write("artifact_written", {"path": "answer.json"})
        trace.write("artifact_written", {"path": "report.md"})
