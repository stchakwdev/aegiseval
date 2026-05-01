from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aegiseval.io import write_json
from aegiseval.replay import load_replay

PASS = "pass"
WARN = "warn"
FAIL = "fail"


def audit_suite_dir(suite_dir: Path, sample_count: int = 3) -> dict[str, Any]:
    suite_path = suite_dir / "suite_result.json"
    if not suite_path.exists():
        raise FileNotFoundError(f"missing suite_result.json: {suite_path}")
    suite_result = json.loads(suite_path.read_text(encoding="utf-8"))
    return build_eval_audit(suite_result, suite_dir=suite_dir, sample_count=sample_count)


def build_eval_audit(suite_result: dict[str, Any], suite_dir: Path, sample_count: int = 3) -> dict[str, Any]:
    """Build an Anthropic-inspired eval-quality audit for a suite run.

    The audit is intentionally small and inspectable. It checks for the properties
    emphasized in Anthropic's public writing on agent evals: repeated trials,
    outcome-based grading, replayable transcripts/traces, environment artifacts,
    flake visibility, and a concrete transcript review queue for humans.
    """
    trials = suite_result.get("trials", [])
    replays = [_safe_load_replay(Path(trial["run_dir"])) for trial in trials]
    events_by_trial = [[event.get("event") for event in replay.get("events", [])] for replay in replays]

    checks = [
        _check(
            "multi_trial_protocol",
            PASS if suite_result.get("trials_per_task", 0) >= 2 else WARN,
            "Run at least two trials per task before trusting pass-rate changes.",
            {"trials_per_task": suite_result.get("trials_per_task", 0)},
        ),
        _check(
            "outcome_grading_recorded",
            PASS if trials and all("grader_result" in events for events in events_by_trial) else FAIL,
            "Grade final environment artifacts/outcomes, not just agent claims.",
            {"missing": _missing_event_trials(trials, events_by_trial, "grader_result")},
        ),
        _check(
            "trace_lifecycle_complete",
            PASS if trials and all({"trial_started", "trial_finished"}.issubset(set(events)) for events in events_by_trial) else FAIL,
            "Every trial should have a complete start/finish lifecycle in its trace.",
            {"missing": _missing_lifecycle_trials(trials, events_by_trial)},
        ),
        _check(
            "artifacts_recorded",
            PASS if trials and all(replay.get("artifacts") for replay in replays) else FAIL,
            "Artifacts must be recorded so humans can inspect final environment state.",
            {"missing": [trial.get("run_dir") for trial, replay in zip(trials, replays, strict=False) if not replay.get("artifacts")]},
        ),
        _check(
            "flake_visibility",
            WARN if suite_result.get("summary", {}).get("flake_tasks") else PASS,
            "Flaky tasks should be explicit because stochastic agent failures compound.",
            {"flake_tasks": suite_result.get("summary", {}).get("flake_tasks", [])},
        ),
        _model_transparency_check(suite_result, trials, events_by_trial),
    ]

    review_queue = _build_review_queue(trials, sample_count=sample_count, suite_dir=suite_dir)
    checks.append(
        _check(
            "human_transcript_review_queue",
            PASS if review_queue else FAIL,
            "Keep a small deterministic queue of traces for human reading; scores alone are not enough.",
            {"sample_count": len(review_queue)},
        )
    )

    return {
        "suite_dir": str(suite_dir),
        "agent": suite_result.get("agent"),
        "summary": suite_result.get("summary", {}),
        "checks": checks,
        "review_queue": review_queue,
        "sources": [
            "Anthropic — Demystifying evals for AI agents",
            "Anthropic — Effective harnesses for long-running agents",
            "Anthropic — Building effective AI agents",
            "Anthropic — Challenges in evaluating AI systems",
            "Anthropic — From shortcuts to sabotage: natural emergent misalignment from reward hacking",
            "Anthropic — Petri: An open-source auditing tool to accelerate AI safety research",
        ],
    }


