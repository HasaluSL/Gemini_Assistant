from __future__ import annotations

import requests
from typing import Any

from adaptive_assistant.tools.base import BaseTool


class UrlFetcherTool(BaseTool):
    @property
    def name(self) -> str:
        return "url_fetcher"

    @property
    def description(self) -> str:
        return "Fetch content from a URL with optional timeout and size limits."

    def get_declaration(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch content from (must be http or https)",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum characters to return (default: 5000)",
                        "default": 5000,
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Request timeout in seconds (default: 10)",
                        "default": 10,
                    }
                },
                "required": ["url"],
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        url = str(kwargs.get("url", "")).strip()
        max_chars = int(kwargs.get("max_chars", 5000))
        timeout = int(kwargs.get("timeout", 10))

        if not url:
            return {"ok": False, "error": "Missing URL argument."}

        if not url.startswith(("http://", "https://")):
            return {"ok": False, "error": "URL must start with http:// or https://"}

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            content = response.text
            if len(content) > max_chars:
                content = content[:max_chars] + "..."

            return {
                "ok": True,
                "content": content,
                "content_length": len(response.text),
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", "unknown")
            }

        except requests.exceptions.RequestException as exc:
            return {"ok": False, "error": f"Request failed: {exc}"}
        except Exception as exc:
            return {"ok": False, "error": f"Unexpected error: {exc}"}