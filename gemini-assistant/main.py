from __future__ import annotations

import os
from pathlib import Path

from adaptive_assistant.agent import Agent
from adaptive_assistant.memory import MemoryManager
from adaptive_assistant.registry import ToolRegistry
from adaptive_assistant.tools import (
    CalculatorTool,
    LocalFileReaderTool,
    TextStatsTool,
    TimeTool,
    WeatherTool,
)


def build_agent() -> Agent:
    registry = ToolRegistry()

    # Strategy registration: add/remove tools without changing Agent internals.
    registry.register(CalculatorTool())
    registry.register(TimeTool())
    registry.register(WeatherTool())
    registry.register(LocalFileReaderTool(allowed_root=Path.cwd()))
    registry.register(TextStatsTool())

    memory = MemoryManager()
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    return Agent(registry=registry, memory=memory, model_name=model_name)


def run_cli() -> None:
    print("Adaptive Gemini Personal Assistant")
    print("Type 'exit' to quit.\n")

    try:
        agent = build_agent()
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"Assistant> Failed to initialize assistant: {exc}")
        return

    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAssistant> Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Assistant> Goodbye!")
            break

        reply = agent.handle_user_message(user_input)
        print(f"Assistant> {reply}\n")


if __name__ == "__main__":
    run_cli()
