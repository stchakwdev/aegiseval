# Anthropic-Informed Eval Harness Notes

These notes capture the public Anthropic engineering/research ideas that now shape AegisEval. The goal is not to imitate internal Anthropic systems, but to build an open, inspectable eval harness that demonstrates the same engineering taste: simple components, outcome-first grading, replayable traces, and explicit reliability checks.

## Source reading

- **Demystifying evals for AI agents** — agent evals need tasks, trials, graders, transcripts/traces, outcomes, and environments. Grade the final environment state, not only what the agent says. Run multiple trials and read transcripts because scores can hide grader bugs or loopholes.
- **Effective harnesses for long-running agents** — long-horizon agents need structured handoff artifacts, incremental work, clean state, and explicit tests before declaring completion.
- **Building effective AI agents** — keep agent systems simple and composable. Prefer transparent direct APIs over opaque frameworks. Tool interfaces deserve the same care as human-computer interfaces.
- **Challenges in evaluating AI systems** — eval scores are fragile: contamination, formatting sensitivity, inconsistent implementations, broken controls, and overinterpreted metrics all matter.
- **From shortcuts to sabotage** — reward hacking is not cosmetic; hackable environments can train models toward broader misalignment. Eval infrastructure should search for loopholes and turn exploits into regression tests.
- **Petri** — automated auditing agents can generate multi-turn transcripts, score behavior, and surface the most interesting cases for human review.

## How this maps to AegisEval

| Anthropic lesson | AegisEval implementation |
| --- | --- |
| Outcome > claim | Graders inspect final workspace artifacts, not the agent's self-report. |
| Trials matter | `aegis suite --trials N` runs repeated trials and computes pass/flake metrics. |
| Read transcripts | `trace.jsonl`, `trace.html`, artifact previews, and `eval_audit.md` review queues make human inspection routine. |
| Keep the harness simple | Python modules, local deterministic workspaces, static HTML, no opaque orchestration framework. |
| Tool/model transparency | Model adapters log request lifecycle events and write artifacts through the same environment path. |
| Reward-hacking resistance | Red-team scanners exercise fabricated citations and artifact spoofing against graders. |
| Long-running cleanliness | Runbooks, smoke tests, docs, and audit reports define what a clean suite run looks like. |

## New portfolio-grade artifact: eval-quality audit

Every suite run now writes:

- `suite_result.json`
- `report.html`
- per-trial `trace.html`
- `eval_audit.json`
- `eval_audit.md`

The audit checks:

1. whether the suite used a multi-trial protocol;
2. whether outcome grading was recorded in every trace;
3. whether trial lifecycle events are complete;
4. whether final artifacts are recorded;
5. whether flaky tasks are surfaced;
6. whether model-backed runs expose model request lifecycle events;
7. which traces a human should inspect first.

This is deliberately small. The point is to make eval quality visible without adding a heavy framework.
