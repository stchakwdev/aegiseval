from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from aegiseval.runner import run_task


class _AnthropicStubHandler(BaseHTTPRequestHandler):
    response_text = ""
    seen_requests: list[dict] = []

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("content-length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        self.__class__.seen_requests.append(
            {
                "path": self.path,
                "x_api_key": self.headers.get("x-api-key"),
                "anthropic_version": self.headers.get("anthropic-version"),
                "body": body,
            }
        )
        payload = {"content": [{"type": "text", "text": self.__class__.response_text}]}
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        return


def _start_stub(response_text: str):
    _AnthropicStubHandler.response_text = response_text
    _AnthropicStubHandler.seen_requests = []
    server = HTTPServer(("127.0.0.1", 0), _AnthropicStubHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def test_anthropic_agent_writes_model_returned_artifacts(tmp_path: Path, monkeypatch):
    response_text = json.dumps(
        {
            "files": [
                {
                    "path": "final.md",
                    "content": "Project Aurora reduced search time by 35% [memo_a.md]. The key rollout risk is fabricated citations [memo_b.md].",
                }
            ]
        }
    )
    server = _start_stub(response_text)
    monkeypatch.setenv("AEGISEVAL_TEST_ANTHROPIC_KEY", "anthropic-test-key")
    try:
        result = run_task(
            Path("tasks/doc_synthesis_001"),
            agent_name="anthropic",
            out_dir=tmp_path / "run",
            model="claude-test",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            api_key_env="AEGISEVAL_TEST_ANTHROPIC_KEY",
        )
    finally:
        server.shutdown()

    assert result.passed is True
    seen = _AnthropicStubHandler.seen_requests[0]
    assert seen["path"] == "/v1/messages"
    assert seen["x_api_key"] == "anthropic-test-key"
    assert seen["anthropic_version"]
    assert seen["body"]["model"] == "claude-test"
    trace = (tmp_path / "run" / "trace.jsonl").read_text(encoding="utf-8")
    assert "model_request_started" in trace
    assert "model_artifact_written" in trace
