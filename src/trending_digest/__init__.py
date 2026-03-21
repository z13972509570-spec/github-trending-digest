"""GitHub Trending Digest — GitHub 热门项目收集与推送"""
__version__ = "1.0.0"

from .fetcher import TrendingFetcher
from .analyzer import TrendAnalyzer
from .storage import TrendStorage
from .notifier import WeChatNotifier
from .models import Project, TrendReport

__all__ = [
    "TrendingFetcher",
    "TrendAnalyzer",
    "TrendStorage", 
    "WeChatNotifier",
    "Project",
    "TrendReport",
]
