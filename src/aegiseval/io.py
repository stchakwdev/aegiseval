from __future__ import annotations

import json
from pathlib import Path

import yaml

from aegiseval.schema import TaskSpec


def load_task(task_dir: Path) -> TaskSpec:
    spec_path = task_dir / "task.yaml"
    if not spec_path.exists():
        raise FileNotFoundError(f"task spec not found: {spec_path}")
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    return TaskSpec.model_validate(data)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
