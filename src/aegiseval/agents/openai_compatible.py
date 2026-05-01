from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from aegiseval.schema import TaskSpec
from aegiseval.traces import TraceWriter

SYSTEM_PROMPT = (
    "You are an eval agent running inside a local workspace. "
    "Return ONLY JSON with shape {\"files\": [{\"path\": string, \"content\": string}]}. "
    "Do not wrap in markdown. Do not include explanations."
)


class OpenAICompatibleAgent:
    """Adapter for OpenAI-compatible /v1/chat/completions APIs.

    The model must return JSON in this shape:
    {"files": [{"path": "final.md", "content": "..."}]}
    """

    def __init__(
        self,
        model: str,
        base_url: str,
        api_key_env: str = "OPENAI_API_KEY",
        timeout: int = 120,
        retries: int = 2,
    ):
        if not model.strip():
            raise ValueError("model is required")
        if not base_url.strip():
            raise ValueError("base_url is required")
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        if retries < 0:
            raise ValueError("retries must be >= 0")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.timeout = timeout
        self.retries = retries

    def run(self, task: TaskSpec, workspace: Path, trace: TraceWriter) -> None:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"missing API key environment variable: {self.api_key_env}")
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": self._build_prompt(task, workspace),
                },
            ],
            "temperature": 0,
        }
        trace.write("model_request_started", {"agent": "openai-compatible", "model": self.model, "base_url": self.base_url})
        response = self._post_json(f"{self.base_url}/chat/completions", payload, api_key)
        content = response["choices"][0]["message"]["content"]
        files_payload = self._parse_files_payload(content)
        for item in files_payload["files"]:
            relative_path = Path(item["path"])
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise ValueError(f"unsafe model artifact path: {item['path']}")
            target = workspace / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(str(item["content"]), encoding="utf-8")
            trace.write("model_artifact_written", {"path": str(relative_path), "bytes": target.stat().st_size})
        trace.write(
            "model_request_finished",
            {
                "files_written": len(files_payload["files"]),
                "usage": response.get("usage", {}),
                "response_id": response.get("id"),
            },
        )

    def _post_json(self, url: str, payload: dict[str, Any], api_key: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"content-type": "application/json", "authorization": f"Bearer {api_key}"},
            method="POST",
        )
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:  # noqa: S310 - user-configured local/API URL
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                if exc.code not in {429, 500, 502, 503, 504} or attempt >= self.retries:
                    raise RuntimeError(f"model API HTTP {exc.code}: {body}") from exc
                time.sleep(2**attempt)
            except urllib.error.URLError as exc:
                if attempt >= self.retries:
                    raise RuntimeError(f"model API connection error: {exc}") from exc
                time.sleep(2**attempt)
        raise RuntimeError("model API request failed after retries")

    def _parse_files_payload(self, content: str) -> dict[str, Any]:
        payload = json.loads(_strip_json_code_fence(content))
        if not isinstance(payload, dict) or not isinstance(payload.get("files"), list):
            raise ValueError("model response must contain a files list")
        for item in payload["files"]:
            if not isinstance(item, dict) or "path" not in item or "content" not in item:
                raise ValueError("each file must contain path and content")
        return payload

    def _build_prompt(self, task: TaskSpec, workspace: Path) -> str:
        fixture_listing = []
        for path in sorted(workspace.rglob("*")):
            if path.is_file() and path.name != "task.json":
                rel = path.relative_to(workspace)
                text = path.read_text(encoding="utf-8", errors="replace")[:4000]
                fixture_listing.append(f"--- {rel} ---\n{text}")
        expected = ", ".join(artifact.path for artifact in task.expected_artifacts)
        return (
            f"Task id: {task.id}\n"
            f"Instruction:\n{task.instruction}\n\n"
            f"Expected output artifact paths: {expected}\n\n"
            "Workspace files:\n"
            + "\n\n".join(fixture_listing)
        )


def _strip_json_code_fence(content: str) -> str:
    stripped = content.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if not lines or not lines[0].startswith("```"):
        return stripped
    if lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return stripped
