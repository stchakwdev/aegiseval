from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aegiseval.io import write_json
from aegiseval.metrics import summarize_trials
from aegiseval.runner import run_task
from aegiseval.suite import write_eval_audit, write_suite_html, write_trace_html

DEFAULT_TASKS = [Path("tasks/doc_synthesis_001"), Path("tasks/data_analysis_001")]


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.replace("export ", "").strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def run_overnight_eval(
    tasks: list[Path],
    out_dir: Path,
    trials: int,
    agent: str,
    model: str | None,
    base_url: str | None,
    api_key_env: str,
    delay_seconds: float,
    timeout: int = 120,
    retries: int = 2,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    trial_payloads: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    started_at = datetime.now(UTC).isoformat()

    for trial_index in range(1, trials + 1):
        for task_dir in tasks:
            task_id = task_dir.name
            trial_dir = out_dir / "trials" / task_id / f"trial-{trial_index:03d}"
            try:
                result = run_task(
                    task_dir,
                    agent_name=agent,
                    out_dir=trial_dir,
                    model=model,
                    base_url=base_url,
                    api_key_env=api_key_env,
                    timeout=timeout,
                    retries=retries,
                )
                write_trace_html(trial_dir / "trace.html", trial_dir)
                payload = result.model_dump()
                payload["trial_index"] = trial_index
                payload["run_dir"] = str(trial_dir)
                trial_payloads.append(payload)
                print(f"[trial] {task_id} #{trial_index} passed={result.passed} score={result.score}", flush=True)
            except Exception as exc:  # noqa: BLE001 - overnight runner must continue after single trial failures.
                failure = {
                    "task_id": task_id,
                    "trial_index": trial_index,
                    "run_dir": str(trial_dir),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
                failures.append(failure)
                if (trial_dir / "trace.jsonl").exists() and (trial_dir / "result.json").exists():
                    write_trace_html(trial_dir / "trace.html", trial_dir)
                print(f"[trial-error] {task_id} #{trial_index} {type(exc).__name__}: {exc}", flush=True)
            if delay_seconds:
                time.sleep(delay_seconds)

    suite_result = {
        "agent": agent,
        "model": model,
        "base_url": base_url,
        "trials_per_task": trials,
        "tasks": [str(path) for path in tasks],
        "summary": summarize_trials(trial_payloads) if trial_payloads else {"total_trials": 0, "pass_rate": 0.0, "flake_tasks": []},
        "trials": trial_payloads,
        "failures": failures,
        "started_at": started_at,
        "finished_at": datetime.now(UTC).isoformat(),
    }
    write_json(out_dir / "suite_result.json", suite_result)
    write_suite_html(out_dir / "report.html", suite_result)
    write_eval_audit(out_dir, suite_result)
    return suite_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a longer real-model AegisEval suite and keep going after trial failures.")
    parser.add_argument("--out", type=Path, default=Path("runs/overnight"))
    parser.add_argument("--trials", type=int, default=25, help="Trials per task. 25 over two MVP tasks gives 50 model calls.")
    parser.add_argument("--task", action="append", dest="tasks", type=Path, help="Task directory. Repeat to run multiple tasks.")
    parser.add_argument("--agent", default="openai-compatible")
    parser.add_argument("--model", default="z-ai/glm-5.1")
    parser.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--timeout", type=int, default=120, help="Model API request timeout in seconds.")
    parser.add_argument("--retries", type=int, default=2, help="Retries for transient model API failures.")
    parser.add_argument("--env-file", type=Path, default=Path.home() / ".hermes" / ".env")
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.trials < 1:
        raise SystemExit("--trials must be >= 1")
    load_env_file(args.env_file)
    if not os.environ.get(args.api_key_env):
        raise SystemExit(f"missing {args.api_key_env}; set it in the environment or pass --env-file")
    tasks = args.tasks or DEFAULT_TASKS
    result = run_overnight_eval(
        tasks=tasks,
        out_dir=args.out,
        trials=args.trials,
        agent=args.agent,
        model=args.model,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
        delay_seconds=args.delay_seconds,
        timeout=args.timeout,
        retries=args.retries,
    )
    print(json.dumps({"summary": result["summary"], "failures": len(result["failures"]), "out": str(args.out)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
