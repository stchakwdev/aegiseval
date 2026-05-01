from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

from aegiseval.io import write_json
from aegiseval.schema import TaskSpec
from aegiseval.traces import TraceWriter


class SubprocessAgent:
    def __init__(self, command: str):
        if not command.strip():
            raise ValueError("subprocess agent requires a non-empty command")
        self.command = command

    def run(self, task: TaskSpec, workspace: Path, trace: TraceWriter) -> None:
        write_json(workspace / "task.json", task.model_dump())
        env = os.environ.copy()
        env.update(
            {
                "AEGISEVAL_TASK_ID": task.id,
                "AEGISEVAL_TASK_INSTRUCTION": task.instruction,
                "AEGISEVAL_WORKSPACE": str(workspace),
            }
        )
        trace.write("subprocess_started", {"command": self.command})
        completed = subprocess.run(
            shlex.split(self.command),
            cwd=workspace,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        trace.write(
            "subprocess_finished",
            {
                "returncode": completed.returncode,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
            },
        )
        if completed.returncode != 0:
            raise RuntimeError(f"subprocess agent failed with exit code {completed.returncode}: {completed.stderr}")
