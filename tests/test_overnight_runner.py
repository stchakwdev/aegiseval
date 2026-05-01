from pathlib import Path

from scripts.run_overnight_eval import run_overnight_eval


def test_overnight_runner_writes_per_trial_trace_html(tmp_path: Path):
    out = tmp_path / "overnight"

    result = run_overnight_eval(
        tasks=[Path("tasks/doc_synthesis_001")],
        out_dir=out,
        trials=1,
        agent="dummy",
        model=None,
        base_url=None,
        api_key_env="unused",
        delay_seconds=0,
    )

    assert result["summary"]["total_trials"] == 1
    trace_html = out / "trials" / "doc_synthesis_001" / "trial-001" / "trace.html"
    assert trace_html.exists()
    assert "Artifact previews" in trace_html.read_text(encoding="utf-8")
    assert (out / "report.html").exists()
    assert (out / "eval_audit.md").exists()
