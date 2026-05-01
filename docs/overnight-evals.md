# Overnight model evals

AegisEval can run a longer real-model suite overnight and write inspectable artifacts for the next morning.

The overnight runner is intentionally boring: it uses the same task specs, graders, traces, artifact previews, suite report, and eval-quality audit as the normal CLI. The only difference is that it keeps going after individual model/API failures and records them in `suite_result.json`.

## Requirements

1. A model API key in the environment.
   - OpenRouter: `OPENROUTER_API_KEY`
   - OpenAI-compatible local server: whatever env var you pass with `--api-key-env`
   - Anthropic direct is supported by the normal CLI, but the overnight default uses OpenRouter through the OpenAI-compatible adapter.
2. Network access to the model endpoint.
3. Enough budget/quota for the number of trials.
4. A writable output directory under `runs/`.

## Default command

```bash
PYTHONPATH=src python scripts/run_overnight_eval.py \
  --trials 25 \
  --model z-ai/glm-5.1 \
  --base-url https://openrouter.ai/api/v1 \
  --api-key-env OPENROUTER_API_KEY \
  --out runs/overnight/glm-5.1-$(date -u +%Y%m%dT%H%M%SZ)
```

The default task set is:

- `tasks/doc_synthesis_001`
- `tasks/data_analysis_001`

With `--trials 25`, this is 50 model calls total.

## Background run

```bash
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p runs/overnight/$RUN_ID
nohup env PYTHONPATH=src python scripts/run_overnight_eval.py \
  --trials 25 \
  --model z-ai/glm-5.1 \
  --base-url https://openrouter.ai/api/v1 \
  --api-key-env OPENROUTER_API_KEY \
  --out runs/overnight/$RUN_ID \
  > runs/overnight/$RUN_ID/overnight.log 2>&1 &

echo $! > runs/overnight/$RUN_ID/pid.txt
```

## Outputs

Each overnight run writes:

- `overnight.log` — stdout/stderr log
- `suite_result.json` — machine-readable aggregate result
- `report.html` — static suite report
- `eval_audit.json` — machine-readable harness-quality audit
- `eval_audit.md` — human review checklist and transcript queue
- `trials/<task>/trial-*/trace.jsonl` — raw trace events
- `trials/<task>/trial-*/trace.html` — per-trial HTML drilldown
- `trials/<task>/trial-*/workspace/*` — model-written artifacts

## Morning review checklist

1. Open `report.html` and scan pass rate/flakes.
2. Open `eval_audit.md` and read the queued traces.
3. Inspect failed trials first; a low score may reveal a grader weakness, prompt mismatch, or model capability gap.
4. Run red-team scanners:

```bash
PYTHONPATH=src python -m aegiseval.cli redteam --out runs/redteam-$(date -u +%Y%m%dT%H%M%SZ)
```

5. If a model finds a grader loophole, turn the loophole into a regression test before changing the grader.

## Budget notes

The MVP tasks are small: each call sends short fixture files and expects short artifacts. The cost is primarily the model's minimum request pricing and output tokens. Start with `--trials 3` to check formatting and quota before launching `--trials 25+`.
