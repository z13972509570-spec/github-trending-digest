"""GitHub Trending 数据抓取"""
import requests
import httpx
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from .models import Project
import logging

logger = logging.getLogger(__name__)


class TrendingFetcher:
    """GitHub Trending 抓取器"""

    BASE_URL = "https://github.com"
    TRENDING_URL = "https://github.com/trending"

    # 编程语言映射
    LANGUAGES = {
        "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++",
        "C#", "Ruby", "Swift", "Kotlin", "PHP", "Shell", "HTML", "CSS",
        "Vue", "React", "AI", "Machine Learning"
    }

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

        # 找到所有项目条目
        articles = soup.select("article.box-shadow")

        for article in articles:
            try:
                # 项目链接
                link = article.select_one("h2 a")
                if not link:
                    continue

                full_name = link.get("href", "").strip("/")
                if "/" not in full_name:
                    continue

                owner, name = full_name.split("/", 1)

                # 描述
                desc_elem = article.select_one("p")
                description = desc_elem.get_text(strip=True) if desc_elem else None

                # Stars
                stars_elem = article.select_one('[aria-label="Stargazers"]')
                stars_text = stars_elem.get_text(strip=True) if stars_elem else "0"
                stars = self._parse_number(stars_text)

                # Forks
                forks_elem = article.select_one('[aria-label="Forks"]')
                forks_text = forks_elem.get_text(strip=True) if forks_elem else "0"
                forks = self._parse_number(forks_text)

                # 语言
                lang_elem = article.select_one('[itemprop="programmingLanguage"]')
                language = lang_elem.get_text(strip=True) if lang_elem else None

                # 今日/本周新增
                if since == "daily":
                    today_stars_elem = article.select_one("span.d-inline-block.float-sm-right")
                    today_text = today_stars_elem.get_text(strip=True) if today_stars_elem else "0"
                    today_stars = self._parse_number(today_text)
                    weekly_stars = 0
                else:
                    today_stars = 0
                    weekly_stars_elem = article.select_one("span.d-inline-block.float-sm-right")
                    weekly_text = weekly_stars_elem.get_text(strip=True) if weekly_stars_elem else "0"
                    weekly_stars = self._parse_number(weekly_text)

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
        """解析数字 (e.g., 1.2k -> 1200)"""
        text = text.strip().upper().replace(",", "")
        multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}

        for suffix, mult in multipliers.items():
            if suffix in text:
                try:
                    return int(float(text.replace(suffix, "")) * mult)
                except:
                    return 0

        try:
            return int(text)
        except:
            return 0

    def fetch_stars_history(self, owner: str, repo: str) -> Dict:
        """获取项目的 Star 历史（通过 API）"""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            response = self.session.get(url, headers=self._get_headers())
            if response.status_code == 200:
                data = response.json()
                return {
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "description": data.get("description"),
                    "language": data.get("language"),
                    "topics": data.get("topics", []),
                }
        except Exception as e:
            logger.error(f"Failed to fetch star history: {e}")
        return {}

    def fetch_rising_stars(self, days: int = 1) -> List[Project]:
        """抓取飙升项目（通过搜索 API）"""
        # 使用 GitHub 搜索 API 找近期创建的高星项目
        query = f"stars:>100 created:>{days}"
        url = f"https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 30
        }

        try:
            response = self.session.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])

                projects = []
                for item in items:
                    # 计算近期的 stars 增长（简化处理）
                    recent_stars = item.get("stargazers_count", 0)

                    project = Project(
                        name=item.get("name"),
                        full_name=item.get("full_name"),
                        description=item.get("description"),
                        language=item.get("language"),
                        stars=item.get("stargazers_count", 0),
                        forks=item.get("forks_count", 0),
                        today_stars=recent_stars // 30,  # 估算
                        weekly_stars=recent_stars // 7,   # 估算
                        owner=item.get("owner", {}).get("login"),
                        url=item.get("html_url"),
                        topics=item.get("topics", []),
                        avatar_url=item.get("owner", {}).get("avatar_url")
                    )
                    projects.append(project)

                return projects
        except Exception as e:
            logger.error(f"Failed to fetch rising stars: {e}")

        return []

    def fetch_all_languages(self, since: str = "daily") -> Dict[str, List[Project]]:
        """抓取所有语言的 Trending"""
        results = {}
        for lang in self.LANGUAGES:
            projects = self.fetch_trending(lang, since)
            if projects:
                results[lang] = projects
        return results
