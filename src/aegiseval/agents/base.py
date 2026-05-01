from __future__ import annotations

from pathlib import Path
from typing import Protocol

from aegiseval.schema import TaskSpec
from aegiseval.traces import TraceWriter


class Agent(Protocol):
    def run(self, task: TaskSpec, workspace: Path, trace: TraceWriter) -> None: ...
