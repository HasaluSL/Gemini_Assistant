from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Contract for all callable assistant tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_declaration(self) -> dict[str, Any]:
        """Return Gemini function declaration schema."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute tool with validated arguments."""
        raise NotImplementedError
