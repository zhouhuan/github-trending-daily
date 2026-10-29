#!/usr/bin/env python3
"""
GitHub 今日热门 - 主入口
每日爬取 GitHub Trending 项目，分析热度原因，发送邮件
"""

import os
import sys
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


def main():
    print("=" * 60)
    print("GitHub 今日热门 - 每日推送")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 从环境变量读取配置
    github_token = os.environ.get("GITHUB_TOKEN", "")
    qq_email = os.environ.get("QQ_EMAIL", "")
    qq_email_password = os.environ.get("QQ_EMAIL_PASSWORD", "")
    recipient_email = os.environ.get("RECIPIENT_EMAIL", "")

    # 检查必需配置
    missing = []
    if not qq_email:
        missing.append("QQ_EMAIL")
    if not qq_email_password:
        missing.append("QQ_EMAIL_PASSWORD")
    if not recipient_email:
        missing.append("RECIPIENT_EMAIL")

    if missing:
        print(f"[ERROR] 缺少必要的环境变量: {', '.join(missing)}")
        print("请在 GitHub Secrets 中配置以上变量，或本地运行时设置环境变量")
        sys.exit(1)

    date_str = get_beijing_date_str()
    print(f"[INFO] 今日日期（北京时间）: {date_str}")

    try:
        # 1. 爬取热门项目
        print("\n[STEP 1] 爬取 GitHub 热门项目...")
        gt = GitHubTrending(github_token=github_token if github_token else None)
        projects = gt.get_top_projects(top_n=3, with_readme=True, with_details=True)

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

        # 3. 生成 HTML 邮件
        print("\n[STEP 3] 生成 HTML 邮件...")
        subject = f"「GitHub 今日热门」- {date_str}"
        html_content = generate_html_report(projects, date_str)
        print(f"[INFO] HTML 邮件生成成功，大小: {len(html_content)} 字符")

        # 4. 发送邮件
        print("\n[STEP 4] 发送邮件...")
        sender = EmailSender(qq_email, qq_email_password)
        success = sender.send_html_email(recipient_email, subject, html_content)

        if success:
            print(f"\n[SUCCESS] 邮件发送成功！收件人: {recipient_email}")
        else:
            print("\n[ERROR] 邮件发送失败")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] 执行过程中发生异常: {e}")
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 60)
    print("全部执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
