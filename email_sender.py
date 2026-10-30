"""
邮件发送模块
使用 Gmail SMTP 发送 HTML 格式邮件
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime


class EmailSender:
    """Gmail SMTP 邮件发送器"""

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465

    def __init__(self, sender_email, sender_password):
        """
        初始化邮件发送器

        Args:
            sender_email: 发件人 Gmail 地址
            sender_password: Gmail 应用专用密码（不是登录密码）
        """
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_html_email(self, recipient_email, subject, html_content):
        """
        发送 HTML 格式邮件

        Args:
            recipient_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML 内容

        Returns:
            bool: 发送是否成功
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr((str(Header("GitHub 今日热门", "utf-8")), self.sender_email))
        msg["To"] = recipient_email
        msg["Subject"] = Header(subject, "utf-8")

        # HTML 部分
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
            print(f"[INFO] 邮件已发送至 {recipient_email}")
            return True
        except smtplib.SMTPAuthenticationError:
            print("[ERROR] Gmail 认证失败，请检查 Gmail 地址和应用专用密码是否正确")
            return False
        except smtplib.SMTPException as e:
            print(f"[ERROR] SMTP 发送失败: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] 邮件发送异常: {e}")
            return False


def generate_html_report(projects, date_str):
    """
    生成 HTML 格式的热门项目报告

    Args:
        projects: 项目列表
        date_str: 日期字符串

    Returns:
        str: HTML 内容
    """
    # 计算总增长
    total_daily = sum(p.get("daily_stars", 0) for p in projects)

    project_cards = ""
    for i, p in enumerate(projects, 1):
        name = p.get("full_name", "Unknown")
        url = p.get("url", "#")
        desc = p.get("description", "暂无描述")
        language = p.get("language", "Unknown")
        stars = p.get("stars", 0"""
邮件发送模块
使用 Gmail SMTP 发送 HTML 格式邮件
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime


class EmailSender:
    """Gmail SMTP 邮件发送器"""

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465

    def __init__(self, sender_email, sender_password):
        """
        初始化邮件发送器

        Args:
            sender_email: 发件人 Gmail 地址
            sender_password: Gmail 应用专用密码（不是登录密码）
        """
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_html_email(self, recipient_email, subject, html_content):
        """
        发送 HTML 格式邮件

        Args:
            recipient_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML 内容

        Returns:
            bool: 发送是否成功
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr((str(Header("GitHub 今日热门", "utf-8")), self.sender_email))
        msg["To"] = recipient_email
        msg["Subject"] = Header(subject, "utf-8")

        # HTML 部分
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
            print(f"[INFO] 邮件已发送至 {recipient_email}")
            return True
        except smtplib.SMTPAuthenticationError:
            print("[ERROR] Gmail 认证失败，请检查 Gmail 地址和应用专用密码是否正确")
            return False
        except smtplib.SMTPException as e:
            print(f"[ERROR] SMTP 发送失败: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] 邮件发送异常: {e}")
            return False


def generate_html_report(projects, date_str):
    """
    生成 HTML 格式的热门项目报告

    Args:
        projects: 项目列表
        date_str: 日期字符串

    Returns:
        str: HTML 内容
    """
    # 计算总增长
    total_daily = sum(p.get("daily_stars", 0) for p in projects)

    project_cards = ""
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

        topics_html = ""
        if topics:
            topic_tags = " ".join(
                f'<span style="display:inline-block;background:#e8f0fe;color:#1967d2;'
                f'padding:2px 8px;border-radius:12px;font-size:12px;margin:2px;">{t}</span>'
                for t in topics[:5]
            )
            topics_html = f'<div style="margin:8px 0;">{topic_tags}</div>'

        readme_html = ""
        if readme:
            readme_html = f'''
            <div style="background:#f8f9fa;padding:10px 14px;border-radius:6px;
                        margin-top:10px;font-size:13px;color:#555;border-left:3px solid #ddd;">
                <strong>README 摘要：</strong>{readme}
            </div>
            '''

        project_cards += f'''
        <div style="background:#fff;border:1px solid #e1e4e8;border-radius:8px;
                    padding:20px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.06);">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <h2 style="margin:0 0 8px 0;font-size:20px;color:#24292e;">
                    <span style="background:#0366d6;color:#fff;border-radius:50%;
                                 width:28px;height:28px;display:inline-block;
                                 text-align:center;line-height:28px;font-size:14px;
                                 margin-right:10px;">{i}</span>
                    <a href="{url}" style="color:#0366d6;text-decoration:none;">{name}</a>
                </h2>
                <div style="text-align:right;">
                    <div style="font-size:18px;color:#24292e;font-weight:600;">
                        ★ {stars:,}
                    </div>
                    <div style="font-size:13px;color:#28a745;font-weight:600;">
                        +{daily_stars:,} 今日
                    </div>
                </div>
            </div>

            <div style="color:#586069;font-size:15px;margin:10px 0;line-height:1.5;">
                {desc}
            </div>

            <div style="display:flex;align-items:center;gap:16px;font-size:13px;color:#586069;">
                <span>
                    <span style="display:inline-block;width:12px;height:12px;
                                 border-radius:50%;background:{_language_color(language)};
                                 margin-right:4px;vertical-align:middle;"></span>
                    {language}
                </span>
            </div>

            {topics_html}

            {readme_html}

            <div style="background:#fff8e1;padding:12px 16px;border-radius:6px;
                        margin-top:14px;border-left:4px solid #ffa000;">
                <div style="font-weight:600;color:#e65100;margin-bottom:6px;">
                    🔥 热度解读
                </div>
                <div style="font-size:14px;color:#5d4037;line-height:1.6;">
                    {analysis}
                </div>
            </div>
        </div>
        '''

    html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub 今日热门 - {date_str}</title>
</head>
<body style="margin:0;padding:0;background:#f6f8fa;font-family:-apple-system,BlinkMacSystemFont,
             'Segoe UI',Helvetica,Arial,sans-serif;">
    <div style="max-width:720px;margin:0 auto;padding:20px;">
        <!-- 头部 -->
        <div style="background:linear-gradient(135deg,#24292e 0%,#0366d6 100%);
                    color:#fff;padding:30px;border-radius:12px 12px 0 0;text-align:center;">
            <div style="font-size:28px;font-weight:700;margin-bottom:8px;">
                🚀 GitHub 今日热门
            </div>
            <div style="font-size:15px;opacity:0.9;">
                {date_str} · 每日精选 Top 3 热门项目
            </div>
            <div style="margin-top:12px;font-size:14px;opacity:0.85;">
                今日 3 个项目共新增 ★ {total_daily:,} 星
            </div>
        </div>

        <!-- 项目列表 -->
        <div style="background:#f6f8fa;padding:20px 10px 10px 10px;">
            {project_cards}
        </div>

        <!-- 底部 -->
        <div style="text-align:center;padding:20px;color:#586069;font-size:12px;
                    border-top:1px solid #e1e4e8;margin-top:10px;">
            <p>数据来源：GitHub Trending</p>
            <p>本邮件由 GitHub Trending Daily 自动发送</p>
            <p style="margin-top:10px;opacity:0.7;">
                如有问题请回复邮件或查看 GitHub 仓库
            </p>
        </div>
    </div>
</body>
</html>
    '''
    return html


def _language_color(language):
    """返回语言对应的颜色（简化版）"""
    colors = {
        "Python": "#3572A5",
        "JavaScript": "#f1e05a",
        "TypeScript": "#2b7489",
        "Java": "#b07219",
        "Go": "#00ADD8",
        "Rust": "#dea584",
        "C++": "#f34b7d",
        "C": "#555555",
        "Ruby": "#701516",
        "PHP": "#4F5D95",
        "Swift": "#ffac45",
        "Kotlin": "#F18E33",
        "Shell": "#89e051",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "Vue": "#41b883",
        "Unknown": "#ccc",
    }
    return colors.get(language, "#ccc")


if __name__ == "__main__":
    # 测试 HTML 生成
    test_projects = [
        {
            "full_name": "test/project1",
            "url": "https://github.com/test/project1",
            "description": "一个测试项目，用于验证邮件格式",
            "language": "Python",
            "stars": 10000,
            "daily_stars": 500,
            "analysis": "这是一个测试解读，项目因为 XXX 原因突然热门起来。",
            "readme_summary": "这是 README 摘要内容...",
            "topics": ["ai", "python", "machine-learning"],
        },
    ]
    html = generate_html_report(test_projects, "2026-10-30")
    print("HTML 生成成功，长度:", len(html))

        daily_stars = p.get("daily_stars", 0)
        analysis = p.get("analysis", "暂无解读")
        readme = p.get("readme_summary", "")
        topics = p.get("topics", [])

        topics_html = ""
        if topics:
            topic_tags = " ".join(
                f'<span style="display:inline-block;background:#e8f0fe;color:#1967d2;'
                f'padding:2px 8px;border-radius:12px;font-size:12px;margin:2px;">{t}</span>'
                for t in topics[:5]
            )
            topics_html = f'<div style="margin:8px 0;">{topic_tags}</div>'

        readme_html = ""
        if readme:
            readme_html = f'''
            <div style="background:#f8f9fa;padding:10px 14px;border-radius:6px;
                        margin-top:10px;font-size:13px;color:#555;border-left:3px solid #ddd;">
                <strong>README 摘要：</strong>{readme}
            </div>
            '''

        project_cards += f'''
        <div style="background:#fff;border:1px solid #e1e4e8;border-radius:8px;
                    padding:20px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.06);">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <h2 style="margin:0 0 8px 0;font-size:20px;color:#24292e;">
                    <span style="background:#0366d6;color:#fff;border-radius:50%;
                                 width:28px;height:28px;display:inline-block;
                                 text-align:center;line-height:28px;font-size:14px;
                                 margin-right:10px;">{i}</span>
                    <a href="{url}" style="color:#0366d6;text-decoration:none;">{name}</a>
                </h2>
                <div style="text-align:right;">
                    <div style="font-size:18px;color:#24292e;font-weight:600;">
                        ★ {stars:,}
                    </div>
                    <div style="font-size:13px;color:#28a745;font-weight:600;">
                        +{daily_stars:,} 今日
                    </div>
                </div>
            </div>

            <div style="color:#586069;font-size:15px;margin:10px 0;line-height:1.5;">
                {desc}
            </div>

            <div style="display:flex;align-items:center;gap:16px;font-size:13px;color:#586069;">
                <span>
                    <span style="display:inline-block;width:12px;height:12px;
                                 border-radius:50%;background:{_language_color(language)};
                                 margin-right:4px;vertical-align:middle;"></span>
                    {language}
                </span>
            </div>

            {topics_html}

            {readme_html}

            <div style="background:#fff8e1;padding:12px 16px;border-radius:6px;
                        margin-top:14px;border-left:4px solid #ffa000;">
                <div style="font-weight:600;color:#e65100;margin-bottom:6px;">
                    🔥 热度解读
                </div>
                <div style="font-size:14px;color:#5d4037;line-height:1.6;">
                    {analysis}
                </div>
            </div>
        </div>
        '''

    html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub 今日热门 - {date_str}</title>
</head>
<body style="margin:0;padding:0;background:#f6f8fa;font-family:-apple-system,BlinkMacSystemFont,
             'Segoe UI',Helvetica,Arial,sans-serif;">
    <div style="max-width:720px;margin:0 auto;padding:20px;">
        <!-- 头部 -->
        <div style="background:linear-gradient(135deg,#24292e 0%,#0366d6 100%);
                    color:#fff;padding:30px;border-radius:12px 12px 0 0;text-align:center;">
            <div style="font-size:28px;font-weight:700;margin-bottom:8px;">
                🚀 GitHub 今日热门
            </div>
            <div style="font-size:15px;opacity:0.9;">
                {date_str} · 每日精选 Top 3 热门项目
            </div>
            <div style="margin-top:12px;font-size:14px;opacity:0.85;">
                今日 3 个项目共新增 ★ {total_daily:,} 星
            </div>
        </div>

        <!-- 项目列表 -->
        <div style="background:#f6f8fa;padding:20px 10px 10px 10px;">
            {project_cards}
        </div>

        <!-- 底部 -->
        <div style="text-align:center;padding:20px;color:#586069;font-size:12px;
                    border-top:1px solid #e1e4e8;margin-top:10px;">
            <p>数据来源：GitHub Trending</p>
            <p>本邮件由 GitHub Trending Daily 自动发送</p>
            <p style="margin-top:10px;opacity:0.7;">
                如有问题请回复邮件或查看 GitHub 仓库
            </p>
        </div>
    </div>
</body>
</html>
    '''
    return html