def write_eval_audit(suite_dir: Path, suite_result: dict[str, Any], sample_count: int = 3) -> dict[str, Any]:
    audit = build_eval_audit(suite_result, suite_dir=suite_dir, sample_count=sample_count)
    write_json(suite_dir / "eval_audit.json", audit)
    (suite_dir / "eval_audit.md").write_text(render_eval_audit_markdown(audit), encoding="utf-8")
    return audit


def render_eval_audit_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# AegisEval Eval-Quality Audit",
        "",
        f"Suite: `{audit['suite_dir']}`",
        f"Agent: `{audit.get('agent')}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Why it matters |",
        "| --- | --- | --- |",
    ]
    for check in audit["checks"]:
        lines.append(f"| `{check['name']}` | **{check['status'].upper()}** | {check['message']} |")

    lines.extend(["", "## Human transcript review queue", ""])
    if audit["review_queue"]:
        for item in audit["review_queue"]:
            lines.append(
                f"- `{item['task_id']}` trial `{item['trial_index']}` score `{item['score']}` "
                f"passed `{item['passed']}` — [{item['trace_html']}]({item['trace_html']})"
            )
    else:
        lines.append("No traces available for review.")

    lines.extend(["", "## Source principles", ""])
    for source in audit["sources"]:
        lines.append(f"- {source}")
    lines.append("")
    return "\n".join(lines)


def _safe_load_replay(run_dir: Path) -> dict[str, Any]:
    try:
        return load_replay(run_dir)
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        return {"events": [], "artifacts": [], "error": str(exc)}


def _check(name: str, status: str, message: str, details: dict[str, Any]) -> dict[str, Any]:
    return {"name": name, "status": status, "message": message, "details": details}


def _missing_event_trials(trials: list[dict[str, Any]], events_by_trial: list[list[str]], event_name: str) -> list[str]:
    return [trial.get("run_dir", "") for trial, events in zip(trials, events_by_trial, strict=False) if event_name not in events]


def _missing_lifecycle_trials(trials: list[dict[str, Any]], events_by_trial: list[list[str]]) -> list[str]:
    required = {"trial_started", "trial_finished"}
    return [trial.get("run_dir", "") for trial, events in zip(trials, events_by_trial, strict=False) if not required.issubset(set(events))]


def _model_transparency_check(
    suite_result: dict[str, Any], trials: list[dict[str, Any]], events_by_trial: list[list[str]]
) -> dict[str, Any]:
    agent = suite_result.get("agent")
    if agent not in {"openai-compatible", "anthropic"}:
        return _check(
            "model_call_transparency",
            PASS,
            "No model-backed adapter was used; model request tracing is not required for this suite.",
            {"agent": agent},
        )

    required = {"model_request_started", "model_request_finished"}
    missing = [trial.get("run_dir", "") for trial, events in zip(trials, events_by_trial, strict=False) if not required.issubset(set(events))]
    return _check(
        "model_call_transparency",
        PASS if not missing else FAIL,
        "Model-backed trials should expose request lifecycle events for debugging and incident review.",
        {"missing": missing},
    )


def _build_review_queue(trials: list[dict[str, Any]], sample_count: int, suite_dir: Path) -> list[dict[str, Any]]:
    ranked = sorted(
        trials,
        key=lambda trial: (trial.get("passed", False), float(trial.get("score", 0.0)), trial.get("task_id", ""), trial.get("trial_index", 0)),
    )
    queue = []
    for trial in ranked[:sample_count]:
        run_dir = Path(trial["run_dir"])
        trace_html = run_dir / "trace.html"
        try:
            trace_ref = str(trace_html.relative_to(suite_dir))
        except ValueError:
            trace_ref = str(trace_html)
        queue.append(
            {
                "task_id": trial.get("task_id"),
                "trial_index": trial.get("trial_index"),
                "passed": trial.get("passed"),
                "score": trial.get("score"),
                "trace_html": trace_ref,
                "run_dir": str(run_dir),
            }
        )
    return queue
