from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Repository:
    id: int
    full_name: str
    name: str
    html_url: str
    description: str
    language: str
    stars: int
    forks: int
    topics: list[str]
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    is_fork: bool
    is_archived: bool
    default_branch: str
    owner_login: str
    readme_excerpt: str = ""

    @classmethod
    def from_api_item(cls, item: dict[str, Any]) -> "Repository":
        return cls(
            id=item["id"],
            full_name=item["full_name"],
            name=item["name"],
            html_url=item["html_url"],
            description=(item.get("description") or "").strip(),
            language=item.get("language") or "Unknown",
            stars=int(item.get("stargazers_count") or 0),
            forks=int(item.get("forks_count") or 0),
            topics=item.get("topics") or [],
            created_at=_parse_github_datetime(item["created_at"]),
            updated_at=_parse_github_datetime(item["updated_at"]),
            pushed_at=_parse_github_datetime(item["pushed_at"]),
            is_fork=bool(item.get("fork")),
            is_archived=bool(item.get("archived")),
            default_branch=item.get("default_branch") or "main",
            owner_login=item["owner"]["login"],
            readme_excerpt="",
        )


def _parse_github_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
