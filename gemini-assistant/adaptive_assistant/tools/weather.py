from __future__ import annotations

from typing import Any

import requests

from adaptive_assistant.tools.base import BaseTool


class WeatherTool(BaseTool):
    @property
    def name(self) -> str:
        return "weather_lookup"

    @property
    def description(self) -> str:
        return "Get current weather for a city using wttr.in service."

    def get_declaration(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. Riga",
                    }
                },
                "required": ["city"],
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        city = str(kwargs.get("city", "")).strip()
        if not city:
            return {"ok": False, "error": "Missing city argument."}

        url = f"https://wttr.in/{city}?format=j1"
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "adaptive-gemini-assistant/1.0"},
            )
            response.raise_for_status()
            data = response.json()
            current = data.get("current_condition", [{}])[0]
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"Weather lookup failed: {exc}"}

        if not current:
            return {"ok": False, "error": f"No weather data found for '{city}'."}

        return {
            "ok": True,
            "city": city,
            "temperature_c": current.get("temp_C"),
            "humidity": current.get("humidity"),
            "description": (current.get("weatherDesc") or [{"value": "unknown"}])[0].get("value"),
        }
