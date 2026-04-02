from __future__ import annotations

from typing import Any

from adaptive_assistant.tools.base import BaseTool


class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Evaluate a basic arithmetic expression safely."

    def get_declaration(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression, e.g. (4 + 2) * 8 / 3",
                    }
                },
                "required": ["expression"],
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        expression = str(kwargs.get("expression", "")).strip()
        if not expression:
            return {"ok": False, "error": "Missing expression argument."}

        allowed_chars = set("0123456789+-*/(). %")
        if any(ch not in allowed_chars for ch in expression):
            return {
                "ok": False,
                "error": "Expression contains unsupported characters.",
            }

        try:
            result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307 - constrained input
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"Calculation failed: {exc}"}

        return {"ok": True, "result": result}
