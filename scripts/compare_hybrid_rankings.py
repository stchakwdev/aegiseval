from __future__ import annotations

import argparse
import json
from pathlib import Path

from aegiseval.io import write_json
from aegiseval.rank_stability import compare_rankings


def render_markdown(comparison: dict) -> str:
    lines = ["# AegisEval Hybrid Rank Stability", ""]
    lines.append("## Code ranking")
    for index, item in enumerate(comparison["code_ranking"], start=1):
        lines.append(f"{index}. `{item['model']}` — code_avg `{item['code_avg']}`")
    lines.append("")
    lines.append("## Hybrid ranking")
    for index, item in enumerate(comparison["hybrid_ranking"], start=1):
        lines.append(f"{index}. `{item['model']}` — hybrid_avg `{item['hybrid_avg']}`")
    lines.append("")
    lines.append("## Per-model disagreement")
    for model, metrics in comparison["models"].items():
        lines.append(
            f"- `{model}`: code_avg `{metrics['code_avg']}`, hybrid_avg `{metrics['hybrid_avg']}`, "
            f"code/judge disagreements `{metrics['code_judge_disagreements']}` / `{metrics['total_trials']}`"
        )
    lines.append("")
    lines.append("## Rank changes")
    for item in comparison["rank_changes"]:
        lines.append(f"- `{item['model']}`: code rank {item['code_rank']} → hybrid rank {item['hybrid_rank']} (delta {item['delta']})")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    comparison = compare_rankings(args.suite)
    args.out.mkdir(parents=True, exist_ok=True)
    write_json(args.out / "rank_stability.json", comparison)
    (args.out / "rank_stability.md").write_text(render_markdown(comparison), encoding="utf-8")
    print(json.dumps(comparison, indent=2), flush=True)


if __name__ == "__main__":
    main()
