import json
import sys
from pathlib import Path

import pytest

from aegiseval.runner import run_task
from aegiseval.suite import write_trace_html


def test_failed_agent_run_writes_result_and_trace_html(tmp_path: Path):
    failing_agent = tmp_path / "fail_agent.py"
    failing_agent.write_text("import sys\nsys.stderr.write('boom')\nsys.exit(7)\n", encoding="utf-8")
    out = tmp_path / "run"

    with pytest.raises(RuntimeError):
        run_task(
            Path("tasks/doc_synthesis_001"),
            agent_name="subprocess",
            out_dir=out,
            agent_command=f"{sys.executable} {failing_agent}",
        )

    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["passed"] is False
    assert result["score"] == 0.0
    assert "agent failed" in result["issues"][0]
    trace = (out / "trace.jsonl").read_text(encoding="utf-8")
    assert "trial_failed" in trace

    write_trace_html(out / "trace.html", out)
    html = (out / "trace.html").read_text(encoding="utf-8")
    assert "trial_failed" in html
