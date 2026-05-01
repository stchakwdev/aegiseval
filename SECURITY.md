# Security Policy

AegisEval is an evaluation harness for local, inspectable agent runs. It is not a sandbox.

## Supported versions

This repository is pre-1.0. Security fixes target `main`.

## Reporting vulnerabilities

Open a GitHub issue if the report can be public. If the issue involves secrets, private infrastructure, or an exploit that should not be public, contact the repository owner privately before disclosing details.

Do not include API keys, model provider tokens, or private run artifacts in public issues.

## Security boundaries

### Task specs

Task specs are trusted input in the current design. The schema rejects unsafe expected artifact paths, but task fixtures and instructions are still treated as local project content. Do not run untrusted task bundles without reviewing them.

### Subprocess agents

`--agent subprocess` executes a local command in the trial workspace. This is for trusted solvers and local agent CLIs only. It is not containerized and does not restrict filesystem or network access beyond the command's normal operating-system permissions.

### Model-written artifacts

Model adapters only write paths returned under the `{ "files": [...] }` contract. Absolute paths and `..` traversal are rejected. Artifact previews escape HTML before rendering. Still, generated artifacts should be treated as untrusted text until reviewed.

### API keys

API keys should be passed through environment variables such as `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY`. The harness never needs keys checked into the repository. Unit tests use local stub HTTP servers and must not call paid APIs.

### Reports

Static reports are designed for local inspection. They may include model outputs, trace payloads, artifact contents, provider base URLs, and failure messages. Review reports before publishing them.

## Known non-goals

- No container sandboxing for subprocess agents yet.
- No secret scanning of generated run directories yet.
- No authentication layer for report viewing yet.
- No guarantee that arbitrary third-party task packs are safe.

## Recommended safe usage

1. Run only trusted task packs.
2. Keep `runs/` out of git.
3. Publish only curated example reports.
4. Use low-privilege API keys where possible.
5. Prefer local stub servers in automated tests.
6. Add container isolation before evaluating untrusted agents.
