from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from src.models import Repository


class GitHubClient:
    def __init__(self, token: str, api_base_url: str, timeout_seconds: int) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "github-ai-daily-bot",
            }
        )

    def fetch_candidates(
        self,
        include_keywords: list[str],
        created_days: int,
        pushed_days: int,
        per_page: int = 50,
        readme_fetch_limit: int = 0,
    ) -> tuple[list[Repository], str]:
        repositories: dict[str, Repository] = {}
        query_mode = "keyword"

        for query in self._build_queries(include_keywords, created_days, pushed_days):
            payload = self._search_repositories(query=query, per_page=per_page)
            for item in payload.get("items", []):
                repository = Repository.from_api_item(item)
                repositories[repository.full_name] = repository

        if not repositories and include_keywords:
            query_mode = "fallback_global"
            for query in self._build_queries([], created_days, pushed_days):
                payload = self._search_repositories(query=query, per_page=per_page)
                for item in payload.get("items", []):
                    repository = Repository.from_api_item(item)
                    repositories[repository.full_name] = repository

        candidates = sorted(
            repositories.values(),
            key=lambda repo: (repo.stars, repo.forks, repo.pushed_at),
            reverse=True,
        )
        for repository in candidates[:readme_fetch_limit]:
            repository.readme_excerpt = self._fetch_readme_excerpt(repository)
        return candidates, query_mode

    def _search_repositories(self, query: str, per_page: int) -> dict[str, Any]:
        response = self.session.get(
            f"{self.api_base_url}/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc", "per_page": per_page},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def _fetch_readme_excerpt(self, repository: Repository, max_chars: int = 2000) -> str:
        response = self.session.get(
            f"{self.api_base_url}/repos/{repository.full_name}/readme",
            headers={"Accept": "application/vnd.github+json"},
            timeout=self.timeout_seconds,
        )
        if response.status_code == 404:
            return ""
        response.raise_for_status()
        payload = response.json()
        content = payload.get("content")
        if not content:
            return ""
        decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
        cleaned = "\n".join(line.strip() for line in decoded.splitlines() if line.strip())
        return cleaned[:max_chars]

    def _build_queries(
        self,
        include_keywords: list[str],
        created_days: int,
        pushed_days: int,
    ) -> list[str]:
        now = datetime.now(timezone.utc)
        created_since = (now - timedelta(days=created_days)).strftime("%Y-%m-%d")
        pushed_since = (now - timedelta(days=pushed_days)).strftime("%Y-%m-%d")
        if not include_keywords:
            return [
                f"created:>={created_since} archived:false fork:false",
                f"pushed:>={pushed_since} archived:false fork:false",
            ]

        keyword_groups = _chunk_keywords(include_keywords, size=3)

        queries: list[str] = []
        for group in keyword_groups:
            name_desc_expr = " OR ".join(f'"{keyword}" in:name,description' for keyword in group)
            topic_keywords = [keyword for keyword in group if _supports_topic_query(keyword)]
            if topic_keywords:
                topic_expr = " OR ".join(f"topic:{keyword.lower()}" for keyword in topic_keywords)
                base_expr = f"({name_desc_expr} OR {topic_expr})"
            else:
                base_expr = f"({name_desc_expr})"
            queries.append(
                f"({base_expr}) created:>={created_since} archived:false fork:false"
            )
            queries.append(
                f"({base_expr}) pushed:>={pushed_since} archived:false fork:false"
            )
        return queries


def _chunk_keywords(values: list[str], size: int) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def _supports_topic_query(keyword: str) -> bool:
    return " " not in keyword and keyword.isascii()
