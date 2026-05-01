from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class RunStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                create table if not exists trials (
                    id integer primary key autoincrement,
                    task_id text not null,
                    passed integer not null,
                    score real not null,
                    payload text not null
                )
                """
            )

    def insert_trial(self, trial: dict[str, Any]) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "insert into trials (task_id, passed, score, payload) values (?, ?, ?, ?)",
                (trial["task_id"], int(bool(trial["passed"])), float(trial["score"]), json.dumps(trial, sort_keys=True)),
            )
            return int(cursor.lastrowid)

    def list_trials(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("select payload from trials order by id").fetchall()
        trials = [json.loads(row["payload"]) for row in rows]
        for trial in trials:
            trial["passed"] = bool(trial["passed"])
        return trials
