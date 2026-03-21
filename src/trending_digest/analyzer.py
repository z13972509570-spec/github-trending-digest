"""数据分析与 AI 筛选"""
from typing import List, Dict, Optional
from .models import Project, TrendReport
import logging

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """趋势分析器"""

    # AI 相关关键词
    AI_KEYWORDS = [
        "ai", "machine learning", "deep learning", "neural", "llm", "gpt",
        "chatbot", "nlp", "cv", "computer vision", "transformer",
        "stable diffusion", "diffusion", "generative", "language model",
        "rag", "agent", "copilot", "embedding", "vector"
    ]

    # 开发工具关键词
    DEVTOOL_KEYWORDS = [
        "cli", "tool", "devtool", "sdk", "framework", "library",
        "docker", "kubernetes", "git", "debug", "monitoring"
    ]

    # 前端关键词
    FRONTEND_KEYWORDS = [
        "react", "vue", "angular", "svelte", "next", "nuxt",
        "frontend", "ui", "component", "css", "tailwind"
    ]

    # 后端关键词
    BACKEND_KEYWORDS = [
        "api", "rest", "grpc", "server", "backend", "database",
        "graphql", "microservice", "gateway"
    ]

    def __init__(self):
        pass

    def analyze(self, projects: List[Project], report_type: str = "daily") -> TrendReport:
        """分析项目并生成报告"""
        import uuid
        from datetime import datetime

        # 按 Stars 排序
        sorted_projects = sorted(projects, key=lambda p: p.stars, reverse=True)

        # 语言统计
        language_stats = self._count_languages(sorted_projects)

        # AI 精选
        ai_picks = self._pick_ai_projects(sorted_projects)

        # 计算飙升项目
        if report_type == "daily":
            rising = sorted(projects, key=lambda p: p.today_stars, reverse=True)[:5]
        else:
            rising = sorted(projects, key=lambda p: p.weekly_stars, reverse=True)[:5]

        # 构建摘要
        summary = {
            "total_projects": len(projects),
            "ai_projects": len(ai_picks),
            "rising_projects": len(rising),
            "top_language": max(language_stats.items(), key=lambda x: x[1])[0] if language_stats else "N/A"
        }

        report = TrendReport(
            report_id=f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
            report_type=report_type,
            projects=sorted_projects,
            summary=summary,
            ai_picks=ai_picks,
            language_stats=language_stats
        )

        return report

    def _count_languages(self, projects: List[Project]) -> Dict[str, int]:
        """统计编程语言分布"""
        stats = {}
        for p in projects:
            lang = p.language or "Unknown"
            stats[lang] = stats.get(lang, 0) + 1
        return dict(sorted(stats.items(), key=lambda x: -x[1])[:10])

    def _pick_ai_projects(self, projects: List[Project]) -> List[Project]:
        """AI 精选项目"""
        ai_projects = []

        for p in projects:
            # 检查描述
            desc = (p.description or "").lower()
            topics = " ".join(p.topics).lower() if p.topics else ""
            combined = desc + " " + topics

            # 检查关键词
            for keyword in self.AI_KEYWORDS:
                if keyword in combined:
                    ai_projects.append(p)
                    break

            if len(ai_projects) >= 10:
                break

        return ai_projects

    def categorize(self, projects: List[Project]) -> Dict[str, List[Project]]:
        """分类项目"""
        categories = {
            "ai": [],
            "frontend": [],
            "backend": [],
            "devtools": [],
            "other": []
        }

        for p in projects:
            desc = (p.description or "").lower()
            topics = " ".join(p.topics).lower() if p.topics else ""
            combined = desc + " " + topics

            if any(kw in combined for kw in self.AI_KEYWORDS):
                categories["ai"].append(p)
            elif any(kw in combined for kw in self.FRONTEND_KEYWORDS):
                categories["frontend"].append(p)
            elif any(kw in combined for kw in self.BACKEND_KEYWORDS):
                categories["backend"].append(p)
            elif any(kw in combined for kw in self.DEVTOOL_KEYWORDS):
                categories["devtools"].append(p)
            else:
                categories["other"].append(p)

        return categories

    def compare_with_history(self, current: List[Project], previous: List[Project]) -> Dict:
        """与历史数据对比"""
        prev_names = {p.full_name for p in previous}

        new_entries = [p for p in current if p.full_name not in prev_names]
        rising_fast = sorted(current, key=lambda p: p.today_stars, reverse=True)[:5]

        return {
            "new_entries": new_entries,
            "rising_fast": rising_fast,
            "total_change": len(current) - len(previous)
        }
