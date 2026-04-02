from __future__ import annotations

from typing import Any

from adaptive_assistant.tools.base import BaseTool


class ToolRegistry:
    """Factory/registry for tool lookup and execution."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    def get_declarations(self) -> list[dict[str, Any]]:
        return [tool.get_declaration() for tool in self._tools.values()]

    def list_tool_names(self) -> list[str]:
        return list(self._tools)

    def execute(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        if name not in self._tools:
            return {
                "ok": False,
                "error": f"Unknown tool: {name}",
            }

        tool = self._tools[name]
        try:
            return tool.execute(**args)
        except TypeError as exc:
            return {
                "ok": False,
                "error": "Invalid arguments for tool call.",
                "details": str(exc),
            }
        except Exception as exc:  # noqa: BLE001 - defensive boundary
            return {
                "ok": False,
                "error": "Tool execution failed.",
                "details": str(exc),
            }
