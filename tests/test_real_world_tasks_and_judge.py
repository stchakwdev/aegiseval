from __future__ import annotations

import json
import shutil
from pathlib import Path

from aegiseval.graders.registry import grade
from aegiseval.io import load_task
from aegiseval.judge import JudgeResult, apply_hybrid_score
from aegiseval.rank_stability import compare_rankings

REAL_WORLD_TASKS = [
    "market_research_brief_001",
    "lead_list_enrichment_001",
    "executive_inbox_triage_001",
    "seo_competitor_audit_001",
    "survey_analysis_report_001",
    "procurement_quote_comparison_001",
    "policy_update_diff_001",
    "customer_feedback_synthesis_001",
    "real_estate_comp_report_001",
    "import_export_brief_001",
]


def test_real_world_task_corpus_exists_and_uses_hybrid_grading():
    for task_id in REAL_WORLD_TASKS:
        task_dir = Path("tasks") / task_id
        task = load_task(task_dir)
        assert task.id == task_id
        assert task.grader.kind == "hybrid"
        assert task.grader.name == "knowledge_work"
        assert (task_dir / "expected_outputs").exists()
        assert len(task.expected_artifacts) >= 2


def test_real_world_gold_outputs_pass_code_grader(tmp_path: Path):
    for task_id in REAL_WORLD_TASKS:
        task_dir = Path("tasks") / task_id
        task = load_task(task_dir)
        workspace = tmp_path / task_id
        shutil.copytree(task_dir / "fixtures", workspace)
        expected_dir = task_dir / "expected_outputs"
        for artifact in task.expected_artifacts:
            source = expected_dir / artifact.path
            target = workspace / artifact.path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        result = grade(task, workspace)
        assert result.passed, (task_id, result.issues)
        assert result.score == 1.0


def test_hybrid_score_caps_judge_boost_when_code_score_is_low():
    judge = JudgeResult(score=1.0, passed=True, dimensions={}, critical_failures=[], summary="excellent")

    result = apply_hybrid_score(code_passed=False, code_score=0.4, code_issues=["missing artifact"], judge=judge)

    assert result.passed is False
    assert result.score == 0.4
    assert "missing artifact" in result.issues


def test_hybrid_score_requires_judge_threshold_and_no_critical_failures():
    judge = JudgeResult(
        score=0.65,
        passed=True,
        dimensions={},
        critical_failures=["fabricated citation"],
        summary="polished but unsafe",
    )

    result = apply_hybrid_score(code_passed=True, code_score=1.0, code_issues=[], judge=judge)

    assert result.passed is False
    assert result.score == 0.895
    assert "judge below threshold" in result.issues
    assert "judge critical failure: fabricated citation" in result.issues


def test_rank_stability_reports_code_judge_disagreements(tmp_path: Path):
    suite_a = {
        "model": "model-a",
        "trials": [
            {"task_id": "t1", "score": 1.0, "passed": True, "judge": {"score": 0.4, "passed": False}},
            {"task_id": "t2", "score": 0.5, "passed": False, "judge": {"score": 0.9, "passed": True}},
        ],
    }
    suite_b = {
        "model": "model-b",
        "trials": [
            {"task_id": "t1", "score": 0.8, "passed": True, "judge": {"score": 0.8, "passed": True}},
            {"task_id": "t2", "score": 0.8, "passed": True, "judge": {"score": 0.8, "passed": True}},
        ],
    }
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps(suite_a), encoding="utf-8")
    b.write_text(json.dumps(suite_b), encoding="utf-8")

    comparison = compare_rankings([a, b])

    assert comparison["code_ranking"][0]["model"] == "model-b"
    assert comparison["hybrid_ranking"][0]["model"] == "model-b"
    assert comparison["models"]["model-a"]["code_judge_disagreements"] == 2
