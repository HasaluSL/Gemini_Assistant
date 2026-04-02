from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from adaptive_assistant.tools.base import BaseTool


class TimeTool(BaseTool):
    @property
    def name(self) -> str:
        return "current_time"

    @property
    def description(self) -> str:
        return "Get the current local and UTC time."

    def get_declaration(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        local_now = datetime.now().astimezone()
        utc_now = datetime.now(timezone.utc)
        return {
            "ok": True,
            "local_time": local_now.isoformat(),
            "utc_time": utc_now.isoformat(),
            "timezone": str(local_now.tzinfo),
        }
