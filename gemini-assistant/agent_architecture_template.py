"""Architectural template reference for the assignment.

This file mirrors the required components and can be used by reviewers as a
quick structure map. Implementation lives in the adaptive_assistant package.
"""

from adaptive_assistant.agent import Agent
from adaptive_assistant.memory import MemoryManager
from adaptive_assistant.registry import ToolRegistry
from adaptive_assistant.tools.base import BaseTool

__all__ = ["Agent", "MemoryManager", "ToolRegistry", "BaseTool"]
