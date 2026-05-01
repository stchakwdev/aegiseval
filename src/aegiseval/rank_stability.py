from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def compare_rankings(suite_paths: list[Path]) -> dict[str, Any]:
    models: dict[str, dict[str, Any]] = {}
    for path in suite_paths:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        model = str(data.get("model") or data.get("agent") or Path(path).parent.name)
        trials = data.get("trials", [])
        code_scores = [float(trial.get("score", 0.0)) for trial in trials]
        hybrid_scores = [float(trial.get("hybrid_score", _hybrid_from_trial(trial))) for trial in trials]
        disagreements = sum(1 for trial in trials if _disagrees(trial))
        models[model] = {
            "code_avg": round(sum(code_scores) / len(code_scores), 4) if code_scores else 0.0,
            "hybrid_avg": round(sum(hybrid_scores) / len(hybrid_scores), 4) if hybrid_scores else 0.0,
            "total_trials": len(trials),
            "code_judge_disagreements": disagreements,
        }
    code_ranking = _rank(models, "code_avg")
    hybrid_ranking = _rank(models, "hybrid_avg")
    return {
        "models": models,
        "code_ranking": code_ranking,
        "hybrid_ranking": hybrid_ranking,
        "rank_changes": _rank_changes(code_ranking, hybrid_ranking),
    }


def _hybrid_from_trial(trial: dict[str, Any]) -> float:
    judge = trial.get("judge") or {}
    judge_score = float(judge.get("score", trial.get("score", 0.0)))
    code_score = float(trial.get("score", 0.0))
    return min(code_score, (0.70 * code_score) + (0.30 * judge_score))


def _disagrees(trial: dict[str, Any]) -> bool:
    judge = trial.get("judge") or {}
    if not judge:
        return False
    code_passed = bool(trial.get("passed"))
    judge_passed = bool(judge.get("passed"))
    return code_passed != judge_passed


def _rank(models: dict[str, dict[str, Any]], key: str) -> list[dict[str, Any]]:
    return [
        {"model": model, key: metrics[key]}
        for model, metrics in sorted(models.items(), key=lambda item: item[1][key], reverse=True)
    ]


def _rank_changes(code_ranking: list[dict[str, Any]], hybrid_ranking: list[dict[str, Any]]) -> list[dict[str, Any]]:
    code_pos = {item["model"]: index + 1 for index, item in enumerate(code_ranking)}
    hybrid_pos = {item["model"]: index + 1 for index, item in enumerate(hybrid_ranking)}
    return [
        {"model": model, "code_rank": code_pos[model], "hybrid_rank": hybrid_pos[model], "delta": code_pos[model] - hybrid_pos[model]}
        for model in code_pos
    ]
