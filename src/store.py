from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.models import Repository


class PushStore:
    def __init__(self, store_path: Path) -> None:
        self.store_path = store_path
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, dict[str, str | int]]:
        if not self.store_path.exists():
            return {}
        with self.store_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def filter_new(self, repositories: list[Repository]) -> list[Repository]:
        history = self.load()
        return [repository for repository in repositories if repository.full_name not in history]

    def save_push_results(self, repositories: list[Repository]) -> None:
        history = self.load()
        pushed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for repository in repositories:
            history[repository.full_name] = {
                "first_seen_at": pushed_at,
                "last_pushed_at": pushed_at,
                "stars_when_pushed": repository.stars,
                "html_url": repository.html_url,
            }

        with self.store_path.open("w", encoding="utf-8") as handle:
            json.dump(history, handle, ensure_ascii=False, indent=2, sort_keys=True)
