from aegiseval.gates import GateConfig, evaluate_gate


def test_gate_passes_when_candidate_is_healthy():
    result = evaluate_gate(
        baseline={"pass_rate": 0.7, "flake_tasks": []},
        candidate={"pass_rate": 0.75, "flake_tasks": []},
        config=GateConfig(max_pass_rate_drop=0.05, max_flake_tasks=0),
    )
    assert result.passed is True


def test_gate_fails_on_regression_and_flakes():
    result = evaluate_gate(
        baseline={"pass_rate": 0.8, "flake_tasks": []},
        candidate={"pass_rate": 0.6, "flake_tasks": ["task"]},
        config=GateConfig(max_pass_rate_drop=0.05, max_flake_tasks=0),
    )
    assert result.passed is False
    assert any("pass_rate" in issue for issue in result.issues)
    assert any("flake" in issue for issue in result.issues)
