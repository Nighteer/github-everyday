from __future__ import annotations

from typing import Protocol

import requests


class Notifier(Protocol):
    def send(self, content: str) -> None:
        ...


class FeishuNotifier:
    def __init__(self, webhook_url: str, timeout_seconds: int) -> None:
        self.webhook_url = webhook_url
        self.timeout_seconds = timeout_seconds

    def send(self, content: str) -> None:
        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "AI GitHub Daily",
                        "content": [[{"tag": "text", "text": content}]],
                    }
                }
            },
        }
        _post(self.webhook_url, payload, self.timeout_seconds)


class WeComNotifier:
    def __init__(self, webhook_url: str, timeout_seconds: int) -> None:
        self.webhook_url = webhook_url
        self.timeout_seconds = timeout_seconds

    def send(self, content: str) -> None:
        payload = {"msgtype": "markdown", "markdown": {"content": content}}
        _post(self.webhook_url, payload, self.timeout_seconds)


def build_notifier(provider: str, webhook_url: str, timeout_seconds: int) -> Notifier:
    normalized = provider.strip().lower()
    if normalized in {"feishu", "lark"}:
        return FeishuNotifier(webhook_url, timeout_seconds)
    if normalized in {"wecom", "wechat_work", "qywx"}:
        return WeComNotifier(webhook_url, timeout_seconds)
    raise ValueError(f"Unsupported notify provider: {provider}")


def _post(webhook_url: str, payload: dict, timeout_seconds: int) -> None:
    response = requests.post(webhook_url, json=payload, timeout=timeout_seconds)
    response.raise_for_status()
