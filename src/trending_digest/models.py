"""数据模型"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Project(BaseModel):
    """GitHub 项目"""
    name: str = Field(description="项目名称")
    full_name: str = Field(description="完整名称 (owner/repo)")
    description: Optional[str] = Field(None, description="项目描述")
    language: Optional[str] = Field(None, description="编程语言")
    stars: int = Field(0, description="当前 Stars")
    forks: int = Field(0, description="当前 Forks")
    today_stars: int = Field(0, description="今日新增 Stars")
    weekly_stars: int = Field(0, description="本周新增 Stars")
    owner: str = Field(description="所有者")
    url: str = Field(description="项目 URL")
    topics: List[str] = Field(default_factory=list, description="主题标签")
    avatar_url: Optional[str] = None

    @property
    def github_url(self) -> str:
        return f"https://github.com/{self.full_name}"

    @property
    def star_trend(self) -> str:
        """Star 趋势描述"""
        if self.today_stars > 1000:
            return "🔥🔥🔥 爆发式增长"
        elif self.today_stars > 500:
            return "🔥🔥 快速增长"
        elif self.today_stars > 100:
            return "🔥 稳步增长"
        elif self.today_stars > 50:
            return "📈 小幅增长"
        return "📊 稳定"


class TrendReport(BaseModel):
    """趋势报告"""
    report_id: str
    report_type: str = Field(description="daily/weekly")
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    projects: List[Project] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    ai_picks: List[Project] = Field(default_factory=list)
    language_stats: Dict[str, int] = Field(default_factory=dict)

    @property
    def top_project(self) -> Optional[Project]:
        return self.projects[0] if self.projects else None

    def to_markdown(self) -> str:
        """转换为 Markdown"""
        date = datetime.now().strftime("%Y-%m-%d")
        title = "📊 GitHub 每日热门" if self.report_type == "daily" else "📊 GitHub 本周热门汇总"

        md = f"""#{ title} ({date})

## 🏆 TOP 10 热门项目

"""

        for i, p in enumerate(self.projects[:10], 1):
            stars_str = f"+{p.today_stars}" if self.report_type == "daily" else f"+{p.weekly_stars}"
            lang = f" • {p.language}" if p.language else ""
            topics = " • ".join(p.topics[:3]) if p.topics else ""

            md += f"""### {i}. {p.full_name}

| 指标 | 数值 |
|------|------|
| ⭐ Stars | {p.stars:,} ({stars_str} today) |
| 🍴 Forks | {p.forks:,} |
{lang and f'| 🏷️ 语言 | {lang[2:]} |'}
{topics and f'| 🏷️ 标签 | {topics} |'}

{p.description or "暂无描述"}

🔗 [查看项目]({p.github_url})

---

"""

        # 分类统计
        if self.language_stats:
            md += "## 📈 编程语言分布\n\n"
            for lang, count in sorted(self.language_stats.items(), key=lambda x: -x[1])[:10]:
                bar = "▓" * count + "░" * (max(10 - count, 0))
                md += f"- {lang or 'Unknown'}: {bar} {count}\n"

        # AI 精选
        if self.ai_picks:
            md += "\n## 🤖 AI 精选推荐\n\n"
            for p in self.ai_picks[:5]:
                md += f"- **[{p.full_name}]({p.github_url})** — {p.description or '暂无描述'}\n"

        return md

    def to_wechat_message(self) -> str:
        """转换为微信消息格式"""
        date = datetime.now().strftime("%Y-%m-%d")
        title = "📊 GitHub 今日热门" if self.report_type == "daily" else "📊 GitHub 本周汇总"

        msg = f"""{title} {date}

🏆 TOP 5 热门项目

"""

        for i, p in enumerate(self.projects[:5], 1):
            stars_str = f"+{p.today_stars}" if self.report_type == "daily" else f"+{p.weekly_stars}"
            desc = (p.description[:50] + "...") if p.description and len(p.description) > 50 else p.description
            lang = f"[{p.language}]" if p.language else ""

            msg += f"""{i}. {p.full_name} {lang}
   ⭐ {p.stars:,} ({stars_str})
   📝 {desc or '暂无描述'}
   🔗 {p.github_url}

"""

        # AI 精选
        if self.ai_picks:
            msg += "🤖 AI 精选推荐\n\n"
            for p in self.ai_picks[:3]:
                msg += f"• {p.full_name}: {p.description[:30] if p.description else ''}...\n"

        return msg
