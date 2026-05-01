import json
from pathlib import Path

from aegiseval.traces import TraceWriter


def test_trace_writer_writes_ordered_jsonl_events(tmp_path: Path):
    trace = TraceWriter(tmp_path / "trace.jsonl")
    trace.write("trial_started", {"task_id": "task"})
    trace.write("agent_message", {"content": "hello"})
    trace.write("trial_finished", {"score": 1.0})

    rows = [json.loads(line) for line in (tmp_path / "trace.jsonl").read_text().splitlines()]
    assert [row["seq"] for row in rows] == [1, 2, 3]
    assert [row["event"] for row in rows] == ["trial_started", "agent_message", "trial_finished"]
