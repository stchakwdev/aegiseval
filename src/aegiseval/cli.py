from __future__ import annotations

from pathlib import Path

import typer
from rich import print

from aegiseval import __version__
from aegiseval.audit import audit_suite_dir, render_eval_audit_markdown
from aegiseval.io import write_json
from aegiseval.redteam.runner import run_redteam
from aegiseval.replay import load_replay
from aegiseval.report import render_report
from aegiseval.runner import run_task
from aegiseval.suite import run_suite

app = typer.Typer(no_args_is_help=True)


@app.command()
def version() -> None:
    """Print version information."""
    print(f"aegiseval {__version__}")


@app.command()
def run(
    task_dir: Path = typer.Argument(..., help="Path to task directory containing task.yaml"),
    agent: str = typer.Option("dummy", "--agent", help="Agent adapter name"),
    agent_command: str | None = typer.Option(None, "--agent-command", help="Command for subprocess agent"),
    model: str | None = typer.Option(None, "--model", help="Model name for model-backed agents"),
    base_url: str | None = typer.Option(None, "--base-url", help="Base URL for OpenAI-compatible APIs, e.g. https://api.openai.com/v1"),
    api_key_env: str = typer.Option("OPENAI_API_KEY", "--api-key-env", help="Environment variable containing API key"),
    timeout: int = typer.Option(120, "--timeout", help="Model API request timeout in seconds"),
    retries: int = typer.Option(2, "--retries", help="Retries for transient model API failures"),
    out: Path = typer.Option(Path("runs/latest"), "--out", help="Output run directory"),
) -> None:
    """Run one task with an agent."""
    result = run_task(
        task_dir,
        agent_name=agent,
        out_dir=out,
        agent_command=agent_command,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        timeout=timeout,
        retries=retries,
    )
    status = "PASS" if result.passed else "FAIL"
    print(f"[{status}] {result.task_id} score={result.score} out={out}")


@app.command()
def report(run_dir: Path = typer.Argument(..., help="Run directory containing result.json")) -> None:
    """Render a run report."""
    render_report(run_dir)


@app.command()
def replay(run_dir: Path = typer.Argument(..., help="Run directory containing result.json and trace.jsonl")) -> None:
    """Print a replay summary for a completed run."""
    replay_data = load_replay(run_dir)
    print(f"task={replay_data['task_id']} passed={replay_data['passed']} score={replay_data['score']}")
    print("artifacts:")
    for artifact in replay_data["artifacts"]:
        print(f"- {artifact['path']} exists={artifact['exists']}")
    print("events:")
    for event in replay_data["events"]:
        print(f"- {event['seq']}: {event['event']}")


@app.command()
def suite(
    task_dirs: list[Path] = typer.Argument(..., help="Task directories to run"),
    trials: int = typer.Option(1, "--trials", help="Trials per task"),
    agent: str = typer.Option("dummy", "--agent", help="Agent adapter name"),
    agent_command: str | None = typer.Option(None, "--agent-command", help="Command for subprocess agent"),
    model: str | None = typer.Option(None, "--model", help="Model name for model-backed agents"),
    base_url: str | None = typer.Option(None, "--base-url", help="Base URL for OpenAI-compatible APIs"),
    api_key_env: str = typer.Option("OPENAI_API_KEY", "--api-key-env", help="Environment variable containing API key"),
    timeout: int = typer.Option(120, "--timeout", help="Model API request timeout in seconds"),
    retries: int = typer.Option(2, "--retries", help="Retries for transient model API failures"),
    out: Path = typer.Option(Path("runs/suite"), "--out", help="Suite output directory"),
) -> None:
    """Run multiple tasks across one or more trials and write an HTML report."""
    result = run_suite(
        task_dirs=task_dirs,
        agent_name=agent,
        trials=trials,
        out_dir=out,
        agent_command=agent_command,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        timeout=timeout,
        retries=retries,
    )
    print(
        f"[PASS] suite total_trials={result['summary']['total_trials']} "
        f"pass_rate={result['summary']['pass_rate']} report={out / 'report.html'}"
    )


@app.command("audit-suite")
def audit_suite_command(
    suite_dir: Path = typer.Argument(..., help="Suite directory containing suite_result.json"),
    sample_count: int = typer.Option(3, "--sample-count", help="Number of traces to queue for human review"),
) -> None:
    """Write an Anthropic-inspired eval-quality audit for a suite run."""
    audit = audit_suite_dir(suite_dir, sample_count=sample_count)
    write_json(suite_dir / "eval_audit.json", audit)
    markdown = render_eval_audit_markdown(audit)
    (suite_dir / "eval_audit.md").write_text(markdown, encoding="utf-8")
    print(f"[PASS] eval audit checks={len(audit['checks'])} report={suite_dir / 'eval_audit.md'}")


@app.command("redteam")
def redteam_command(
    out: Path = typer.Option(Path("runs/redteam"), "--out", help="Output directory for scanner artifacts"),
) -> None:
    """Run built-in eval-integrity scanners."""
    findings = run_redteam(out / "workspaces")
    write_json(out / "findings.json", findings)
    failed_to_reject = [finding for finding in findings if not finding["exploit_found"]]
    status = "PASS" if not failed_to_reject else "FAIL"
    print(f"[{status}] redteam findings={len(findings)} out={out / 'findings.json'}")


if __name__ == "__main__":
    app()
