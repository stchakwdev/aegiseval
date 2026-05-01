from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from typer.testing import CliRunner

from aegiseval.agents.openai_compatible import OpenAICompatibleAgent
from aegiseval.cli import app
from aegiseval.runner import run_task


class _OpenAIStubHandler(BaseHTTPRequestHandler):
    response_content = ""
    response_contents: list[str] = []
    seen_requests: list[dict] = []
    transient_failures_remaining = 0

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("content-length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        self.__class__.seen_requests.append(
            {
                "path": self.path,
                "authorization": self.headers.get("authorization"),
                "body": body,
            }
        )
        if self.__class__.transient_failures_remaining > 0:
            self.__class__.transient_failures_remaining -= 1
            encoded = b'{"error":"temporary"}'
            self.send_response(500)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return
        content = (
            self.__class__.response_contents.pop(0)
            if self.__class__.response_contents
            else self.__class__.response_content
        )
        payload = {
            "choices": [
                {
                    "message": {
                        "content": content,
                    }
                }
            ]
        }
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        return


def _start_stub(response_content: str):
    _OpenAIStubHandler.response_content = response_content
    _OpenAIStubHandler.response_contents = []
    _OpenAIStubHandler.seen_requests = []
    _OpenAIStubHandler.transient_failures_remaining = 0
    server = HTTPServer(("127.0.0.1", 0), _OpenAIStubHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def test_suite_trace_html_includes_artifact_preview_panel(tmp_path: Path):
    out = tmp_path / "suite"
    result = CliRunner().invoke(
        app,
        [
            "suite",
            "tasks/doc_synthesis_001",
            "--trials",
            "1",
            "--agent",
            "dummy",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output

    trace_html = (out / "trials" / "doc_synthesis_001" / "trial-001" / "trace.html").read_text(encoding="utf-8")
    assert "Artifact previews" in trace_html
    assert "Project Aurora memo" in trace_html
    assert "final.md" in trace_html


def test_openai_compatible_agent_writes_model_returned_artifacts(tmp_path: Path, monkeypatch):
    response_content = json.dumps(
        {
            "files": [
                {
                    "path": "final.md",
                    "content": "Project Aurora reduced search time by 35% [memo_a.md]. The key rollout risk is fabricated citations [memo_b.md].",
                }
            ]
        }
    )
    server = _start_stub(response_content)
    monkeypatch.setenv("AEGISEVAL_TEST_API_KEY", "test-key")
    try:
        result = run_task(
            Path("tasks/doc_synthesis_001"),
            agent_name="openai-compatible",
            out_dir=tmp_path / "run",
            model="stub-model",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            api_key_env="AEGISEVAL_TEST_API_KEY",
        )
    finally:
        server.shutdown()

    assert result.passed is True
    assert (tmp_path / "run" / "workspace" / "final.md").exists()
    seen = _OpenAIStubHandler.seen_requests[0]
    assert seen["path"] == "/v1/chat/completions"
    assert seen["authorization"] == "Bearer test-key"
    assert seen["body"]["model"] == "stub-model"
    assert seen["body"]["response_format"] == {"type": "json_object"}
    trace = (tmp_path / "run" / "trace.jsonl").read_text(encoding="utf-8")
    assert "model_request_started" in trace
    assert "model_artifact_written" in trace


def test_cli_openai_compatible_agent_accepts_model_options(tmp_path: Path, monkeypatch):
    response_content = json.dumps(
        {
            "files": [
                {
                    "path": "final.md",
                    "content": "Project Aurora reduced search time by 35% [memo_a.md]. The key rollout risk is fabricated citations [memo_b.md].",
                }
            ]
        }
    )
    server = _start_stub(response_content)
    monkeypatch.setenv("AEGISEVAL_TEST_API_KEY", "test-key")
    try:
        result = CliRunner().invoke(
            app,
            [
                "run",
                "tasks/doc_synthesis_001",
                "--agent",
                "openai-compatible",
                "--model",
                "stub-model",
                "--base-url",
                f"http://127.0.0.1:{server.server_port}/v1",
                "--api-key-env",
                "AEGISEVAL_TEST_API_KEY",
                "--timeout",
                "5",
                "--retries",
                "1",
                "--out",
                str(tmp_path / "run"),
            ],
        )
    finally:
        server.shutdown()

    assert result.exit_code == 0, result.output
    assert "[PASS]" in result.output


def test_openai_compatible_agent_parses_json_code_fence():
    agent = OpenAICompatibleAgent(model="stub", base_url="http://127.0.0.1")

    payload = agent._parse_files_payload('```json\n{"files":[{"path":"final.md","content":"ok"}]}\n```')

    assert payload["files"][0]["path"] == "final.md"


def test_openai_compatible_agent_extracts_json_from_prose_wrapper():
    agent = OpenAICompatibleAgent(model="stub", base_url="http://127.0.0.1")

    payload = agent._parse_files_payload('Sure — {"files":[{"path":"final.md","content":"ok"}]}')

    assert payload["files"][0]["content"] == "ok"


def test_openai_compatible_agent_repairs_invalid_json_response(tmp_path: Path, monkeypatch):
    server = _start_stub("")
    _OpenAIStubHandler.response_contents = [
        "not json",
        json.dumps(
            {
                "files": [
                    {
                        "path": "final.md",
                        "content": "Project Aurora reduced search time by 35% [memo_a.md]. The key rollout risk is fabricated citations [memo_b.md].",
                    }
                ]
            }
        ),
    ]
    monkeypatch.setenv("AEGISEVAL_TEST_API_KEY", "test-key")
    try:
        result = run_task(
            Path("tasks/doc_synthesis_001"),
            agent_name="openai-compatible",
            out_dir=tmp_path / "run",
            model="stub-model",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            api_key_env="AEGISEVAL_TEST_API_KEY",
        )
    finally:
        server.shutdown()

    assert result.passed is True
    assert len(_OpenAIStubHandler.seen_requests) == 2
    repair_request = _OpenAIStubHandler.seen_requests[1]["body"]
    assert repair_request["messages"][-1]["role"] == "user"
    assert "Repair this model response" in repair_request["messages"][-1]["content"]
    trace = (tmp_path / "run" / "trace.jsonl").read_text(encoding="utf-8")
    assert "model_response_parse_failed" in trace


def test_openai_compatible_agent_retries_transient_failure(tmp_path: Path, monkeypatch):
    response_content = json.dumps(
        {
            "files": [
                {
                    "path": "final.md",
                    "content": "Project Aurora reduced search time by 35% [memo_a.md]. The key rollout risk is fabricated citations [memo_b.md].",
                }
            ]
        }
    )
    server = _start_stub(response_content)
    _OpenAIStubHandler.transient_failures_remaining = 1
    monkeypatch.setenv("AEGISEVAL_TEST_API_KEY", "test-key")
    try:
        result = run_task(
            Path("tasks/doc_synthesis_001"),
            agent_name="openai-compatible",
            out_dir=tmp_path / "run",
            model="stub-model",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            api_key_env="AEGISEVAL_TEST_API_KEY",
            retries=1,
        )
    finally:
        server.shutdown()

    assert result.passed is True
    assert len(_OpenAIStubHandler.seen_requests) == 2
