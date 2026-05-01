from __future__ import annotations

from html import escape
import json
from pathlib import Path
from typing import Any

from aegiseval.audit import write_eval_audit
from aegiseval.io import write_json
from aegiseval.metrics import summarize_trials
from aegiseval.replay import load_replay
from aegiseval.runner import run_task


def run_suite(
    task_dirs: list[Path],
    agent_name: str,
    trials: int,
    out_dir: Path,
    agent_command: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key_env: str = "OPENAI_API_KEY",
) -> dict[str, Any]:
    if trials < 1:
        raise ValueError("trials must be >= 1")
    out_dir.mkdir(parents=True, exist_ok=True)
    trial_payloads: list[dict[str, Any]] = []

    for task_dir in task_dirs:
        task_id = task_dir.name
        for index in range(1, trials + 1):
            trial_dir = out_dir / "trials" / task_id / f"trial-{index:03d}"
            result = run_task(
                task_dir,
                agent_name=agent_name,
                out_dir=trial_dir,
                agent_command=agent_command,
                model=model,
                base_url=base_url,
                api_key_env=api_key_env,
            )
            write_trace_html(trial_dir / "trace.html", trial_dir)
            payload = result.model_dump()
            payload["trial_index"] = index
            payload["run_dir"] = str(trial_dir)
            trial_payloads.append(payload)

    summary = summarize_trials(trial_payloads)
    suite_result = {
        "agent": agent_name,
        "trials_per_task": trials,
        "tasks": [str(path) for path in task_dirs],
        "summary": summary,
        "trials": trial_payloads,
    }
    write_json(out_dir / "suite_result.json", suite_result)
    write_suite_html(out_dir / "report.html", suite_result)
    write_eval_audit(out_dir, suite_result)
    return suite_result


def write_suite_html(path: Path, suite_result: dict[str, Any]) -> None:
    rows = []
    for trial in suite_result["trials"]:
        issues = "; ".join(trial.get("issues", [])) or "none"
        run_dir = Path(trial["run_dir"])
        try:
            trace_href = str(run_dir.relative_to(path.parent) / "trace.html")
        except ValueError:
            trace_href = str(run_dir / "trace.html")
        rows.append(
            "<tr>"
            f"<td>{escape(str(trial['task_id']))}</td>"
            f"<td>{escape(str(trial['trial_index']))}</td>"
            f"<td>{escape(str(trial['passed']))}</td>"
            f"<td>{escape(str(trial['score']))}</td>"
            f"<td>{escape(issues)}</td>"
            f"<td><a href=\"{escape(trace_href)}\">trace.html</a></td>"
            f"<td>{escape(str(trial['run_dir']))}</td>"
            "</tr>"
        )
    summary = suite_result["summary"]
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AegisEval Suite Report</title>
  <style>
    body {{ background: #0a0a0a; color: #f5f5f5; font-family: Inter, system-ui, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #333; padding: 0.55rem; text-align: left; }}
    th {{ background: #171717; }}
    .card {{ background: #111; border: 1px solid #333; border-radius: 12px; padding: 1rem; margin: 1rem 0; }}
  </style>
</head>
<body>
  <h1>AegisEval Suite Report</h1>
  <div class="card">
    <p><strong>Agent:</strong> {escape(str(suite_result['agent']))}</p>
    <p><strong>Total trials:</strong> {escape(str(summary['total_trials']))}</p>
    <p><strong>Pass rate:</strong> {escape(str(summary['pass_rate']))}</p>
    <p><strong>Flake tasks:</strong> {escape(', '.join(summary['flake_tasks']) or 'none')}</p>
    <p><strong>Eval-quality audit:</strong> eval_audit.md</p>
  </div>
  <table>
    <thead><tr><th>Task</th><th>Trial</th><th>Passed</th><th>Score</th><th>Issues</th><th>Trace</th><th>Run dir</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def write_trace_html(path: Path, run_dir: Path) -> None:
    replay = load_replay(run_dir)
    event_rows = []
    for event in replay["events"]:
        event_rows.append(
            "<tr>"
            f"<td>{escape(str(event['seq']))}</td>"
            f"<td>{escape(str(event['event']))}</td>"
            f"<td><pre>{escape(str(event.get('payload', {})))}</pre></td>"
            "</tr>"
        )
    artifact_rows = []
    preview_cards = []
    workspace = Path(replay["run_dir"]) / "workspace"
    for artifact in replay["artifacts"]:
        artifact_path = workspace / artifact["path"]
        artifact_rows.append(
            "<tr>"
            f"<td>{escape(str(artifact['path']))}</td>"
            f"<td>{escape(str(artifact['exists']))}</td>"
            f"<td>{escape(str(artifact.get('sha256') or ''))}</td>"
            "</tr>"
        )
        preview = render_artifact_preview(artifact_path, str(artifact["path"]))
        if preview:
            preview_cards.append(preview)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AegisEval Trace: {escape(str(replay['task_id']))}</title>
  <style>
    body {{ background: #0a0a0a; color: #f5f5f5; font-family: Inter, system-ui, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #333; padding: 0.55rem; text-align: left; vertical-align: top; }}
    th {{ background: #171717; }}
    pre {{ white-space: pre-wrap; margin: 0; }}
    .artifact-preview {{ background: #111; border: 1px solid #333; border-radius: 12px; margin: 1rem 0; padding: 1rem; box-shadow: 0 0 24px rgba(124,58,237,0.10); }}
    .artifact-preview h3 {{ color: #EC4899; margin-top: 0; }}
    .artifact-preview pre {{ color: #E5E7EB; }}
  </style>
</head>
<body>
  <h1>Trace: {escape(str(replay['task_id']))}</h1>
  <p><strong>Passed:</strong> {escape(str(replay['passed']))} <strong>Score:</strong> {escape(str(replay['score']))}</p>
  <h2>Artifacts</h2>
  <table><thead><tr><th>Path</th><th>Exists</th><th>SHA256</th></tr></thead><tbody>{''.join(artifact_rows)}</tbody></table>
  <h2>Artifact previews</h2>
  <div class="previews">{''.join(preview_cards) or '<p>No previewable artifacts.</p>'}</div>
  <h2>Events</h2>
  <table><thead><tr><th>Seq</th><th>Event</th><th>Payload</th></tr></thead><tbody>{''.join(event_rows)}</tbody></table>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def render_artifact_preview(path: Path, label: str) -> str:
    if not path.exists() or not path.is_file():
        return ""
    if path.suffix.lower() not in {".md", ".txt", ".json", ".csv"}:
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".json":
        try:
            text = json.dumps(json.loads(text), indent=2, sort_keys=True)
        except json.JSONDecodeError:
            pass
    if len(text) > 4000:
        text = text[:4000] + "\n...[truncated]"
    return (
        '<section class="artifact-preview">'
        f"<h3>{escape(label)}</h3>"
        f"<pre>{escape(text)}</pre>"
        "</section>"
    )
