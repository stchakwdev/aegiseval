# AegisEval Next Implementation Plan

Goal: complete the next three portfolio-critical features in one coherent pass.

## 1. Replay command

- Add `aegiseval.replay` with `load_replay(run_dir)`.
- Summarize `result.json`, `trace.jsonl`, and artifact records.
- Add CLI: `aegis replay RUN_DIR`.
- Tests: replay returns task id, score, ordered events, artifact paths.

## 2. Real CLI/subprocess agent adapter

- Add `agents/subprocess_agent.py`.
- It executes a user-provided command in the trial workspace.
- Pass task instruction via environment variables and `task.json` in workspace.
- Add CLI options: `--agent subprocess --agent-command "..."` for `run` and `suite`.
- Tests use a small Python one-liner/script to write valid artifacts.

## 3. Improved suite report

- Extend `suite.py` to generate per-trial trace HTML pages and artifact previews.
- Add suite report links to trace pages and artifact files.
- Include red-team findings section when present separately later; for now focus suite drilldown.
- Tests assert `trace.html` exists and report links to it.

## Verification

- Unit tests for all three features.
- Smoke:
  - dummy single run
  - subprocess single run
  - multi-task suite
  - replay command
  - redteam command
  - full pytest
