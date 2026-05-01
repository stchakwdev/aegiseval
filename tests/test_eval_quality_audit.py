import json
from pathlib import Path

from typer.testing import CliRunner

from aegiseval.audit import audit_suite_dir
from aegiseval.cli import app
from aegiseval.suite import run_suite


def test_suite_writes_eval_quality_audit(tmp_path: Path):
    out = tmp_path / "suite"
    run_suite(
        task_dirs=[Path("tasks/doc_synthesis_001"), Path("tasks/data_analysis_001")],
        agent_name="dummy",
        trials=2,
        out_dir=out,
    )

    audit_path = out / "eval_audit.json"
    report_path = out / "eval_audit.md"
    assert audit_path.exists()
    assert report_path.exists()

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    checks = {check["name"]: check for check in audit["checks"]}
    assert checks["multi_trial_protocol"]["status"] == "pass"
    assert checks["outcome_grading_recorded"]["status"] == "pass"
    assert checks["trace_lifecycle_complete"]["status"] == "pass"
    assert checks["artifacts_recorded"]["status"] == "pass"
    assert audit["review_queue"]

    markdown = report_path.read_text(encoding="utf-8")
    assert "Human transcript review queue" in markdown
    assert "Demystifying evals for AI agents" in markdown
    assert "trace.html" in markdown


def test_audit_warns_on_single_trial_protocol(tmp_path: Path):
    out = tmp_path / "suite"
    run_suite(
        task_dirs=[Path("tasks/doc_synthesis_001")],
        agent_name="dummy",
        trials=1,
        out_dir=out,
    )

    audit = audit_suite_dir(out)
    checks = {check["name"]: check for check in audit["checks"]}
    assert checks["multi_trial_protocol"]["status"] == "warn"
    assert checks["human_transcript_review_queue"]["status"] == "pass"


def test_cli_audit_suite_command_writes_reports(tmp_path: Path):
    out = tmp_path / "suite"
    run_suite(
        task_dirs=[Path("tasks/doc_synthesis_001")],
        agent_name="dummy",
        trials=1,
        out_dir=out,
    )
    (out / "eval_audit.json").unlink()
    (out / "eval_audit.md").unlink()

    result = CliRunner().invoke(app, ["audit-suite", str(out), "--sample-count", "1"])

    assert result.exit_code == 0, result.output
    assert "eval audit" in result.output
    assert (out / "eval_audit.json").exists()
    audit = json.loads((out / "eval_audit.json").read_text(encoding="utf-8"))
    assert len(audit["review_queue"]) == 1
