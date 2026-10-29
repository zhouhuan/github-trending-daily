"""
GitHub 热门项目爬取模块
从 github.com/trending 爬取当日增长最快的项目
"""

import time
import requests
from bs4 import BeautifulSoup


GITHUB_TRENDING_URL = "https://github.com/trending?since=daily"
GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}"
README_API_URL = "https://api.github.com/repos/{owner}/{repo}/readme"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class GitHubTrending:
    """爬取 GitHub 热门项目"""

    def __init__(self, github_token=None):
        self.github_token = github_token
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _api_headers(self):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "github-trending-daily",
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers

    def fetch_trending_page(self):
        """获取 trending 页面 HTML"""
        try:
            resp = self.session.get(GITHUB_TRENDING_URL, timeout=30)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            print(f"[ERROR] 获取 trending 页面失败: {e}")
            return None

    def parse_trending(self, html, top_n=3):
        """解析 trending 页面，提取前 N 个项目"""
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        articles = soup.select("article.Box-row")

        projects = []
        for article in articles[:top_n]:
            try:
                # 项目名称 (owner/repo)
                h2 = article.select_one("h2 a")
                if not h2:
                    continue
                repo_path = h2.get("href", "").strip("/")
                owner, repo = repo_path.split("/", 1)

                # 项目描述
                desc_p = article.select_one("p")
                description = desc_p.get_text(strip=True) if desc_p else ""

                # 语言
                lang_span = article.select_one("span[itemprop='programmingLanguage']")
                language = lang_span.get_text(strip=True) if lang_span else "Unknown"

                # 总星数
                stars_link = article.select_one("a[href$='/stargazers']")
                stars_text = stars_link.get_text(strip=True).replace(",", "") if stars_link else "0"
                try:
                    stars = int(stars_text)
                except ValueError:
                    stars = 0

                # 今日增长星数
                daily_span = article.select_one("span.d-inline-block.float-sm-right")
                daily_stars = 0
                if daily_span:
                    daily_text = daily_span.get_text(strip=True)
                    # 格式如: 1,234 stars today
                    for part in daily_text.split():
                        part = part.replace(",", "")
                        if part.isdigit():
                            daily_stars = int(part)
                            break

                projects.append({
                    "owner": owner,
                    "repo": repo,
                    "full_name": f"{owner}/{repo}",
                    "url": f"https://github.com/{owner}/{repo}",
                    "description": description,
                    "language": language,
                    "stars": stars,
                    "daily_stars": daily_stars,
                })
            except Exception as e:
                print(f"[WARN] 解析项目失败: {e}")
                continue

        return projects

    def fetch_readme_summary(self, owner, repo, max_chars=500):
        """通过 GitHub API 获取 README 摘要"""
        try:
            url = README_API_URL.format(owner=owner, repo=repo)
            resp = self.session.get(url, headers=self._api_headers(), timeout=15)
            if resp.status_code == 403:
                # API 限流，等待后重试一次
                reset_time = resp.headers.get("X-RateLimit-Reset")
                if reset_time:
                    wait = max(1, int(reset_time) - int(time.time()))
                    print(f"[WARN] GitHub API 限流，等待 {wait}s 后重试...")
                    time.sleep(min(wait, 5))
                    resp = self.session.get(url, headers=self._api_headers(), timeout=15)
            if resp.status_code != 200:
                return ""

            import base64
            data = resp.json()
            content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")

            # 简单清理 markdown 标记，提取文本摘要
            import re
            # 移除代码块
            content = re.sub(r"```[\s\S]*?```", " ", content)
            # 移除 markdown 标题标记
            content = re.sub(r"^#{1,6}\s+", "", content, flags=re.MULTILINE)
            # 移除链接
            content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)
            # 移除图片
            content = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", content)
            # 移除 HTML 标签
            content = re.sub(r"<[^>]+>", "", content)
            # 清理多余空白
            content = re.sub(r"\s+", " ", content).strip()

            return content[:max_chars] if len(content) > max_chars else content

        except Exception as e:
            print(f"[WARN] 获取 README 失败 ({owner}/{repo}): {e}")
            return ""

    def fetch_repo_details(self, owner, repo):
        """通过 GitHub API 获取项目详细信息（补充 trending 页面数据）"""
        try:
            url = GITHUB_API_URL.format(owner=owner, repo=repo)
            resp = self.session.get(url, headers=self._api_headers(), timeout=15)
            if resp.status_code != 200:
                return {}
            data = resp.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "language": data.get("language") or "Unknown",
                "description": data.get("description") or "",
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
                "topics": data.get("topics", []),
                "homepage": data.get("homepage") or "",
            }
        except Exception as e:
            print(f"[WARN] 获取项目详情失败 ({owner}/{repo}): {e}")
            return {}

    def get_top_projects(self, top_n=3, with_readme=True, with_details=True):
        """
        获取前 N 个热门项目，包含完整信息
        """
        print(f"[INFO] 正在获取 GitHub Trending 前 {top_n} 个项目...")
        html = self.fetch_trending_page()
        if not html:
            print("[ERROR] 无法获取 trending 页面")
            return []

        projects = self.parse_trending(html, top_n=top_n)
        print(f"[INFO] 解析到 {len(projects)} 个项目")

        for i, project in enumerate(projects):
            print(f"[INFO] 处理项目 {i+1}/{len(projects)}: {project['full_name']}")

            # 补充 API 详情
            if with_details:
                details = self.fetch_repo_details(project["owner"], project["repo"])
                if details:
                    project["stars"] = details.get("stars", project["stars"])
                    project["forks"] = details.get("forks", 0)
                    project["language"] = details.get("language", project["language"])
                    project["topics"] = details.get("topics", [])
                    project["homepage"] = details.get("homepage", "")
                    if details.get("description"):
                        project["description"] = details["description"]
                time.sleep(0.5)  # 避免请求过快

            # 获取 README 摘要
            if with_readme:
                readme = self.fetch_readme_summary(project["owner"], project["repo"])
                project["readme_summary"] = readme
                time.sleep(0.5)  # 避免请求过快

        return projects


if __name__ == "__main__":
    gt = GitHubTrending()
    projects = gt.get_top_projects(top_n=3)
    for p in projects:
        print(f"\n{p['full_name']} - ★{p['stars']} (+{p['daily_stars']} today)")
        print(f"  语言: {p['language']}")
        print(f"  描述: {p['description'][:100]}")
