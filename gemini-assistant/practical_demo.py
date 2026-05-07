#!/usr/bin/env python3
"""
Practical demonstration of the AI Assistant tools.
This script tests the tools directly without requiring the Gemini API.
Run this to verify tool functionality.
"""

from pathlib import Path
from adaptive_assistant.tools import CalculatorTool, LocalFileReaderTool, TextStatsTool, TimeTool


def demo_calculator():
    print("=== Calculator Tool Demo ===")
    tool = CalculatorTool()
    expressions = ["2 + 3", "(10 - 4) * 2", "15 / 3 + 1"]
    for expr in expressions:
        result = tool.execute(expression=expr)
        print(f"Expression: {expr} -> {result}")


def demo_file_reader():
    print("\n=== File Reader Tool Demo ===")
    # Create a temporary file for demo
    demo_file = Path("demo_text.txt")
    demo_file.write_text("This is a sample text file.\nIt has multiple lines.\nFor testing the file reader tool.", encoding="utf-8")

    tool = LocalFileReaderTool(allowed_root=Path.cwd())
    result = tool.execute(path="demo_text.txt", max_chars=50)
    print(f"File content: {result}")

    # Clean up
    demo_file.unlink()


def demo_text_stats():
    print("\n=== Text Stats Tool Demo ===")
    tool = TextStatsTool()
    text = "This is a sample text for analyzing statistics. It contains words and sentences."
    result = tool.execute(text=text)
    print(f"Text stats: {result}")


def demo_time():
    print("\n=== Time Tool Demo ===")
    tool = TimeTool()
    result = tool.execute()
    print(f"Current time: {result}")


if __name__ == "__main__":
    print("Practical Demo of AI Assistant Tools\n")
    demo_calculator()
    demo_file_reader()
    demo_text_stats()
    demo_time()
    print("\nDemo completed successfully!")