from __future__ import annotations

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
    ) -> list[Repository]:
        repositories: dict[str, Repository] = {}

        for query in self._build_queries(include_keywords, created_days, pushed_days):
            payload = self._search_repositories(query=query, per_page=per_page)
            for item in payload.get("items", []):
                repository = Repository.from_api_item(item)
                repositories[repository.full_name] = repository

        return list(repositories.values())

    def _search_repositories(self, query: str, per_page: int) -> dict[str, Any]:
        response = self.session.get(
            f"{self.api_base_url}/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc", "per_page": per_page},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def _build_queries(
        self,
        include_keywords: list[str],
        created_days: int,
        pushed_days: int,
    ) -> list[str]:
        now = datetime.now(timezone.utc)
        created_since = (now - timedelta(days=created_days)).strftime("%Y-%m-%d")
        pushed_since = (now - timedelta(days=pushed_days)).strftime("%Y-%m-%d")
        keyword_groups = _chunk_keywords(include_keywords, size=4)

        queries: list[str] = []
        for group in keyword_groups:
            keyword_expr = " OR ".join(f'"{keyword}"' for keyword in group)
            topic_expr = " OR ".join(f"topic:{keyword}" for keyword in group)
            base_expr = f'(({keyword_expr}) in:name,description OR ({topic_expr}))'
            queries.append(
                f"({base_expr}) created:>={created_since} archived:false fork:false"
            )
            queries.append(
                f"({base_expr}) pushed:>={pushed_since} archived:false fork:false"
            )
        return queries


def _chunk_keywords(values: list[str], size: int) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]