def _language_color(language):
    """返回语言对应的颜色（简化版）"""
    colors = {
        "Python": "#3572A5",
        "JavaScript": "#f1e05a",
        "TypeScript": "#2b7489",
        "Java": "#b07219",
        "Go": "#00ADD8",
        "Rust": "#dea584",
        "C++": "#f34b7d",
        "C": "#555555",
        "Ruby": "#701516",
        "PHP": "#4F5D95",
        "Swift": "#ffac45",
        "Kotlin": "#F18E33",
        "Shell": "#89e051",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "Vue": "#41b883",
        "Unknown": "#ccc",
    }
    return colors.get(language, "#ccc")


if __name__ == "__main__":
    # 测试 HTML 生成
    test_projects = [
        {
            "full_name": "test/project1",
            "url": "https://github.com/test/project1",
            "description": "一个测试项目，用于验证邮件格式",
            "language": "Python",
            "stars": 10000,
            "daily_stars": 500,
            "analysis": "这是一个测试解读，项目因为 XXX 原因突然热门起来。",
            "readme_summary": "这是 README 摘要内容...",
            "topics": ["ai", "python", "machine-learning"],
        },
    ]
    html = generate_html_report(test_projects, "2026-10-30")
    print("HTML 生成成功，长度:", len(html))
