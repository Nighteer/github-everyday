from __future__ import annotations

import json
from dataclasses import dataclass

from src.deepseek_client import DeepSeekClient
from src.models import Repository


@dataclass(slots=True)
class SummaryItem:
    full_name: str
    category: str
    summary: str
    reason: str


@dataclass(slots=True)
class DailySummary:
    title: str
    overview: str
    items: list[SummaryItem]


class GitHubDailySummarizer:
    def __init__(self, client: DeepSeekClient, max_push_count: int) -> None:
        self.client = client
        self.max_push_count = max_push_count

    def summarize(self, repositories: list[Repository]) -> DailySummary:
        if not repositories:
            return DailySummary(
                title="GitHub 每日项目简报",
                overview="今天没有采集到符合候选条件的项目。",
                items=[],
            )

        system_prompt = (
            "你是一个负责整理 GitHub 新项目日报的智能分析助手。"
            "你会从候选仓库中挑出最值得关注的项目，优先关注 AI、Agent、RAG、开发者工具、自动化和效率工具。"
            "如果候选中 AI 项目不多，也可以保留少量高质量通用技术项目。"
            "请严格返回 JSON，不要输出额外解释。"
        )
        user_prompt = (
            "请基于下面的候选 GitHub 仓库，筛选出最值得推送到团队群里的项目，并输出结构化 JSON。\n"
            f"最多保留 {self.max_push_count} 个项目。\n"
            "排序要求：优先新鲜度、可用性、讨论度、技术亮点。\n"
            "对每个项目给出：category、summary、reason。\n"
            "JSON 格式必须是：\n"
            '{\n'
            '  "title": "日报标题",\n'
            '  "overview": "2-3句总览",\n'
            '  "items": [\n'
            '    {\n'
            '      "full_name": "owner/repo",\n'
            '      "category": "分类",\n'
            '      "summary": "一句话总结",\n'
            '      "reason": "为什么值得关注"\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "候选仓库如下：\n"
            f"{json.dumps([_repository_payload(repo) for repo in repositories], ensure_ascii=False, indent=2)}"
        )
        payload = self.client.complete_json(system_prompt=system_prompt, user_prompt=user_prompt)
        items = [
            SummaryItem(
                full_name=item["full_name"],
                category=item["category"],
                summary=item["summary"],
                reason=item["reason"],
            )
            for item in payload.get("items", [])[: self.max_push_count]
        ]
        return DailySummary(
            title=payload.get("title", "GitHub 每日项目简报"),
            overview=payload.get("overview", "已生成今日项目摘要。"),
            items=items,
        )


def _repository_payload(repository: Repository) -> dict[str, object]:
    return {
        "full_name": repository.full_name,
        "description": repository.description,
        "language": repository.language,
        "stars": repository.stars,
        "forks": repository.forks,
        "topics": repository.topics[:8],
        "created_at": repository.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pushed_at": repository.pushed_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "html_url": repository.html_url,
        "readme_excerpt": repository.readme_excerpt[:500],
    }
