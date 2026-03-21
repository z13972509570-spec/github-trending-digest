"""GitHub Trending 数据抓取"""
import httpx
from typing import List, Optional, Dict
from datetime import datetime
from bs4 import BeautifulSoup
from .models import Project
import logging

logger = logging.getLogger(__name__)


class TrendingFetcher:
    """GitHub Trending 抓取器"""

    BASE_URL = "https://github.com"
    TRENDING_URL = "https://github.com/trending"

    def __init__(self, github_token: Optional[str] = None):
        self.token = github_token
        self.session = httpx.Client(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )

    def _get_headers(self) -> Dict:
        headers = {}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def fetch_trending(self, language: Optional[str] = None, since: str = "daily") -> List[Project]:
        """抓取 Trending 项目"""
        url = self.TRENDING_URL
        if language:
            url += f"/{language}"
        url += f"?since={since}"

        logger.info(f"Fetching trending: {url}")

        try:
            response = self.session.get(url, headers=self._get_headers())
            response.raise_for_status()
            return self._parse_trending(response.text, since)
        except Exception as e:
            logger.error(f"Failed to fetch trending: {e}")
            return []

    def _parse_trending(self, html: str, since: str) -> List[Project]:
        """解析 Trending 页面"""
        soup = BeautifulSoup(html, "lxml")
        projects = []

        # 新版选择器
        articles = soup.select("article.Box-row")

        for article in articles:
            try:
                # 项目链接
                link = article.select_one("h2 a")
                if not link:
                    continue

                full_name = link.get("href", "").strip("/")
                if not full_name or "/" not in full_name:
                    continue

                parts = full_name.split("/")
                owner = parts[0]
                name = parts[1] if len(parts) > 1 else parts[0]

                # 描述
                desc_elem = article.select_one("p")
                description = desc_elem.get_text(strip=True) if desc_elem else None

                # Stars - 查找带 star 图标的 span
                stars_text = "0"
                stars_elem = article.select_one("a[href$='/stargazers']")
                if stars_elem:
                    stars_text = stars_elem.get_text(strip=True)
                stars = self._parse_number(stars_text)

                # Forks
                forks_text = "0"
                forks_elem = article.select_one("a[href$='/forks']")
                if forks_elem:
                    forks_text = forks_elem.get_text(strip=True)
                forks = self._parse_number(forks_text)

                # 语言
                lang_elem = article.select_one('[itemprop="programmingLanguage"]')
                language = lang_elem.get_text(strip=True) if lang_elem else None

                # 今日/本周新增 - 查找 "X stars today" 文本
                today_stars = 0
                weekly_stars = 0
                all_text = article.get_text()
                import re
                star_match = re.search(r'([\d,]+)\s*stars?\s*(today|this week|this month)', all_text, re.I)
                if star_match:
                    count = self._parse_number(star_match.group(1))
                    period = star_match.group(2).lower()
                    if 'today' in period:
                        today_stars = count
                    elif 'week' in period:
                        weekly_stars = count

                project = Project(
                    name=name,
                    full_name=full_name,
                    description=description,
                    language=language,
                    stars=stars,
                    forks=forks,
                    today_stars=today_stars,
                    weekly_stars=weekly_stars,
                    owner=owner,
                    url=f"https://github.com/{full_name}",
                    topics=[]
                )
                projects.append(project)

            except Exception as e:
                logger.warning(f"Failed to parse project: {e}")
                continue

        return projects

    def _parse_number(self, text: str) -> int:
        """解析数字"""
        text = str(text).strip().upper().replace(",", "")
        multipliers = {"K": 1000, "M": 1000000}

        for suffix, mult in multipliers.items():
            if suffix in text:
                try:
                    return int(float(text.replace(suffix, "")) * mult)
                except:
                    return 0

        try:
            return int(float(text))
        except:
            return 0
