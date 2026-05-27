# GitHub Smart Daily

每天从 GitHub 拉取候选项目，使用 DeepSeek 智能分析、筛选和总结，然后推送到飞书或企业微信。

## 功能

- 通过 GitHub Search API 搜索最近创建或最近活跃的候选仓库
- 拉取部分 README 摘要，给 DeepSeek 提供更完整的判断上下文
- 由 DeepSeek 自动完成筛选、分类、总结和排序
- 本地 JSON 去重，避免重复推送
- 同时保留飞书和企业微信 Webhook 推送能力
- 使用 GitHub Actions 定时执行

## 项目结构

```text
.
├── .github/workflows/daily-ai-projects.yml
├── config/keywords.json
├── data/pushed_projects.json
├── requirements.txt
└── src/
```

## 配置

### GitHub Secrets

- `GH_TOKEN`: GitHub Personal Access Token
- `DEEPSEEK_API_KEY`: DeepSeek API Key
- `WEBHOOK_URL`: 飞书或企业微信机器人地址

### GitHub Variables

- `NOTIFY_PROVIDER`: `feishu` 或 `wecom`
- `MAX_PUSH_COUNT`: 每日最大推送数量，默认推荐 `8`
- `CANDIDATE_LIMIT`: 候选仓库数量，默认推荐 `30`
- `README_FETCH_LIMIT`: 拉取 README 的候选仓库数量，默认推荐 `12`
- `DEEPSEEK_MODEL`: 建议 `deepseek-v4-flash`
- `DEEPSEEK_TIMEOUT_SECONDS`: DeepSeek 请求超时秒数，默认推荐 `90`
- `MIN_STARS`: 最低 stars，默认推荐 `5`
- `CREATED_DAYS`: 最近创建时间窗口，默认 `1`
- `PUSHED_DAYS`: 最近活跃时间窗口，默认 `1`

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GITHUB_TOKEN=your_github_token
export DEEPSEEK_API_KEY=your_deepseek_api_key
export WEBHOOK_URL=your_webhook_url
export NOTIFY_PROVIDER=feishu
export DRY_RUN=true
export DEEPSEEK_TIMEOUT_SECONDS=90

python -m src.main
```

`DRY_RUN=true` 时不会真正发送消息，而是直接打印 DeepSeek 生成的日报内容。

## 推送渠道

### 飞书

- `NOTIFY_PROVIDER=feishu`
- `WEBHOOK_URL` 填飞书群机器人 webhook

### 企业微信

- `NOTIFY_PROVIDER=wecom`
- `WEBHOOK_URL` 填企业微信群机器人 webhook

## 可调配置

- 修改 [config/keywords.json](/Users/xinliqiang/PycharmProjects/codexproject/githubeveryday/config/keywords.json) 可调整候选仓库抓取方向
- 修改 Actions cron 可调整每日执行时间
- 修改 `data/pushed_projects.json` 可重置历史推送记录
- `include` 为空时，默认抓取全站最近项目；不为空时，会优先围绕这些关键词抓候选项目
