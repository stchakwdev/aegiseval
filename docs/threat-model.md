# Threat model

AegisEval evaluates agents that read local fixtures and write output artifacts. The main security risks are not remote attackers; they are unsafe local execution, unsafe task bundles, misleading reports, and accidental secret exposure.

## Assets

- API keys used by model adapters.
- Local filesystem outside trial workspaces.
- Generated eval traces and reports.
- Integrity of grader results and benchmark claims.
- Developer machine or VPS running subprocess agents.

## Trust assumptions

| Component | Trust level | Notes |
| --- | --- | --- |
| Built-in task specs | trusted | Reviewed and version-controlled in this repo. |
| Third-party task specs | untrusted until reviewed | May include malicious fixture content or misleading instructions. |
| Dummy agent | trusted | Deterministic local solver. |
| Subprocess agent command | trusted only | Runs with normal OS permissions. No sandbox. |
| Model API responses | untrusted | Can return malformed JSON, unsafe paths, or adversarial content. |
| Static reports | sensitive until reviewed | May contain model output and trace payloads. |

## Main risks and mitigations

### Accidental filesystem deletion

Risk: a user passes an unsafe `--out` path and the harness deletes important files while resetting a trial.

Mitigation: run directories now use an `.aegiseval-run` marker. AegisEval refuses to delete non-empty unmarked directories and symlink run paths.

### Path traversal in artifacts

Risk: a task spec or model output references absolute paths or `..` paths.

Mitigation: task artifact paths and model-written artifact paths reject absolute paths and `..` components.

### Arbitrary code execution through subprocess agents

Risk: `--agent subprocess` runs arbitrary commands.

Mitigation: documentation labels subprocess mode as trusted-only. Future hardening should add container or restricted-process isolation.

### Misleading eval scores

Risk: scores hide brittle graders, missing artifacts, or flaky behavior.

Mitigation: suite runs produce trace drilldowns, artifact previews, flake metrics, and `eval_audit.md` review queues.

### Secret leakage in reports

Risk: trace payloads, model errors, or generated artifacts include credentials.

Mitigation: unit tests use stubs; docs warn to review reports before publication. Future hardening should add optional secret scanning for reports.

### Reward hacking / grader loopholes

Risk: agents satisfy the letter of a grader while violating task intent.

Mitigation: red-team scanners test citation fabrication and artifact spoofing. Harder tasks include contradictions, policy constraints, and incident-analysis traps.

## Future mitigations

- Container sandbox for subprocess agents.
- Optional report secret scanner.
- Signed task packs or task provenance metadata.
- Model API retry budget and rate-limit telemetry.
- Regression-test generator from failed/red-team traces.
