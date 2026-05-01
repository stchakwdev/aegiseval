# AegisEval Runbook

## Symptom: task run fails before grading

1. Check the CLI output for task path and agent name.
2. Confirm `task.yaml` exists.
3. Confirm fixture files are under `fixtures/`.
4. Run `python3 -m pytest tests/test_runner.py -q`.
5. Inspect `runs/<name>/trace.jsonl` if it was created.

## Symptom: grader returns unexpected failure

1. Open `runs/<name>/workspace/`.
2. Inspect required artifacts from `task.yaml`.
3. Run the specific grader test.
4. Check whether the failure is an agent artifact issue or a grader logic issue.
5. Add a regression test before changing grader behavior.

## Symptom: release gate fails

1. Compare baseline and candidate summaries.
2. Check pass-rate drop.
3. Inspect flake tasks.
4. Review traces for new failures.
5. Only relax thresholds if the eval owner accepts the changed risk.

## Smoke commands

```bash
cd /home/clawdbot/aegiseval
python3 -m pytest -q
PYTHONPATH=src python3 scripts/e2e_smoke.py
PYTHONPATH=src python3 -m aegiseval.cli run tasks/doc_synthesis_001 --agent dummy --out runs/doc-demo
PYTHONPATH=src python3 -m aegiseval.cli replay runs/doc-demo
PYTHONPATH=src python3 -m aegiseval.cli run tasks/data_analysis_001 --agent dummy --out runs/data-demo
PYTHONPATH=src python3 -m aegiseval.cli suite tasks/doc_synthesis_001 tasks/data_analysis_001 --trials 2 --agent dummy --out runs/suite-demo
PYTHONPATH=src python3 -m aegiseval.cli redteam --out runs/redteam-demo
PYTHONPATH=src python3 -m aegiseval.cli report runs/doc-demo

# Model-backed adapters require API keys and expect JSON-only file output.
# OpenAI-compatible gateways: --agent openai-compatible --model <model> --base-url <.../v1> --api-key-env OPENAI_API_KEY
# Anthropic: --agent anthropic --model <model> --api-key-env ANTHROPIC_API_KEY
```
