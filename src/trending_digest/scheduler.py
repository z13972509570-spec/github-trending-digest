"""定时任务调度"""
import schedule
import time
import logging
from typing import Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TrendingScheduler:
    """定时任务调度器"""

    def __init__(self):
        self.jobs = []

    def add_daily_job(self, job: Callable, time_str: str = "09:00"):
        """添加每日任务"""
        schedule.every().day.at(time_str).do(job)
        self.jobs.append(("daily", time_str, job))
        logger.info(f"Added daily job at {time_str}")

    def add_weekly_job(self, job: Callable, day: int = 0, time_str: str = "09:00"):
        """添加每周任务（day: 0=周一, 6=周日）"""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_name = days[day]

        getattr(schedule.every(), day_name).at(time_str).do(job)
        self.jobs.append((f"weekly-{day_name}", time_str, job))
        logger.info(f"Added weekly job on {day_name} at {time_str}")

    def run_pending(self):
        """运行待执行任务"""
        schedule.run_pending()

    def run_forever(self):
        """持续运行"""
        logger.info("Scheduler started")
        while True:
            schedule.run_pending()
            time.sleep(60)

    def list_jobs(self) -> list:
        """列出所有任务"""
        return self.jobs


def run_daily_task():
    """每日任务"""
    from .fetcher import TrendingFetcher
    from .analyzer import TrendAnalyzer
    from .storage import TrendStorage
    from .notifier import WeChatNotifier

    logger.info("Running daily task...")

    # 抓取数据
    fetcher = TrendingFetcher()
    projects = fetcher.fetch_trending(since="daily")

    # 分析
    analyzer = TrendAnalyzer()
    report = analyzer.analyze(projects, "daily")

    # 存储
    storage = TrendStorage()
    storage.save_projects(projects, "daily")
    storage.save_report(report)

    # 推送
    notifier = WeChatNotifier()
    notifier.send_report(report)

    logger.info(f"Daily task completed: {len(projects)} projects")


def run_weekly_task():
    """每周任务"""
    from .fetcher import TrendingFetcher
    from .analyzer import TrendAnalyzer
    from .storage import TrendStorage
    from .notifier import WeChatNotifier

    logger.info("Running weekly task...")

    # 抓取数据
    fetcher = TrendingFetcher()
    projects = fetcher.fetch_trending(since="weekly")

    # 分析
    analyzer = TrendAnalyzer()
    report = analyzer.analyze(projects, "weekly")

    # 存储
    storage = TrendStorage()
    storage.save_projects(projects, "weekly")
    storage.save_report(report)

    # 推送
    notifier = WeChatNotifier()
    notifier.send_report(report)

    logger.info(f"Weekly task completed: {len(projects)} projects")
