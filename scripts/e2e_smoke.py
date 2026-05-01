#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(cmd: list[str], *, cwd: Path = ROOT) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="aegis-smoke-") as tmp:
        out = Path(tmp)
        doc_solver = out / "doc_solver.py"
        doc_solver.write_text(
            "from pathlib import Path\n"
            "Path('final.md').write_text('Project Aurora reduced search time by 35% [memo_a.md]. The key rollout risk is fabricated citations [memo_b.md].', encoding='utf-8')\n",
            encoding="utf-8",
        )
        data_solver = out / "data_solver.py"
        data_solver.write_text(
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

        run([PYTHON, "-m", "pytest", "-q"])
        run([PYTHON, "-m", "aegiseval.cli", "run", "tasks/doc_synthesis_001", "--agent", "dummy", "--out", str(out / "doc")])
        run([PYTHON, "-m", "aegiseval.cli", "replay", str(out / "doc")])
        run([PYTHON, "-m", "aegiseval.cli", "report", str(out / "doc")])
        run([PYTHON, "-m", "aegiseval.cli", "run", "tasks/doc_synthesis_001", "--agent", "subprocess", "--agent-command", f"{PYTHON} {doc_solver}", "--out", str(out / "doc-subprocess")])
        run([PYTHON, "-m", "aegiseval.cli", "run", "tasks/data_analysis_001", "--agent", "subprocess", "--agent-command", f"{PYTHON} {data_solver}", "--out", str(out / "data-subprocess")])
        run([PYTHON, "-m", "aegiseval.cli", "suite", "tasks/doc_synthesis_001", "tasks/data_analysis_001", "--trials", "2", "--agent", "dummy", "--out", str(out / "suite")])
        run([PYTHON, "-m", "aegiseval.cli", "redteam", "--out", str(out / "redteam")])

        suite = json.loads((out / "suite" / "suite_result.json").read_text(encoding="utf-8"))
        assert suite["summary"]["total_trials"] == 4
        assert suite["summary"]["pass_rate"] == 1.0
        assert (out / "suite" / "report.html").exists()
        assert (out / "suite" / "trials" / "doc_synthesis_001" / "trial-001" / "trace.html").exists()
        findings = json.loads((out / "redteam" / "findings.json").read_text(encoding="utf-8"))
        assert len(findings) == 2
        assert all(finding["exploit_found"] for finding in findings)
        print(f"AegisEval smoke passed. Artifacts in {out}")


if __name__ == "__main__":
    main()
