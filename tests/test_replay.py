from pathlib import Path

from typer.testing import CliRunner

from aegiseval.cli import app
from aegiseval.replay import load_replay
from aegiseval.runner import run_task


def test_load_replay_summarizes_result_trace_and_artifacts(tmp_path: Path):
    run_task(Path("tasks/doc_synthesis_001"), agent_name="dummy", out_dir=tmp_path / "run")

    replay = load_replay(tmp_path / "run")

    assert replay["task_id"] == "doc_synthesis_001"
    assert replay["score"] == 1.0
    assert replay["events"][0]["event"] == "trial_started"
    assert replay["artifacts"][0]["path"] == "final.md"


def test_cli_replay_prints_run_summary(tmp_path: Path):
    run_task(Path("tasks/doc_synthesis_001"), agent_name="dummy", out_dir=tmp_path / "run")

    result = CliRunner().invoke(app, ["replay", str(tmp_path / "run")])

    assert result.exit_code == 0, result.output
    assert "doc_synthesis_001" in result.output
    assert "trial_started" in result.output
    assert "final.md" in result.output
