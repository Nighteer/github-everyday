from __future__ import annotations

from src.config import AppConfig
from src.filters import FilterConfig, select_repositories
from src.formatter import build_markdown_report
from src.github_client import GitHubClient
from src.notifier import build_notifier
from src.store import PushStore


def main() -> None:
    config = AppConfig.from_env()
    keywords = config.load_keywords()

    client = GitHubClient(
        token=config.github_token,
        api_base_url=config.github_api_base_url,
        timeout_seconds=config.request_timeout_seconds,
    )
    store = PushStore(config.store_path)
    notifier = build_notifier(config.notify_provider, config.webhook_url, config.request_timeout_seconds)

    repositories = client.fetch_candidates(
        include_keywords=keywords["include"],
        created_days=config.created_days,
        pushed_days=config.pushed_days,
    )
    selected = select_repositories(
        repositories,
        FilterConfig(
            min_stars=config.min_stars,
            max_push_count=config.max_push_count,
            timezone=config.timezone,
            created_days=config.created_days,
            pushed_days=config.pushed_days,
            include_keywords=keywords["include"],
            exclude_keywords=keywords["exclude"],
        ),
    )
    new_repositories = store.filter_new(selected)
    content = build_markdown_report(new_repositories, config.timezone)

    if config.dry_run:
        print(content)
        return

    notifier.send(content)
    if new_repositories:
        store.save_push_results(new_repositories)


if __name__ == "__main__":
    main()
