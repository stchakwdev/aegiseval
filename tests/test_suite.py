import json
from pathlib import Path

from typer.testing import CliRunner

from aegiseval.cli import app
from aegiseval.suite import run_suite


def test_run_suite_runs_multiple_tasks_and_trials(tmp_path: Path):
    result = run_suite(
        task_dirs=[Path("tasks/doc_synthesis_001"), Path("tasks/data_analysis_001")],
        agent_name="dummy",
        trials=2,
        out_dir=tmp_path / "suite",
    )

    assert result["summary"]["total_trials"] == 4
    assert result["summary"]["pass_rate"] == 1.0
    assert (tmp_path / "suite" / "suite_result.json").exists()
    assert (tmp_path / "suite" / "trials" / "doc_synthesis_001" / "trial-001" / "result.json").exists()


def test_cli_suite_writes_static_html_report(tmp_path: Path):
    out = tmp_path / "suite"
    result = CliRunner().invoke(
        app,
        [
            "suite",
            "tasks/doc_synthesis_001",
            "tasks/data_analysis_001",
            "--trials",
            "1",
            "--agent",
            "dummy",
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0, result.output
    summary = json.loads((out / "suite_result.json").read_text(encoding="utf-8"))
    assert summary["summary"]["total_trials"] == 2
    html = (out / "report.html").read_text(encoding="utf-8")
    assert "AegisEval Suite Report" in html
    assert "doc_synthesis_001" in html
    assert "data_analysis_001" in html
    assert "trace.html" in html
    assert (out / "trials" / "doc_synthesis_001" / "trial-001" / "trace.html").exists()
