from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.models import Repository


PREFERRED_LANGUAGES = {"Python", "TypeScript", "JavaScript", "Jupyter Notebook", "Go", "Rust"}


@dataclass(slots=True)
class FilterConfig:
    min_stars: int
    max_push_count: int
    timezone: str
    created_days: int
    pushed_days: int
    include_keywords: list[str]
    exclude_keywords: list[str]


def select_repositories(repositories: list[Repository], config: FilterConfig) -> list[Repository]:
    now = datetime.now(ZoneInfo(config.timezone))
    created_threshold = now - timedelta(days=config.created_days)
    pushed_threshold = now - timedelta(days=config.pushed_days)

    filtered: list[Repository] = []
    for repository in repositories:
        if repository.is_fork or repository.is_archived:
            continue
        if repository.stars < config.min_stars:
            continue
        if not repository.description:
            continue
        if _contains_excluded_text(repository, config.exclude_keywords):
            continue
        if not _looks_like_ai_project(repository, config.include_keywords):
            continue
        if not _is_recent_enough(repository, created_threshold, pushed_threshold, config.timezone):
            continue
        filtered.append(repository)

    filtered.sort(key=lambda repo: _score_repository(repo, now, config.include_keywords), reverse=True)
    return filtered[: config.max_push_count]


def _contains_excluded_text(repository: Repository, exclude_keywords: list[str]) -> bool:
    combined = " ".join([repository.name, repository.description, " ".join(repository.topics)]).lower()
    return any(keyword.lower() in combined for keyword in exclude_keywords)


def _looks_like_ai_project(repository: Repository, include_keywords: list[str]) -> bool:
    if not include_keywords:
        return True
    combined = " ".join([repository.name, repository.description, " ".join(repository.topics)]).lower()
    return any(keyword.lower() in combined for keyword in include_keywords)


def _is_recent_enough(
    repository: Repository,
    created_threshold: datetime,
    pushed_threshold: datetime,
    timezone_name: str,
) -> bool:
    zone = ZoneInfo(timezone_name)
    created_at = repository.created_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(zone)
    pushed_at = repository.pushed_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(zone)
    return created_at >= created_threshold or pushed_at >= pushed_threshold


def _score_repository(repository: Repository, now: datetime, include_keywords: list[str]) -> float:
    hours_since_created = max((now - repository.created_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(now.tzinfo)).total_seconds() / 3600, 1)
    hours_since_pushed = max((now - repository.pushed_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(now.tzinfo)).total_seconds() / 3600, 1)
    keyword_hits = sum(
        keyword.lower() in " ".join([repository.name, repository.description, " ".join(repository.topics)]).lower()
        for keyword in include_keywords
    )
    language_bonus = 5 if repository.language in PREFERRED_LANGUAGES else 0
    return (
        repository.stars * 1.8
        + repository.forks * 0.5
        + keyword_hits * 6
        + language_bonus
        + (48 / hours_since_created)
        + (24 / hours_since_pushed)
    )
