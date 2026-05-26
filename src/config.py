from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_KEYWORDS_PATH = ROOT_DIR / "config" / "keywords.json"
DEFAULT_STORE_PATH = ROOT_DIR / "data" / "pushed_projects.json"


@dataclass(slots=True)
class AppConfig:
    github_token: str
    github_api_base_url: str
    timezone: str
    keywords_path: Path
    store_path: Path
    notify_provider: str
    webhook_url: str
    max_push_count: int
    min_stars: int
    created_days: int
    pushed_days: int
    request_timeout_seconds: int
    dry_run: bool

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            github_token=_required("GITHUB_TOKEN"),
            github_api_base_url=os.getenv("GITHUB_API_BASE_URL", "https://api.github.com"),
            timezone=os.getenv("TZ", "Asia/Shanghai"),
            keywords_path=Path(os.getenv("KEYWORDS_PATH", str(DEFAULT_KEYWORDS_PATH))),
            store_path=Path(os.getenv("STORE_PATH", str(DEFAULT_STORE_PATH))),
            notify_provider=os.getenv("NOTIFY_PROVIDER", "feishu").strip().lower(),
            webhook_url=_required("WEBHOOK_URL"),
            max_push_count=int(os.getenv("MAX_PUSH_COUNT", "8")),
            min_stars=int(os.getenv("MIN_STARS", "5")),
            created_days=int(os.getenv("CREATED_DAYS", "1")),
            pushed_days=int(os.getenv("PUSHED_DAYS", "1")),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
            dry_run=os.getenv("DRY_RUN", "false").strip().lower() == "true",
        )

    def load_keywords(self) -> dict[str, list[str]]:
        with self.keywords_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value
