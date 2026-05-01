from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from aegiseval.agents.openai_compatible import OpenAICompatibleAgent, SYSTEM_PROMPT
from aegiseval.schema import TaskSpec
from aegiseval.traces import TraceWriter


class AnthropicAgent(OpenAICompatibleAgent):
    """Adapter for Anthropic Messages API.

    The model must return JSON text in this shape:
    {"files": [{"path": "final.md", "content": "..."}]}
    """

    def __init__(self, model: str, base_url: str = "https://api.anthropic.com/v1", api_key_env: str = "ANTHROPIC_API_KEY", timeout: int = 120):
        super().__init__(model=model, base_url=base_url, api_key_env=api_key_env, timeout=timeout)

    def run(self, task: TaskSpec, workspace: Path, trace: TraceWriter) -> None:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"missing API key environment variable: {self.api_key_env}")
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": 0,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": self._build_prompt(task, workspace)},
            ],
        }
        trace.write("model_request_started", {"agent": "anthropic", "model": self.model, "base_url": self.base_url})
        response = self._post_anthropic_json(f"{self.base_url}/messages", payload, api_key)
        content = "".join(block.get("text", "") for block in response.get("content", []) if block.get("type") == "text")
        files_payload = self._parse_files_payload(content)
        for item in files_payload["files"]:
            relative_path = Path(item["path"])
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise ValueError(f"unsafe model artifact path: {item['path']}")
            target = workspace / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(str(item["content"]), encoding="utf-8")
            trace.write("model_artifact_written", {"path": str(relative_path), "bytes": target.stat().st_size})
        trace.write("model_request_finished", {"files_written": len(files_payload["files"])})

    def _post_anthropic_json(self, url: str, payload: dict[str, Any], api_key: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # noqa: S310 - user-configured local/API URL
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"anthropic API HTTP {exc.code}: {body}") from exc
