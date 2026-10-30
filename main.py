#!/usr/bin/env python3
"""
GitHub 今日热门 - 主入口
每日爬取 GitHub Trending 项目，分析热度原因，发送邮件
"""

import os
import sys
import argparse
import traceback
from datetime import datetime, timezone, timedelta

from github_trending import GitHubTrending
from news_analyzer import NewsAnalyzer
from email_sender import EmailSender, generate_html_report


def get_beijing_date_str():
    """获取北京时间的日期字符串"""
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    return now.strftime("%Y-%m-%d")


def print_text_report(projects, date_str):
    """以纯文本格式打印完整的热门项目报告"""
    total_daily = sum(p.get("daily_stars", 0) for p in projects)

    print("\n" + "=" * 70)
    print(f"  GitHub 今日热门 - {date_str}")
    print(f"  每日精选 Top {len(projects)} 热门项目 · 今日共新增 ★ {total_daily:,} 星")
    print("=" * 70)

    for i, p in enumerate(projects, 1):
        name = p.get("full_name", "Unknown")
        url = p.get("url", "#")
        desc = p.get("description", "暂无描述")
        language = p.get("language", "Unknown")
        stars = p.get("stars", 0)
        daily_stars = p.get("daily_stars", 0)
        analysis = p.get("analysis", "暂无解读")
        readme = p.get("readme_summary", "")
        topics = p.get("topics", [])
        forks = p.get("forks", 0)
        homepage = p.get("homepage", "")

        print(f"\n{'─' * 70}")
        print(f"  【第 {i} 名】 {name}")
        print(f"{'─' * 70}")
        print(f"  项目地址 : {url}")
        print(f"  项目描述 : {desc}")
        print(f"  开发语言 : {language}")
        print(f"  总星数   : ★ {stars:,}")
        print(f"  今日新增 : +{daily_stars:,} 星")
        print(f"  Fork 数  : {forks:,}")
        if homepage:
            print(f"  官网     : {homepage}")
        if topics:
            print(f"  主题标签 : {', '.join(topics[:8])}")
        if readme:
            print(f"  README 摘要:")
            print(f"    {readme}")
        print(f"\n  🔥 热度解读:")
        print(f"    {analysis}")

    print("\n" + "=" * 70)
    print("  报告结束")
    print("=" * 70)


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="GitHub 今日热门 - 每日推送")
    parser.add_argument("--no-email", action="store_true",
                        help="不发送邮件，仅在控制台打印结果")
    parser.add_argument("--top", type=int, default=10,
                        help="爬取的热门项目数量（默认10）")
    args = parser.parse_args()

    print("=" * 60)
    print("GitHub 今日热门 - 每日推送")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 从环境变量读取配置
    github_token = os.environ.get("GITHUB_TOKEN", "")
    gmail_user = os.environ.get("GMAIL_USER", "")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD", "")
    recipient_email = os.environ.get("RECIPIENT_EMAIL", "")

    # 判断是否需要发送邮件
    email_configured = all([gmail_user, gmail_app_password, recipient_email])
    skip_email = args.no_email or not email_configured

    if skip_email and not args.no_email:
        print("[WARN] 未配置邮箱环境变量，将跳过邮件发送，仅在控制台打印结果")
    if args.no_email:
        print("[INFO] 使用 --no-email 参数，跳过邮件发送")

    date_str = get_beijing_date_str()
    print(f"[INFO] 今日日期（北京时间）: {date_str}")

    try:
        # 1. 爬取热门项目
        print("\n[STEP 1] 爬取 GitHub 热门项目...")
        gt = GitHubTrending(github_token=github_token if github_token else None)
        projects = gt.get_top_projects(top_n=args.top, with_readme=True, with_details=True)

        if not projects:
            print("[ERROR] 未能获取到任何热门项目")
            sys.exit(1)

        print(f"[INFO] 成功获取 {len(projects)} 个热门项目:")
        for i, p in enumerate(projects, 1):
            print(f"  {i}. {p['full_name']} - ★{p['stars']:,} (+{p['daily_stars']:,})")

        # 2. 分析热度原因
        print("\n[STEP 2] 分析项目热度原因...")
        analyzer = NewsAnalyzer()
        for i, project in enumerate(projects, 1):
            print(f"  分析 {i}/{len(projects)}: {project['full_name']}...")
            result = analyzer.analyze_project_trend_reason(project)
            project["analysis"] = result["analysis"]
            project["related_news"] = result["related_news"]
            print(f"    解读: {project['analysis'][:60]}...")

        # 3. 生成报告
        print("\n[STEP 3] 生成报告...")
        subject = f"「GitHub 今日热门」- {date_str}"
        html_content = generate_html_report(projects, date_str)
        print(f"[INFO] HTML 报告生成成功，大小: {len(html_content)} 字符")

        # 4. 发送邮件（如果配置了邮箱且未指定 --no-email）
        if not skip_email:
            print("\n[STEP 4] 发送邮件...")
            sender = EmailSender(gmail_user, gmail_app_password)
            success = sender.send_html_email(recipient_email, subject, html_content)

            if success:
                print(f"\n[SUCCESS] 邮件发送成功！收件人: {recipient_email}")
            else:
                print("\n[ERROR] 邮件发送失败")
                sys.exit(1)
        else:
            print("\n[STEP 4] 跳过邮件发送，打印文本报告...")
            print_text_report(projects, date_str)

    except Exception as e:
        print(f"\n[ERROR] 执行过程中发生异常: {e}")
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 60)
    print("全部执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
