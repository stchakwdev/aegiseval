from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from aegiseval.metrics import summarize_trials

console = Console()


def load_result(run_dir: Path) -> dict:
    return json.loads((run_dir / "result.json").read_text(encoding="utf-8"))


def render_report(run_dir: Path) -> dict:
    result = load_result(run_dir)
    summary = summarize_trials([result])
    table = Table(title=f"AegisEval Report: {run_dir}")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("task_id", str(result["task_id"]))
    table.add_row("passed", str(result["passed"]))
    table.add_row("score", str(result["score"]))
    table.add_row("issues", "; ".join(result.get("issues", [])) or "none")
    table.add_row("pass_rate", str(summary["pass_rate"]))
    console.print(table)
    return summary
