from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolCall:
    """Represents a single tool call requested by the model."""

    name: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ToolResponse:
    """Represents a single tool response returned to the model."""

    name: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ModelResponse:
    """Structured LLM response parsed from Gemini output."""

    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
