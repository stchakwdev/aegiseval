from pathlib import Path

from aegiseval.runner import run_task


def test_runner_produces_trace_result_and_artifacts(tmp_path: Path):
    result = run_task(Path("tasks/doc_synthesis_001"), agent_name="dummy", out_dir=tmp_path / "run")

    assert result.passed is True
    assert (tmp_path / "run" / "trace.jsonl").exists()
    assert (tmp_path / "run" / "result.json").exists()
    assert (tmp_path / "run" / "workspace" / "final.md").exists()
