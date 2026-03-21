#!/usr/bin/env python3
"""CLI 入口"""
import click
import os
from rich.console import Console
from rich.table import Table

from src.trending_digest import (
    TrendingFetcher, TrendAnalyzer, TrendStorage,
    WeChatNotifier, ConsoleNotifier
)


@click.group()
@click.version_option("1.0.0")
def cli():
    """📊 GitHub Trending Digest — 热门项目收集与推送"""
    pass


@cli.command()
@click.option("--type", "-t", "report_type", default="daily",
              type=click.Choice(["daily", "weekly"]), help="报告类型")
@click.option("--language", "-l", default=None, help="指定语言")
def fetch(report_type, language):
    """📥 抓取 GitHub Trending"""
    console = Console()

    token = os.getenv("GITHUB_TOKEN", "")
    fetcher = TrendingFetcher(github_token=token)

    console.print(f"\n📥 正在抓取 {report_type} Trending...")

    projects = fetcher.fetch_trending(language=language, since=report_type)

    console.print(f"\n✅ 抓取完成，共 {len(projects)} 个项目\n")

    # 显示前 10 个
    table = Table(title=f"TOP 10 {report_type.capitalize()} Trending")
    table.add_column("排名", style="cyan")
    table.add_column("项目", style="green")
    table.add_column("语言", style="yellow")
    table.add_column("⭐ Stars", style="red")

    for i, p in enumerate(projects[:10], 1):
        table.add_row(
            str(i),
            p.full_name,
            p.language or "-",
            f"{p.stars:,}"
        )

    console.print(table)

    # 保存
    storage = TrendStorage()
    storage.save_projects(projects, report_type)
    console.print(f"\n💾 已保存到数据库")


@cli.command()
@click.option("--type", "-t", "report_type", default="daily",
              type=click.Choice(["daily", "weekly"]), help="报告类型")
@click.option("--target", default="wechat", help="推送目标")
def push(report_type, target):
    """📤 推送报告"""
    console = Console()

    # 抓取数据
    token = os.getenv("GITHUB_TOKEN", "")
    fetcher = TrendingFetcher(github_token=token)
    projects = fetcher.fetch_trending(since=report_type)

    # 分析
    analyzer = TrendAnalyzer()
    report = analyzer.analyze(projects, report_type)

    # 推送
    if target == "wechat":
        notifier = WeChatNotifier()
    else:
        notifier = ConsoleNotifier()

    if notifier.send_report(report):
        console.print(f"\n✅ 报告已推送\n")
    else:
        console.print(f"\n❌ 推送失败\n")


@cli.command()
@click.option("--days", "-d", default=7, help="查看天数")
def history(days):
    """📋 查看历史报告"""
    console = Console()

    storage = TrendStorage()
    reports = storage.get_history(days=days)

    if not reports:
        console.print(f"\n⚠️  暂无历史报告\n")
        return

    table = Table(title=f"最近 {days} 天报告")
    table.add_column("报告ID", style="cyan")
    table.add_column("类型", style="green")
    table.add_column("生成时间", style="yellow")
    table.add_column("项目数", style="red")

    for r in reports:
        table.add_row(
            r.report_id[:20],
            r.report_type,
            r.generated_at[:10],
            str(len(r.projects)) if r.projects else str(r.summary.get("total_projects", 0))
        )

    console.print(table)


@cli.command()
def analyze():
    """🔍 分析趋势"""
    console = Console()

    storage = TrendStorage()
    projects = storage.get_recent_projects(days=1)

    if not projects:
        console.print(f"\n⚠️  暂无数据，请先运行 fetch\n")
        return

    analyzer = TrendAnalyzer()
    report = analyzer.analyze(projects, "daily")

    # 显示分析结果
    console.print(f"\n📊 分析结果\n")
    console.print(f"总项目数: {report.summary['total_projects']}")
    console.print(f"AI 项目数: {report.summary['ai_projects']}")
    console.print(f"最热语言: {report.summary['top_language']}")

    console.print(f"\n🤖 AI 精选项目\n")
    for p in report.ai_picks[:5]:
        console.print(f"• {p.full_name}: {p.description[:50]}")


@cli.command()
def fetch_and_push():
    """🚀 一键抓取并推送（用于定时任务）"""
    from src.trending_digest.scheduler import run_daily_task
    run_daily_task()


@cli.command()
def test():
    """🧪 测试推送"""
    notifier = WeChatNotifier()
    if notifier.send_test():
        click.echo("✅ 测试消息已发送")
    else:
        click.echo("❌ 测试消息发送失败")


if __name__ == "__main__":
    cli()
