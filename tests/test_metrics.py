from aegiseval.metrics import pass_at_k, pass_power_k, summarize_trials


def test_pass_metrics():
    outcomes = [True, False, True, True]
    assert pass_at_k(outcomes, 1) == 0.75
    assert pass_power_k(outcomes, 2) == 0.5


def test_summarize_trials_detects_flake():
    summary = summarize_trials([
        {"task_id": "task", "passed": True, "score": 1.0},
        {"task_id": "task", "passed": False, "score": 0.2},
    ])

    assert summary["total_trials"] == 2
    assert summary["pass_rate"] == 0.5
    assert summary["flake_tasks"] == ["task"]
