from __future__ import annotations

from pathlib import Path

from aegiseval.agents.anthropic import AnthropicAgent
from aegiseval.agents.dummy import DummyAgent
from aegiseval.agents.openai_compatible import OpenAICompatibleAgent
from aegiseval.agents.subprocess_agent import SubprocessAgent
from aegiseval.env import TrialEnvironment
from aegiseval.graders.registry import grade
from aegiseval.io import load_task, write_json
from aegiseval.schema import TrialResult
from aegiseval.traces import TraceWriter


def get_agent(
    agent_name: str,
    agent_command: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key_env: str = "OPENAI_API_KEY",
):
    if agent_name == "dummy":
        return DummyAgent()
    if agent_name == "subprocess":
        if agent_command is None:
            raise ValueError("--agent-command is required for subprocess agent")
        return SubprocessAgent(agent_command)
    if agent_name == "openai-compatible":
        if model is None or base_url is None:
            raise ValueError("--model and --base-url are required for openai-compatible agent")
        return OpenAICompatibleAgent(model=model, base_url=base_url, api_key_env=api_key_env)
    if agent_name == "anthropic":
        if model is None:
            raise ValueError("--model is required for anthropic agent")
        return AnthropicAgent(model=model, base_url=base_url or "https://api.anthropic.com/v1", api_key_env=api_key_env)
    raise ValueError(f"unknown agent: {agent_name}")


def run_task(
    task_dir: Path,
    agent_name: str,
    out_dir: Path,
    agent_command: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key_env: str = "OPENAI_API_KEY",
) -> TrialResult:
    task_dir = task_dir.resolve()
    task = load_task(task_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    env = TrialEnvironment.create(task.id, task_dir / "fixtures", out_dir)
    trace = TraceWriter(out_dir / "trace.jsonl")
    trace.write("trial_started", {"task_id": task.id, "agent": agent_name})

    agent = get_agent(agent_name, agent_command=agent_command, model=model, base_url=base_url, api_key_env=api_key_env)
    try:
        agent.run(task, env.workspace, trace)
    except Exception as exc:
        trace.write("trial_failed", {"error_type": type(exc).__name__, "error": str(exc)})
        raise

    grader_result = grade(task, env.workspace)
    artifacts = env.collect_artifacts([artifact.path for artifact in task.expected_artifacts])
    trace.write("grader_result", grader_result.model_dump())
    result = TrialResult(
        task_id=task.id,
        passed=grader_result.passed,
        score=grader_result.score,
        issues=grader_result.issues,
        artifacts=artifacts,
        trace_path=str(out_dir / "trace.jsonl"),
        workspace_path=str(env.workspace),
    )
    trace.write("trial_finished", {"passed": result.passed, "score": result.score})
    write_json(out_dir / "result.json", result.model_dump())
    return result
