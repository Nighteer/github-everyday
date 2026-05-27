from __future__ import annotations

from src.config import AppConfig
from src.deepseek_client import DeepSeekClient
from src.filters import FilterConfig, select_repositories
from src.formatter import build_summary_report
from src.github_client import GitHubClient
from src.notifier import build_notifier
from src.store import PushStore
from src.summarizer import GitHubDailySummarizer


def main() -> None:
    config = AppConfig.from_env()
    keywords = config.load_keywords()

    client = GitHubClient(
        token=config.github_token,
        api_base_url=config.github_api_base_url,
        timeout_seconds=config.request_timeout_seconds,
    )
    deepseek_client = DeepSeekClient(
        api_key=config.deepseek_api_key,
        api_base_url=config.deepseek_api_base_url,
        model=config.deepseek_model,
        timeout_seconds=config.deepseek_timeout_seconds,
    )
    store = PushStore(config.store_path)
    notifier = build_notifier(config.notify_provider, config.webhook_url, config.request_timeout_seconds)
    summarizer = GitHubDailySummarizer(deepseek_client, max_push_count=config.max_push_count)

    repositories, query_mode = client.fetch_candidates(
        include_keywords=keywords["include"],
        created_days=config.created_days,
        pushed_days=config.pushed_days,
        per_page=config.candidate_limit,
        readme_fetch_limit=config.readme_fetch_limit,
    )
    print(
        f"[debug] query_mode={query_mode} "
        f"keywords={len(keywords['include'])} fetched_candidates={len(repositories)}"
    )
    candidates = select_repositories(
        repositories,
        FilterConfig(
            min_stars=config.min_stars,
            max_push_count=config.candidate_limit,
            timezone=config.timezone,
            created_days=config.created_days,
            pushed_days=config.pushed_days,
            include_keywords=keywords["include"],
            exclude_keywords=keywords["exclude"],
        ),
    )
    print(f"[debug] filtered_candidates={len(candidates)}")
    fresh_candidates = store.filter_new(candidates)
    print(f"[debug] fresh_candidates={len(fresh_candidates)}")
    summary = summarizer.summarize(fresh_candidates[: config.candidate_limit])
    selected_repository_names = {item.full_name for item in summary.items}
    selected_repositories = [
        repository for repository in fresh_candidates if repository.full_name in selected_repository_names
    ]
    print(f"[debug] selected_repositories={len(selected_repositories)}")
    content = build_summary_report(
        summary,
        repositories_by_name={repository.full_name: repository for repository in fresh_candidates},
        timezone_name=config.timezone,
    )

    if config.dry_run:
        print(content)
        return

    notifier.send(content)
    if selected_repositories:
        store.save_push_results(selected_repositories)


if __name__ == "__main__":
    main()
