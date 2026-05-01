from pathlib import Path

from aegiseval.store import RunStore


def test_run_store_inserts_and_lists_trials(tmp_path: Path):
    store = RunStore(tmp_path / "runs.db")
    store.insert_trial({"task_id": "task", "passed": True, "score": 1.0, "issues": []})

    trials = store.list_trials()

    assert len(trials) == 1
    assert trials[0]["task_id"] == "task"
    assert trials[0]["passed"] is True
