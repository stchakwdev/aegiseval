from pathlib import Path

from aegiseval.runner import run_task


def test_dummy_agent_passes_harder_contradiction_task(tmp_path: Path):
    result = run_task(Path("tasks/contradiction_review_001"), "dummy", tmp_path / "contradiction")

    assert result.passed is True
    assert result.score == 1.0


def test_dummy_agent_passes_harder_policy_task(tmp_path: Path):
    result = run_task(Path("tasks/policy_decision_001"), "dummy", tmp_path / "policy")

    assert result.passed is True
    assert result.score == 1.0


def test_dummy_agent_passes_harder_incident_task(tmp_path: Path):
    result = run_task(Path("tasks/incident_analysis_001"), "dummy", tmp_path / "incident")

    assert result.passed is True
    assert result.score == 1.0
