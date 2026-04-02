from __future__ import annotations

from adaptive_assistant.llm_client import GeminiClient
from adaptive_assistant.memory import MemoryManager
from adaptive_assistant.models import ToolResponse
from adaptive_assistant.registry import ToolRegistry


class Agent:
    """Coordinates ReAct-style reasoning with Gemini and external tools."""

    def __init__(
        self,
        registry: ToolRegistry,
        memory: MemoryManager,
        model_name: str = "gemini-1.5-flash",
        max_steps: int = 6,
    ) -> None:
        self._registry = registry
        self._memory = memory
        self._model_name = model_name
        self._max_steps = max_steps
        self._client: GeminiClient | None = None

    def _get_client(self) -> GeminiClient:
        if self._client is None:
            self._client = GeminiClient(
                model_name=self._model_name,
                tool_declarations=self._registry.get_declarations(),
            )
        return self._client

    def handle_user_message(self, message: str) -> str:
        self._memory.add("user", message)

        try:
            model_response = self._get_client().send_user_message(message)
        except Exception as exc:  # noqa: BLE001 - API/runtime boundary
            err = f"Gemini API error: {exc}"
            self._memory.add("assistant", err)
            return err

        step = 0
        while step < self._max_steps and model_response.tool_calls:
            tool_responses: list[ToolResponse] = []
            for tool_call in model_response.tool_calls:
                tool_result = self._registry.execute(tool_call.name, tool_call.args)
                self._memory.add("tool", f"{tool_call.name}({tool_call.args}) -> {tool_result}")
                tool_responses.append(ToolResponse(name=tool_call.name, payload=tool_result))

            try:
                model_response = self._get_client().send_function_responses(tool_responses)
            except Exception as exc:  # noqa: BLE001 - API/runtime boundary
                err = f"Gemini API error: {exc}"
                self._memory.add("assistant", err)
                return err
            step += 1

        if model_response.tool_calls:
            final_text = (
                f"I stopped after {self._max_steps} reasoning steps without reaching a final answer. "
                "Please refine the request and try again."
            )
            self._memory.add("assistant", final_text)
            return final_text

        final_text = model_response.text.strip() or "I could not produce a final answer."
        self._memory.add("assistant", final_text)
        return final_text
