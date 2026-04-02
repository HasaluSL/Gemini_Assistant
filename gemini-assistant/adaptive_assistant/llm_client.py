from __future__ import annotations

import os
from typing import Any

import google.generativeai as genai

from adaptive_assistant.models import ModelResponse, ToolCall, ToolResponse

SYSTEM_INSTRUCTION = """You are an adaptive personal assistant running in a CLI.
Use natural language for normal answers.
Use tools only when they are needed to answer accurately or to inspect local project files.
When tool output contains an error, explain the failure clearly and continue helping when possible.
If a request can be answered directly, do not call a tool.
"""


class GeminiClient:
    """Gemini wrapper responsible for model calls and response parsing."""

    def __init__(
        self,
        model_name: str,
        tool_declarations: list[dict[str, Any]],
        system_instruction: str = SYSTEM_INSTRUCTION,
    ) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")

        genai.configure(api_key=api_key)

        self._model = genai.GenerativeModel(
            model_name=model_name,
            tools=[{"function_declarations": tool_declarations}],
            system_instruction=system_instruction,
        )
        self._chat = self._model.start_chat(history=[])

    def send_user_message(self, text: str) -> ModelResponse:
        response = self._chat.send_message(text)
        return self._parse_response(response)

    def send_function_responses(self, responses: list[ToolResponse]) -> ModelResponse:
        parts = [
            genai.protos.Part(
                function_response=genai.protos.FunctionResponse(
                    name=response.name,
                    response=response.payload,
                )
            )
            for response in responses
        ]
        response = self._chat.send_message(parts)
        return self._parse_response(response)

    def _parse_response(self, response: Any) -> ModelResponse:
        text_chunks: list[str] = []
        tool_calls: list[ToolCall] = []

        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            if not content:
                continue

            for part in getattr(content, "parts", []) or []:
                part_text = getattr(part, "text", None)
                if part_text:
                    text_chunks.append(part_text)

                function_call = getattr(part, "function_call", None)
                if function_call:
                    args = dict(getattr(function_call, "args", {}) or {})
                    tool_calls.append(ToolCall(name=function_call.name, args=args))

        merged_text = "\n".join(chunk.strip() for chunk in text_chunks if chunk.strip())
        return ModelResponse(text=merged_text, tool_calls=tool_calls)
