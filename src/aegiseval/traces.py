from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class TraceWriter:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._seq = 0
        self.path.write_text("", encoding="utf-8")

    def write(self, event: str, payload: dict[str, Any]) -> None:
        self._seq += 1
        row = {
            "seq": self._seq,
            "ts": datetime.now(UTC).isoformat(),
            "event": event,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
