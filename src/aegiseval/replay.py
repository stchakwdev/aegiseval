from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_replay(run_dir: Path) -> dict[str, Any]:
    result_path = run_dir / "result.json"
    trace_path = run_dir / "trace.jsonl"
    if not result_path.exists():
        raise FileNotFoundError(f"missing result.json: {result_path}")
    if not trace_path.exists():
        raise FileNotFoundError(f"missing trace.jsonl: {trace_path}")

    result = json.loads(result_path.read_text(encoding="utf-8"))
    events = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {
        "run_dir": str(run_dir),
        "task_id": result["task_id"],
        "passed": result["passed"],
        "score": result["score"],
        "issues": result.get("issues", []),
        "artifacts": result.get("artifacts", []),
        "events": events,
    }
