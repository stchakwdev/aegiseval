from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aegiseval.audit import write_eval_audit
from aegiseval.io import load_task, write_json
from aegiseval.judge import apply_hybrid_score, judge_with_openai_compatible, local_judge_from_code_result
from aegiseval.metrics import summarize_trials
from aegiseval.runner import run_task
from aegiseval.suite import write_suite_html, write_trace_html

DEFAULT_TASKS = [
    Path("tasks/doc_synthesis_001"),
    Path("tasks/data_analysis_001"),
    Path("tasks/contradiction_review_001"),
    Path("tasks/policy_decision_001"),
    Path("tasks/incident_analysis_001"),
    Path("tasks/market_research_brief_001"),
    Path("tasks/lead_list_enrichment_001"),
    Path("tasks/executive_inbox_triage_001"),
    Path("tasks/seo_competitor_audit_001"),
    Path("tasks/survey_analysis_report_001"),
    Path("tasks/procurement_quote_comparison_001"),
    Path("tasks/policy_update_diff_001"),
    Path("tasks/customer_feedback_synthesis_001"),
    Path("tasks/real_estate_comp_report_001"),
    Path("tasks/import_export_brief_001"),
]


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.replace("export ", "").strip(), value.strip().strip('"').strip("'"))


def run_hybrid_eval(
    tasks: list[Path],
    out_dir: Path,
    trials: int,
    model: str,
    base_url: str,
    api_key_env: str,
    timeout: int,
    retries: int,
    delay_seconds: float,
    judge_model: str | None = None,
    judge_base_url: str | None = None,
    judge_api_key_env: str | None = None,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    trial_payloads: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    started_at = datetime.now(UTC).isoformat()

    for index in range(1, trials + 1):
        for task_dir in tasks:
            task_id = task_dir.name
            trial_dir = out_dir / "trials" / task_id / f"trial-{index:03d}"
            try:
                code_result = run_task(
                    task_dir,
                    agent_name="openai-compatible",
                    out_dir=trial_dir,
                    model=model,
                    base_url=base_url,
                    api_key_env=api_key_env,
                    timeout=timeout,
                    retries=retries,
                )
                if judge_model:
                    judge = judge_with_openai_compatible(
                        task=load_task(task_dir),
                        workspace=trial_dir / "workspace",
                        code_result=code_result,
                        model=judge_model,
                        base_url=judge_base_url or base_url,
                        api_key_env=judge_api_key_env or api_key_env,
                        timeout=timeout,
                    )
                else:
                    judge = local_judge_from_code_result(code_result)
                hybrid = apply_hybrid_score(code_result.passed, code_result.score, code_result.issues, judge)
                write_trace_html(trial_dir / "trace.html", trial_dir)
                payload = code_result.model_dump()
                payload["trial_index"] = index
                payload["run_dir"] = str(trial_dir)
                payload["judge"] = judge.model_dump()
                payload["hybrid_score"] = hybrid.score
                payload["hybrid_passed"] = hybrid.passed
                payload["hybrid_issues"] = hybrid.issues
                trial_payloads.append(payload)
                print(
                    f"[trial] {task_id} #{index} code_passed={code_result.passed} "
                    f"code_score={code_result.score} hybrid_passed={hybrid.passed} hybrid_score={hybrid.score}",
                    flush=True,
                )
            except Exception as exc:  # noqa: BLE001 - comparison runner keeps going after trial failures.
                failure = {
                    "task_id": task_id,
                    "trial_index": index,
                    "run_dir": str(trial_dir),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
                failures.append(failure)
                if (trial_dir / "trace.jsonl").exists() and (trial_dir / "result.json").exists():
                    write_trace_html(trial_dir / "trace.html", trial_dir)
                print(f"[trial-error] {task_id} #{index} {type(exc).__name__}: {exc}", flush=True)
            if delay_seconds:
                time.sleep(delay_seconds)

    hybrid_trials = [dict(trial, passed=trial["hybrid_passed"], score=trial["hybrid_score"]) for trial in trial_payloads]
    suite_result = {
        "agent": "openai-compatible",
        "model": model,
        "base_url": base_url,
        "trials_per_task": trials,
        "tasks": [str(path) for path in tasks],
        "summary": summarize_trials(trial_payloads) if trial_payloads else {"total_trials": 0, "pass_rate": 0.0, "flake_tasks": []},
        "hybrid_summary": summarize_trials(hybrid_trials) if hybrid_trials else {"total_trials": 0, "pass_rate": 0.0, "flake_tasks": []},
        "trials": trial_payloads,
        "failures": failures,
        "started_at": started_at,
        "finished_at": datetime.now(UTC).isoformat(),
        "judge_mode": "openai_compatible" if judge_model else "local_deterministic_proxy",
        "judge_model": judge_model,
    }
    write_json(out_dir / "suite_result.json", suite_result)
    write_suite_html(out_dir / "report.html", suite_result)
    write_eval_audit(out_dir, suite_result)
    return suite_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run model comparison suite with deterministic hybrid judge scoring.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--task", action="append", dest="tasks", type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--env-file", type=Path, default=Path.home() / ".hermes" / ".env")
    parser.add_argument("--judge-model", default=None)
    parser.add_argument("--judge-base-url", default=None)
    parser.add_argument("--judge-api-key-env", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_env_file(args.env_file)
    if not os.environ.get(args.api_key_env):
        raise SystemExit(f"missing {args.api_key_env}; set it in environment or pass --env-file")
    result = run_hybrid_eval(
        tasks=args.tasks or DEFAULT_TASKS,
        out_dir=args.out,
        trials=args.trials,
        model=args.model,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
        timeout=args.timeout,
        retries=args.retries,
        delay_seconds=args.delay_seconds,
        judge_model=args.judge_model,
        judge_base_url=args.judge_base_url,
        judge_api_key_env=args.judge_api_key_env,
    )
    print(json.dumps({"summary": result["summary"], "hybrid_summary": result["hybrid_summary"], "failures": len(result["failures"]), "out": str(args.out)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
