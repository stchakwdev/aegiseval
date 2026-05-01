# AegisEval Eval-Quality Audit

Suite: `examples/reports/portfolio-demo`
Agent: `dummy`

## Checks

| Check | Status | Why it matters |
| --- | --- | --- |
| `multi_trial_protocol` | **PASS** | Run at least two trials per task before trusting pass-rate changes. |
| `outcome_grading_recorded` | **PASS** | Grade final environment artifacts/outcomes, not just agent claims. |
| `trace_lifecycle_complete` | **PASS** | Every trial should have a complete start/finish lifecycle in its trace. |
| `artifacts_recorded` | **PASS** | Artifacts must be recorded so humans can inspect final environment state. |
| `flake_visibility` | **PASS** | Flaky tasks should be explicit because stochastic agent failures compound. |
| `model_call_transparency` | **PASS** | No model-backed adapter was used; model request tracing is not required for this suite. |
| `human_transcript_review_queue` | **PASS** | Keep a small deterministic queue of traces for human reading; scores alone are not enough. |

## Human transcript review queue

- `contradiction_review_001` trial `1` score `1.0` passed `True` — [trials/contradiction_review_001/trial-001/trace.html](trials/contradiction_review_001/trial-001/trace.html)
- `contradiction_review_001` trial `2` score `1.0` passed `True` — [trials/contradiction_review_001/trial-002/trace.html](trials/contradiction_review_001/trial-002/trace.html)
- `data_analysis_001` trial `1` score `1.0` passed `True` — [trials/data_analysis_001/trial-001/trace.html](trials/data_analysis_001/trial-001/trace.html)

## Source principles

- Anthropic — Demystifying evals for AI agents
- Anthropic — Effective harnesses for long-running agents
- Anthropic — Building effective AI agents
- Anthropic — Challenges in evaluating AI systems
- Anthropic — From shortcuts to sabotage: natural emergent misalignment from reward hacking
- Anthropic — Petri: An open-source auditing tool to accelerate AI safety research
