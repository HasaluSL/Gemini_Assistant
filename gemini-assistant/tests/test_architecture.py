from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adaptive_assistant.agent import Agent
from adaptive_assistant.memory import MemoryManager
from adaptive_assistant.models import ModelResponse, ToolCall
from adaptive_assistant.registry import ToolRegistry
from adaptive_assistant.tools.base import BaseTool
from adaptive_assistant.tools.file_reader import LocalFileReaderTool
from adaptive_assistant.tools.url_fetcher import UrlFetcherTool


class EchoTool(BaseTool):
    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Echo a value."

    def get_declaration(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                },
                "required": ["value"],
            },
        }

    def execute(self, **kwargs: object) -> dict[str, object]:
        return {"ok": True, "value": kwargs.get("value")}


class FakeClient:
    def __init__(self) -> None:
        self.responses = [
            ModelResponse(
                text="",
                tool_calls=[
                    ToolCall(name="echo", args={"value": "one"}),
                    ToolCall(name="echo", args={"value": "two"}),
                ],
            ),
            ModelResponse(text="Completed", tool_calls=[]),
        ]
        self.batch_sizes: list[int] = []

    def send_user_message(self, text: str) -> ModelResponse:
        return self.responses.pop(0)

    def send_function_responses(self, responses: list[object]) -> ModelResponse:
        self.batch_sizes.append(len(responses))
        return self.responses.pop(0)


class AgentArchitectureTests(unittest.TestCase):
    def test_agent_batches_multiple_tool_calls(self) -> None:
        registry = ToolRegistry()
        registry.register(EchoTool())
        agent = Agent(registry=registry, memory=MemoryManager())
        fake_client = FakeClient()
        agent._client = fake_client  # type: ignore[assignment]

        result = agent.handle_user_message("Use tools")

        self.assertEqual(result, "Completed")
        self.assertEqual(fake_client.batch_sizes, [2])

    def test_agent_surfaces_client_initialization_errors(self) -> None:
        registry = ToolRegistry()
        registry.register(EchoTool())
        agent = Agent(registry=registry, memory=MemoryManager())

        with patch("adaptive_assistant.agent.GeminiClient", side_effect=RuntimeError("boom")):
            result = agent.handle_user_message("hello")

        self.assertIn("Gemini API error: boom", result)


class RegistryAndToolTests(unittest.TestCase):
    def test_duplicate_tool_registration_is_rejected(self) -> None:
        registry = ToolRegistry()
        registry.register(EchoTool())

        with self.assertRaises(ValueError):
            registry.register(EchoTool())

    def test_file_reader_validates_max_chars(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sample = temp_path / "sample.txt"
            sample.write_text("hello world", encoding="utf-8")
            tool = LocalFileReaderTool(allowed_root=temp_path)

            result = tool.execute(path="sample.txt", max_chars="bad")

        self.assertEqual(result["ok"], False)
        self.assertIn("max_chars", result["error"])

    def test_file_reader_blocks_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = LocalFileReaderTool(allowed_root=Path(temp_dir))
            result = tool.execute(path="..\\outside.txt")

        self.assertEqual(result, {"ok": False, "error": "Path is outside allowed directory."})

    @patch('adaptive_assistant.tools.url_fetcher.requests.get')
    def test_url_fetcher_success(self, mock_get) -> None:
        mock_response = unittest.mock.Mock()
        mock_response.text = "Hello World"
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        tool = UrlFetcherTool()
        result = tool.execute(url="https://example.com")

        self.assertEqual(result["ok"], True)
        self.assertEqual(result["content"], "Hello World")
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["content_type"], "text/plain")

    def test_url_fetcher_invalid_url(self) -> None:
        tool = UrlFetcherTool()
        result = tool.execute(url="ftp://example.com")

        self.assertEqual(result["ok"], False)
        self.assertIn("URL must start with http", result["error"])

    def test_url_fetcher_missing_url(self) -> None:
        tool = UrlFetcherTool()
        result = tool.execute()

        self.assertEqual(result["ok"], False)
        self.assertIn("Missing URL", result["error"])


if __name__ == "__main__":
    unittest.main()