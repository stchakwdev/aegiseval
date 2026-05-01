import json
from pathlib import Path

from aegiseval.graders.data_analysis import grade_data_analysis


def test_data_analysis_grader_accepts_correct_numeric_answer(tmp_path: Path):
    (tmp_path / "answer.json").write_text(json.dumps({"clean_rows": 4, "total_revenue": 750.0, "top_region": "North"}), encoding="utf-8")
    (tmp_path / "report.md").write_text("# Report\nNorth leads revenue after cleaning invalid rows.", encoding="utf-8")

    result = grade_data_analysis(tmp_path)

    assert result.passed is True
    assert result.score == 1.0


def test_data_analysis_grader_rejects_wrong_answer(tmp_path: Path):
    (tmp_path / "answer.json").write_text(json.dumps({"clean_rows": 1, "total_revenue": 10, "top_region": "South"}), encoding="utf-8")
    (tmp_path / "report.md").write_text("# Report\nWrong.", encoding="utf-8")

    result = grade_data_analysis(tmp_path)

    assert result.passed is False
    assert result.score < 1.0
    assert result.issues
