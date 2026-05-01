# AegisEval Technical Report

## Motivation

Agent evaluations are only useful when the full chain is inspectable: task spec, environment state, agent actions, artifacts, grader logic, and final outcome. AegisEval is a local-first harness for reliable knowledge-work agent evals.

## Design principles

1. Outcome over claims: grade the final environment and artifacts, not the agent's explanation of success.
2. Simple transparent interfaces: task YAML, Python graders, JSONL traces.
3. Deterministic smoke path: dummy agent and fixture-based tasks make infrastructure bugs easy to isolate.
4. Eval-integrity first: scanners test whether graders reject known exploit patterns.

## Task/environment model

A task directory contains:

- `task.yaml` — id, version, domain, instruction, artifacts, grader, tool metadata.
- `fixtures/` — input documents/data copied into each trial workspace.

Each run creates an output directory with:

- `workspace/` — isolated trial state.
- `trace.jsonl` — ordered lifecycle/action/grader events.
- `result.json` — normalized trial result.

## MVP task suite

- `doc_synthesis_001`: requires a cited memo over source documents and rejects fabricated citations.
- `data_analysis_001`: requires cleaning a messy CSV, writing numeric JSON output, and producing a short report.

## Reliability model

The current metric layer computes pass rate, pass@1, pass^2, and flake detection across repeated task outcomes. The gate layer can fail candidate summaries on pass-rate regression or excessive flaky tasks.

## Red-team model

The MVP red-team layer includes:

- fabricated citation scanner,
- artifact spoofing scanner.

The scanner output is intentionally simple: exploit title, severity, issues, and transcript. Later versions should persist findings and auto-generate regression tests from exploit transcripts.

## Limitations

- Model adapters are implemented for OpenAI-compatible `/v1/chat/completions` APIs and Anthropic Messages API.
- Container sandboxing is not implemented yet.
- Static report is CLI-only at this stage.
- Static HTML reports include trace drilldowns and artifact preview panels for markdown/json/text/csv outputs.
- Task suite is intentionally small; it proves the harness shape before scaling task count.
