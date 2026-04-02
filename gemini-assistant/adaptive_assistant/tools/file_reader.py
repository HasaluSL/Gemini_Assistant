from __future__ import annotations

from pathlib import Path
from typing import Any

from adaptive_assistant.tools.base import BaseTool


class LocalFileReaderTool(BaseTool):
    """Custom tool: reads a local text file from an allowed root."""

    def __init__(self, allowed_root: Path | None = None) -> None:
        self._allowed_root = (allowed_root or Path.cwd()).resolve()

    @property
    def name(self) -> str:
        return "read_local_file"

    @property
    def description(self) -> str:
        return "Read UTF-8 text content from a local file within allowed directory."

    def get_declaration(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path within the current project folder.",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum characters to return. Default 2000.",
                    },
                },
                "required": ["path"],
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        path_value = str(kwargs.get("path", "")).strip()
        if not path_value:
            return {"ok": False, "error": "Missing path argument."}

        try:
            max_chars = int(kwargs.get("max_chars", 2000))
        except (TypeError, ValueError):
            return {"ok": False, "error": "max_chars must be an integer."}

        if max_chars <= 0:
            return {"ok": False, "error": "max_chars must be greater than zero."}

        try:
            target = (self._allowed_root / path_value).resolve()
            target.relative_to(self._allowed_root)
        except Exception:
            return {"ok": False, "error": "Path is outside allowed directory."}

        if not target.exists() or not target.is_file():
            return {"ok": False, "error": "File not found."}

        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return {"ok": False, "error": "File is not UTF-8 text."}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"Failed to read file: {exc}"}

        return {
            "ok": True,
            "path": str(target),
            "content": content[:max_chars],
            "truncated": len(content) > max_chars,
        }
