# GitHub AI Daily

每天从 GitHub 发现新的 AI 相关项目，并推送到飞书或企业微信。

## 功能

- 通过 GitHub Search API 搜索最近创建或最近活跃的 AI 仓库
- 按关键词、热度、时间窗口过滤
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
- `WEBHOOK_URL`: 飞书或企业微信机器人地址

### GitHub Variables

- `NOTIFY_PROVIDER`: `feishu` 或 `wecom`
- `MAX_PUSH_COUNT`: 每日最大推送数量，默认推荐 `8`
- `MIN_STARS`: 最低 stars，默认推荐 `5`
- `CREATED_DAYS`: 最近创建时间窗口，默认 `1`
- `PUSHED_DAYS`: 最近活跃时间窗口，默认 `1`

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GITHUB_TOKEN=your_github_token
export WEBHOOK_URL=your_webhook_url
export NOTIFY_PROVIDER=feishu
export DRY_RUN=true

python -m src.main
```

`DRY_RUN=true` 时不会真正发送消息，而是直接打印日报内容。

## 推送渠道

### 飞书

- `NOTIFY_PROVIDER=feishu`
- `WEBHOOK_URL` 填飞书群机器人 webhook

### 企业微信

- `NOTIFY_PROVIDER=wecom`
- `WEBHOOK_URL` 填企业微信群机器人 webhook

## 可调配置

- 修改 [config/keywords.json](/Users/xinliqiang/PycharmProjects/codexproject/githubeveryday/config/keywords.json) 可增删关注关键词
- 修改 Actions cron 可调整每日执行时间
- 修改 `data/pushed_projects.json` 可重置历史推送记录
