from __future__ import annotations

import re
from typing import Any

from adaptive_assistant.tools.base import BaseTool


class TextStatsTool(BaseTool):
    """Custom tool: returns basic text statistics."""

    @property
    def name(self) -> str:
        return "text_stats"

    @property
    def description(self) -> str:
        return "Analyze text and return character, word, and sentence counts."

    def get_declaration(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Input text to analyze.",
                    }
                },
                "required": ["text"],
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        text = str(kwargs.get("text", ""))
        if not text.strip():
            return {"ok": False, "error": "Missing text argument."}

        words = re.findall(r"\b\w+\b", text)
        sentences = [part for part in re.split(r"[.!?]+", text) if part.strip()]

        return {
            "ok": True,
            "characters": len(text),
            "characters_no_spaces": len(text.replace(" ", "")),
            "word_count": len(words),
            "sentence_count": len(sentences),
        }
