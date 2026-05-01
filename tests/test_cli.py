from pathlib import Path

from typer.testing import CliRunner

from aegiseval.cli import app


def test_cli_version():
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert "aegiseval" in result.stdout


def test_cli_can_run_dummy_doc_task(tmp_path: Path):
    out = tmp_path / "run"
    result = CliRunner().invoke(app, ["run", "tasks/doc_synthesis_001", "--agent", "dummy", "--out", str(out)])
    assert result.exit_code == 0, result.output
    assert (out / "trace.jsonl").exists()
    assert (out / "result.json").exists()
