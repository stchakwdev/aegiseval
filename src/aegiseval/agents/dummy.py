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
        elif task.domain == "contradiction_review":
            self._solve_contradiction(workspace, trace)
        elif task.domain == "policy_decision":
            self._solve_policy(workspace, trace)
        elif task.domain == "incident_analysis":
            self._solve_incident(workspace, trace)
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

    def _solve_contradiction(self, workspace: Path, trace: TraceWriter) -> None:
        (workspace / "final.md").write_text(
            "# Atlas release review\n\n"
            "The central contradiction is that aggregate user/product metrics improved, including an 18% mean task-time improvement "
            "and 91% positive analyst survey response [product_summary.md], but reliability regressed: p95 latency moved "
            "from 210 ms to 480 ms during peak traffic [reliability_review.md].\n\n"
            "Release should not proceed until p95 latency is below the 250 ms reliability threshold and timeout retries are controlled.\n",
            encoding="utf-8",
        )
        trace.write("artifact_written", {"path": "final.md"})

    def _solve_policy(self, workspace: Path, trace: TraceWriter) -> None:
        decision = {"approved_ids": ["E-1001", "E-1004"], "denied_ids": ["E-1002", "E-1003", "E-1005"]}
        (workspace / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
        (workspace / "rationale.md").write_text(
            "# Reimbursement decisions\n\n"
            "E-1002 is denied because the software request exceeds the policy limit without sufficient finance approval.\n"
            "E-1003 is denied because the transit request is missing a receipt.\n"
            "E-1005 is denied because the meal request exceeds the 80 CAD meal limit.\n",
            encoding="utf-8",
        )
        trace.write("artifact_written", {"path": "decision.json"})
        trace.write("artifact_written", {"path": "rationale.md"})

    def _solve_incident(self, workspace: Path, trace: TraceWriter) -> None:
        incident = {
            "root_cause": "cache invalidation job evicted the hot policy index after a malformed deploy flag",
            "highest_severity": "sev1",
            "customer_impact_minutes": 47,
            "followups": ["add circuit breaker around cache invalidation job", "block malformed deploy flags in CI"],
        }
        (workspace / "incident.json").write_text(json.dumps(incident, indent=2), encoding="utf-8")
        (workspace / "postmortem.md").write_text(
            "# Incident postmortem\n\n"
            "- 02:18Z: customer-visible timeouts began.\n"
            "- 02:24Z: cache invalidation evicted the hot policy index after a malformed deploy flag.\n"
            "- 03:05Z: customer-visible timeouts resolved after manual cache warmup.\n",
            encoding="utf-8",
        )
        trace.write("artifact_written", {"path": "incident.json"})
        trace.write("artifact_written", {"path": "postmortem.md"})
