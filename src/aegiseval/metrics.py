from __future__ import annotations

from collections import defaultdict
from typing import Any


def pass_at_k(outcomes: list[bool], k: int) -> float:
    if not outcomes:
        return 0.0
    return sum(1 for value in outcomes if value) / len(outcomes)


def pass_power_k(outcomes: list[bool], k: int) -> float:
    if not outcomes or k <= 0:
        return 0.0
    windows = [outcomes[index : index + k] for index in range(0, len(outcomes), k)]
    complete_windows = [window for window in windows if len(window) == k]
    if not complete_windows:
        return 0.0
    return sum(1 for window in complete_windows if all(window)) / len(complete_windows)


def summarize_trials(trials: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = [bool(trial["passed"]) for trial in trials]
    by_task: dict[str, list[bool]] = defaultdict(list)
    for trial in trials:
        by_task[str(trial["task_id"])].append(bool(trial["passed"]))
    flake_tasks = sorted(task_id for task_id, task_outcomes in by_task.items() if len(set(task_outcomes)) > 1)
    return {
        "total_trials": len(trials),
        "pass_rate": pass_at_k(outcomes, 1),
        "pass_at_1": pass_at_k(outcomes, 1),
        "pass_power_2": pass_power_k(outcomes, 2),
        "flake_tasks": flake_tasks,
    }
