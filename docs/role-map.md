# AegisEval Role Map

Target role: Anthropic Research Engineer, RL Infrastructure and Reliability — Knowledge Work.

| Anthropic signal | AegisEval evidence |
|---|---|
| Stable training/eval runs | `runner.py` creates isolated trial workspaces and deterministic traces. |
| Canonical eval tooling | `TaskSpec`, `GraderSpec`, `ArtifactSpec`, and CLI commands define a repeatable eval interface. |
| Outcome-based grading | Document and data tasks grade artifacts, claims, citations, and numeric outputs rather than agent self-reports. |
| Observability | JSONL traces capture lifecycle, agent messages, artifact writes, grader results, and final outcomes. |
| Eval integrity | Red-team scanners test fabricated citations and artifact spoofing. |
| Release processes | Gate primitives compare reliability summaries and fail on regression/flakes. |
| Researcher toil reduction | Dummy agent, smoke tasks, deterministic fixtures, and reports give a reproducible debug path. |

## Current MVP status

Implemented:

- Task schema.
- Trial environment reset/copy behavior.
- Trace writer.
- Dummy scripted agent.
- Document synthesis task and grader.
- Data analysis task and grader.
- Runner and Typer CLI.
- SQLite run store.
- Reliability metrics.
- Gate evaluator.
- Two eval-integrity red-team scanners.
- Static HTML suite reports with per-trial trace drilldowns.
- CLI red-team scanner command.
- CLI replay command for inspecting result, artifacts, and ordered trace events.
- Subprocess agent adapter for evaluating real command-line agents.
- OpenAI-compatible model adapter for OpenAI/OpenRouter/Z.ai-compatible gateways/local vLLM.
- Anthropic Messages API adapter.
- Artifact preview panels in per-trial HTML trace pages.

Next quality push:

- Add more realistic tasks and eval cards.
- Persist suite runs into SQLite store.
- Add richer benchmark comparison charts.
- Add task eval cards for each task.
- Add container sandboxing for untrusted agents.
