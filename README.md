# AegisEval

Reliable infrastructure for agentic knowledge-work evals.

AegisEval is a local-first Python harness for building, running, grading, replaying, and auditing realistic knowledge-work agent tasks. The goal is to make agent evaluation runs trustworthy: versioned task specs, deterministic environments, outcome-based graders, trace capture, artifact inspection, reliability metrics, and release gates.

## Why this exists

Agent evals are easy to make impressive and hard to make trustworthy. A score is only useful if the task, environment, grader, trace, and artifacts can be inspected and reproduced. AegisEval starts from that premise.

## MVP scope

- Task schemas for knowledge-work environments.
- Local deterministic trial workspaces.
- JSONL traces for agent messages, tool calls, artifacts, grader results, and run lifecycle.
- Outcome-based graders for document synthesis and data analysis tasks.
- Dummy/scripted agent for deterministic smoke tests.
- Subprocess agent adapter for real CLI/agent integration.
- OpenAI-compatible chat-completions adapter for OpenAI, OpenRouter, Z.ai-compatible gateways, local vLLM, etc.
- Anthropic Messages API adapter.
- CLI commands for running, replaying, red-teaming, audit-reporting, and reporting.
- Multi-task/multi-trial suite runs with static HTML reports, per-trial trace drilldowns, artifact preview panels, and eval-quality audits.
- Eval-integrity red-team scanners for fabricated citations and artifact spoofing.

## Quickstart

```bash
cd /home/clawdbot/aegiseval
python3 -m venv .venv
.venv/bin/pip install -e . pytest
.venv/bin/pytest -q
PYTHONPATH=src .venv/bin/python scripts/e2e_smoke.py
.venv/bin/aegis run tasks/doc_synthesis_001 --agent dummy --out runs/doc-demo
.venv/bin/aegis replay runs/doc-demo
.venv/bin/aegis suite tasks/doc_synthesis_001 tasks/data_analysis_001 --trials 2 --agent dummy --out runs/suite-demo
.venv/bin/aegis audit-suite runs/suite-demo
.venv/bin/aegis redteam --out runs/redteam-demo
.venv/bin/aegis report runs/doc-demo
```

## Model-backed agents

Model adapters expect the model to return JSON only:

```json
{"files": [{"path": "final.md", "content": "..."}]}
```

OpenAI-compatible endpoint:

```bash
OPENAI_API_KEY=... .venv/bin/aegis run tasks/doc_synthesis_001 \
  --agent openai-compatible \
  --model gpt-4.1-mini \
  --base-url https://api.openai.com/v1 \
  --api-key-env OPENAI_API_KEY \
  --out runs/openai-demo
```

Anthropic endpoint:

```bash
ANTHROPIC_API_KEY=... .venv/bin/aegis run tasks/doc_synthesis_001 \
  --agent anthropic \
  --model claude-sonnet-4-5 \
  --api-key-env ANTHROPIC_API_KEY \
  --out runs/anthropic-demo
```

## Role fit

This project is built to demonstrate production-grade ownership of agentic evaluation infrastructure: canonical task specs, stable runs, instrumentation, outcome grading, replayability, reliability metrics, and eval-integrity failure analysis.

## Anthropic-informed harness principles

The design is guided by Anthropic's public technical writing on agent evals and long-running harnesses:

- grade final environment outcomes instead of trusting agent claims;
- run multiple trials and make flakes visible;
- preserve inspectable traces/transcripts and artifact previews;
- keep the harness simple and transparent rather than hiding behavior behind a large framework;
- treat reward-hacking and grader loopholes as first-class reliability failures.

See `docs/anthropic-eval-harness-notes.md` for the source-to-implementation mapping. Suite runs write `eval_audit.json` and `eval_audit.md` so the portfolio artifact contains not only scores, but also a review queue and harness-quality checks.
