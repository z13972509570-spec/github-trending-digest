# 使用指南

## 安装

```bash
pip install -e .
```

## 配置

创建 `.env` 文件：

```bash
# GitHub Token（提高 API 限制）
GITHUB_TOKEN=ghp_xxx

# QClaw Gateway
QCLAW_GATEWAY_URL=http://localhost:18789
QCLAW_TOKEN=your_token

# 微信推送目标
WECHAT_TARGET=your_wechat_id

# 推送时间
DAILY_PUSH_TIME=09:00
```

## 使用

### 手动运行

```bash
# 抓取今日热门
trending-digest fetch --type daily

# 抓取本周热门
trending-digest fetch --type weekly

# 推送微信
trending-digest push --target wechat

# 查看历史
trending-digest history --days 7

# 分析趋势
trending-digest analyze
```

### 定时任务

```bash
# 添加 crontab
crontab -e

# 每天早上 9 点
0 9 * * * cd /path/to/project && python -m trending_digest fetch --type daily && python -m trending_digest push --target wechat
```
