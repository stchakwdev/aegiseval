from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path

from typer.testing import CliRunner

from aegiseval.cli import app


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href")
        if href:
            self.links.append(href)


def test_suite_report_links_resolve_to_trace_pages(tmp_path: Path):
    out = tmp_path / "suite"
    result = CliRunner().invoke(
        app,
        [
            "suite",
            "tasks/doc_synthesis_001",
            "tasks/data_analysis_001",
            "--trials",
            "2",
            "--agent",
            "dummy",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output

    report = out / "report.html"
    parser = _LinkParser()
    parser.feed(report.read_text(encoding="utf-8"))

    assert parser.links
    for href in parser.links:
        target = report.parent / href
        assert target.exists(), href
        trace_html = target.read_text(encoding="utf-8")
        assert "Events" in trace_html
        assert "Artifacts" in trace_html


def test_cli_subprocess_agent_solves_data_task_end_to_end(tmp_path: Path):
    script = tmp_path / "solve_data.py"
    script.write_text(
        "import csv, json\n"
        "from collections import defaultdict\n"
        "from pathlib import Path\n"
        "totals=defaultdict(float); clean_rows=0\n"
        "with Path('data.csv').open(newline='', encoding='utf-8') as handle:\n"
        "    for row in csv.DictReader(handle):\n"
        "        try: revenue=float(row['revenue'])\n"
        "        except (KeyError, ValueError): continue\n"
        "        if revenue < 0 or not row.get('region'): continue\n"
        "        clean_rows += 1; totals[row['region']] += revenue\n"
        "top_region=max(totals.items(), key=lambda item: item[1])[0]\n"
        "total_revenue=sum(totals.values())\n"
        "Path('answer.json').write_text(json.dumps({'clean_rows': clean_rows, 'total_revenue': total_revenue, 'top_region': top_region}), encoding='utf-8')\n"
        "Path('report.md').write_text(f'# Report\\n\\n{top_region} leads revenue after cleaning invalid rows.', encoding='utf-8')\n",
        encoding="utf-8",
    )

    out = tmp_path / "data-subprocess"
    result = CliRunner().invoke(
        app,
        [
            "run",
            "tasks/data_analysis_001",
            "--agent",
            "subprocess",
            "--agent-command",
            f"{sys.executable} {script}",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert payload["passed"] is True
    trace = (out / "trace.jsonl").read_text(encoding="utf-8")
    assert "subprocess_started" in trace
    assert "subprocess_finished" in trace
