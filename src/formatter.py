from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from src.models import Repository
from src.summarizer import DailySummary


def build_markdown_report(repositories: list[Repository], timezone_name: str) -> str:
    today = datetime.now(ZoneInfo(timezone_name)).strftime("%Y-%m-%d")
    if not repositories:
        return (
            f"## {today} AI GitHub Daily\n"
            "今日没有发现符合条件的高质量 AI 新项目。"
        )

    lines = [f"## {today} AI GitHub Daily", f"今日发现 {len(repositories)} 个值得关注的项目：", ""]
    for index, repository in enumerate(repositories, start=1):
        summary = repository.description or "暂无描述"
        topics = ", ".join(repository.topics[:3]) if repository.topics else "AI"
        lines.append(
            "\n".join(
                [
                    f"{index}. **{repository.full_name}**",
                    f"   - 简介：{summary}",
                    f"   - Stars：{repository.stars} | Language：{repository.language} | Topics：{topics}",
                    f"   - 链接：{repository.html_url}",
                ]
            )
        )
        lines.append("")
    return "\n".join(lines).strip()


def build_summary_report(summary: DailySummary, repositories_by_name: dict[str, Repository], timezone_name: str) -> str:
    today = datetime.now(ZoneInfo(timezone_name)).strftime("%Y-%m-%d")
    lines = [f"## {today} {summary.title}", summary.overview, ""]
    if not summary.items:
        lines.append("今天没有值得推送的项目。")
        return "\n".join(lines).strip()

    for index, item in enumerate(summary.items, start=1):
        repository = repositories_by_name.get(item.full_name)
        if repository is None:
            continue
        lines.extend(
            [
                f"{index}. **{repository.full_name}** | {item.category}",
                f"   - 总结：{item.summary}",
                f"   - 关注点：{item.reason}",
                f"   - Stars：{repository.stars} | Language：{repository.language}",
                f"   - 链接：{repository.html_url}",
                "",
            ]
        )
    return "\n".join(lines).strip()
