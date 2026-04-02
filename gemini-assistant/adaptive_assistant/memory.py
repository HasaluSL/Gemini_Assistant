from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MemoryTurn:
    role: str
    content: str


@dataclass(slots=True)
class MemoryManager:
    """Stores conversation turns for the current CLI session."""

    _turns: list[MemoryTurn] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self._turns.append(MemoryTurn(role=role, content=content))

    def all_turns(self) -> list[MemoryTurn]:
        return list(self._turns)

    def pretty_history(self, limit: int = 12) -> str:
        recent = self._turns[-limit:]
        return "\n".join(f"{turn.role}: {turn.content}" for turn in recent)
