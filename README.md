[![CI](https://github.com/z13972509570-spec/github-trending-digest/actions/workflows/ci.yml/badge.svg)](https://github.com/z13972509570-spec/github-trending-digest/actions)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)

# 📊 GitHub Trending Digest

> 自动收集 GitHub 热门项目、Star 飙升项目，通过微信每日/每周定时推送

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Cron](https://img.shields.io/badge/Cron-Daily%2FWeekly-orange.svg)]()

## ✨ 功能特性

- 📈 **每日热门** — 自动抓取 GitHub Trending 今日榜
- ⭐ **Star 飙升** — 计算 24 小时内 Star 增长最快的项目
- 🔥 **每周汇总** — 周一早上推送本周热门项目 TOP 20
- 🤖 **AI 筛选** — 智能筛选 AI/开发工具/前端/后端等分类
- 💬 **微信推送** — 通过 QClaw 微信通道定时推送
- 📊 **数据持久化** — 本地 SQLite 存储历史趋势数据

## 🚀 快速开始

### 安装

```bash
pip install -e .
```

### 配置

创建 `.env` 文件：

```bash
# GitHub Token（提高 API 限制）
GITHUB_TOKEN=ghp_xxx

# 微信推送配置（QClaw）
QCLAW_GATEWAY_URL=http://localhost:18789
QCLAW_TOKEN=your_token
WECHAT_TARGET=your_wechat_id

# 推送时间（可选）
DAILY_PUSH_TIME=09:00
WEEKLY_PUSH_TIME=09:00
WEEKLY_PUSH_DAY=1  # 周一
```

### 手动运行

```bash
# 抓取今日热门
python -m trending_digest fetch --type daily

# 抓取本周热门
python -m trending_digest fetch --type weekly

# 发送推送
python -m trending_digest push --target wechat

# 查看历史
python -m trending_digest history --days 7
```

### 定时任务

```bash
# 添加到 crontab
crontab -e

# 每天早上 9:00 推送
0 9 * * * cd /path/to/github-trending-digest && python -m trending_digest fetch-and-push

# 每周一早上 9:00 推送周报
0 9 * * 1 cd /path/to/github-trending-digest && python -m trending_digest fetch-and-push --type weekly
```

## 📋 推送内容示例

### 每日推送

```
📊 GitHub 今日热门 (2026-03-22)

🔥 TOP 5 热门项目

1. awesome-project ⭐ 2.3k (今日 +1.2k)
   📝 项目描述...
   🔗 github.com/user/awesome-project

2. cool-tool ⭐ 1.8k (今日 +800)
   📝 项目描述...
   🔗 github.com/user/cool-tool

📈 分类趋势
• AI/ML: 3 个项目上榜
• 前端: 2 个项目上榜
• 工具: 5 个项目上榜

💡 推荐关注
• trending-repo-1
• trending-repo-2
```

### 每周汇总

```
📊 GitHub 本周热门汇总 (2026-03-17 ~ 2026-03-23)

🏆 TOP 10 飙升项目

1. 🚀 rocket-app
   ⭐ 本周 +5.2k | 总计 12.3k
   📝 高性能火箭发射模拟器
   🏷️ Rust | Simulation

2. 🤖 ai-assistant
   ⭐ 本周 +4.8k | 总计 8.9k
   📝 开源 AI 助手框架
   🏷️ Python | AI

...

📊 分类统计
• AI/ML: 15 个项目
• 前端: 8 个项目
• 后端: 12 个项目
• 工具: 20 个项目
```

## 📁 项目结构

```
github-trending-digest/
├── src/
│   └── trending_digest/
│       ├── __init__.py
│       ├── fetcher.py       # 数据抓取
│       ├── analyzer.py      # 数据分析
│       ├── storage.py       # 数据存储
│       ├── notifier.py      # 推送通知
│       └── scheduler.py     # 定时任务
├── cli/
│   └── main.py              # CLI 入口
├── data/                    # 数据存储
│   └── trending.db
├── docs/                    # 文档
└── tests/
```

## 📄 License

MIT © 2026

---
版本: 1.0.0 | 许可证: MIT | 维护者: @z13972509570-spec
