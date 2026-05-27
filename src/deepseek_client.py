from __future__ import annotations

import json
import re
from typing import Any

import requests


class DeepSeekClient:
    def __init__(self, api_key: str, api_base_url: str, model: str, timeout_seconds: int) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        }
        response = self.session.post(
            f"{self.api_base_url}/chat/completions",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        message = body["choices"][0]["message"]["content"]
        return _extract_json_object(message)


def _extract_json_object(content: str) -> dict[str, Any]:
    fenced_match = re.search(r"```json\s*(\{.*\})\s*```", content, re.DOTALL)
    if fenced_match:
        return json.loads(fenced_match.group(1))

    raw_match = re.search(r"(\{.*\})", content, re.DOTALL)
    if raw_match:
        return json.loads(raw_match.group(1))

    raise ValueError("DeepSeek response does not contain a valid JSON object.")
