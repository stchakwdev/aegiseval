import sys
from pathlib import Path

from aegiseval.runner import run_task


def test_subprocess_agent_runs_command_in_workspace(tmp_path: Path):
    script = tmp_path / "solve_doc.py"
    script.write_text(
        "from pathlib import Path\n"
        "Path('final.md').write_text('Project Aurora reduced search time by 35% [memo_a.md]. The key rollout risk is fabricated citations [memo_b.md].', encoding='utf-8')\n",
        encoding="utf-8",
    )

    result = run_task(
        Path("tasks/doc_synthesis_001"),
        agent_name="subprocess",
        out_dir=tmp_path / "run",
        agent_command=f"{sys.executable} {script}",
    )

    assert result.passed is True
    trace = (tmp_path / "run" / "trace.jsonl").read_text(encoding="utf-8")
    assert "subprocess_started" in trace
    assert "subprocess_finished" in trace
