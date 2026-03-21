"""数据存储"""
import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from .models import Project, TrendReport
import logging

logger = logging.getLogger(__name__)


class TrendStorage:
    """趋势数据存储"""

    def __init__(self, db_path: str = "./data/trending.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                full_name TEXT UNIQUE NOT NULL,
                description TEXT,
                language TEXT,
                stars INTEGER DEFAULT 0,
                forks INTEGER DEFAULT 0,
                today_stars INTEGER DEFAULT 0,
                weekly_stars INTEGER DEFAULT 0,
                owner TEXT,
                url TEXT,
                topics TEXT,
                fetched_at TEXT,
                report_type TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT UNIQUE,
                report_type TEXT,
                generated_at TEXT,
                summary TEXT,
                project_count INTEGER
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_projects_full_name ON projects(full_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_projects_fetched_at ON projects(fetched_at)
        """)

        conn.commit()
        conn.close()

    def save_projects(self, projects: List[Project], report_type: str = "daily"):
        """保存项目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        fetched_at = datetime.now().isoformat()

        for p in projects:
            topics_str = json.dumps(p.topics) if p.topics else "[]"

            cursor.execute("""
                INSERT OR REPLACE INTO projects
                (name, full_name, description, language, stars, forks,
                 today_stars, weekly_stars, owner, url, topics, fetched_at, report_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p.name, p.full_name, p.description, p.language,
                p.stars, p.forks, p.today_stars, p.weekly_stars,
                p.owner, p.url, topics_str, fetched_at, report_type
            ))

        conn.commit()
        conn.close()
        logger.info(f"Saved {len(projects)} projects")

    def save_report(self, report: TrendReport):
        """保存报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        summary_str = json.dumps(report.summary)
        cursor.execute("""
            INSERT OR REPLACE INTO reports
            (report_id, report_type, generated_at, summary, project_count)
            VALUES (?, ?, ?, ?, ?)
        """, (
            report.report_id, report.report_type,
            report.generated_at, summary_str, len(report.projects)
        ))

        conn.commit()
        conn.close()

    def get_recent_projects(self, days: int = 1, limit: int = 100) -> List[Project]:
        """获取最近的项目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT DISTINCT full_name, name, description, language,
                   stars, forks, today_stars, weekly_stars, owner, url, topics
            FROM projects
            WHERE fetched_at > ?
            ORDER BY stars DESC
            LIMIT ?
        """, (cutoff, limit))

        rows = cursor.fetchall()
        conn.close()

        projects = []
        for row in rows:
            topics = json.loads(row[10]) if row[10] else []
            p = Project(
                name=row[1], full_name=row[0], description=row[2],
                language=row[3], stars=row[4], forks=row[5],
                today_stars=row[6], weekly_stars=row[7],
                owner=row[8], url=row[9], topics=topics
            )
            projects.append(p)

        return projects

    def get_history(self, report_type: str = "daily", days: int = 30) -> List[TrendReport]:
        """获取历史报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT report_id, report_type, generated_at, summary, project_count
            FROM reports
            WHERE report_type = ? AND generated_at > ?
            ORDER BY generated_at DESC
        """, (report_type, cutoff))

        rows = cursor.fetchall()
        conn.close()

        reports = []
        for row in rows:
            summary = json.loads(row[3])
            reports.append(TrendReport(
                report_id=row[0],
                report_type=row[1],
                generated_at=row[2],
                summary=summary,
                project_count=row[4]
            ))

        return reports
