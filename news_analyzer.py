"""
新闻搜索与项目热度解读模块
搜索相关技术新闻、讨论，并生成项目热度原因解读
"""

import time
import re
import requests
from bs4 import BeautifulSoup


SEARCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


class NewsAnalyzer:
    """搜索相关新闻并生成解读"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(SEARCH_HEADERS)

    def search_related_news(self, project_name, description, language, topics=None, max_results=5):
        """
        搜索项目相关的新闻和讨论
        使用多个来源进行搜索
        """
        results = []

        # 搜索源1: Google 搜索（通过抓取搜索结果页）
        query = f"{project_name} github"
        try:
            google_results = self._search_google(query, max_results=max_results)
            results.extend(google_results)
        except Exception as e:
            print(f"[WARN] Google 搜索失败: {e}")

        # 搜索源2: 项目的 GitHub issues/discussions 关键词
        # 这里我们通过项目描述和主题来补充搜索
        if topics:
            topic_query = " ".join(topics[:3])
            try:
                topic_results = self._search_google(f"{topic_query} trending", max_results=2)
                results.extend(topic_results)
            except Exception as e:
                print(f"[WARN] 主题搜索失败: {e}")

        time.sleep(1)
        return results[:max_results]

    def _search_google(self, query, max_results=5):
        """简单的 Google 搜索抓取（可能受限制，作为备选方案）"""
        results = []
        try:
            url = "https://www.google.com/search"
            params = {"q": query, "num": max_results, "hl": "zh-CN"}
            resp = self.session.get(url, params=params, timeout=15)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "lxml")
            # Google 搜索结果选择器（可能随 Google UI 变化而调整）
            for g in soup.select("div.g")[:max_results]:
                h3 = g.select_one("h3")
                link = g.select_one("a")
                if h3 and link:
                    href = link.get("href", "")
                    # 提取真实 URL
                    if href.startswith("/url?q="):
                        href = href.split("/url?q=")[1].split("&")[0]
                    results.append({
                        "title": h3.get_text(strip=True),
                        "url": href,
                        "snippet": "",
                    })
        except Exception as e:
            print(f"[WARN] Google 搜索异常: {e}")
        return results

    def search_hacker_news(self, query, max_results=5):
        """搜索 Hacker News 相关讨论"""
        results = []
        try:
            # 使用 Algolia HN Search API
            url = "https://hn.algolia.com/api/v1/search"
            params = {"query": query, "tags": "story", "hitsPerPage": max_results}
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for hit in data.get("hits", [])[:max_results]:
                    results.append({
                        "title": hit.get("title", ""),
                        "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                        "snippet": hit.get("points", 0),
                        "source": "HackerNews",
                    })
        except Exception as e:
            print(f"[WARN] HN 搜索失败: {e}")
        return results

    def analyze_project_trend_reason(self, project):
        """
        分析项目突然热门的原因，生成解读文本（100-200字）
        基于项目信息综合分析，无需外部搜索也能生成有价值的解读
        """
        name = project.get("full_name", "")
        desc = project.get("description", "")
        language = project.get("language", "")
        daily_stars = project.get("daily_stars", 0)
        stars = project.get("stars", 0)
        topics = project.get("topics", [])
        readme = project.get("readme_summary", "")
        homepage = project.get("homepage", "")

        # 组合关键词进行搜索
        search_query = project.get("repo", "")
        if topics:
            search_query += " " + " ".join(topics[:2])

        # 搜索相关新闻
        news = []
        hn_news = []
        try:
            hn_news = self.search_hacker_news(search_query, max_results=3)
            news.extend(hn_news)
        except Exception:
            pass

        # 分析热门原因的线索
        reasons = []
        evidence = []

        # 判断是否为新项目（星数相对较少但日增很多 = 新项目爆发）
        if stars > 0 and daily_stars / stars > 0.1:
            reasons.append("新项目/新发布引发关注")
            evidence.append("日增星数占总星数比例较高，显示为近期新推出或刚获得曝光的项目")

        # 判断是否有重大版本发布
        version_keywords = ["release", "launch", "v1", "v2", "1.0", "2.0", "announce", "announcing"]
        if any(kw in desc.lower() for kw in version_keywords):
            reasons.append("新版本发布或产品上线")

        # 话题标签分析
        hot_topics_map = {
            "ai": "AI/大模型相关技术",
            "llm": "大语言模型方向",
            "machine-learning": "机器学习领域",
            "gpt": "GPT 生态",
            "agent": "AI Agent 方向",
            "rust": "Rust 语言生态",
            "go": "Go 语言项目",
            "typescript": "TypeScript 前端/全栈",
            "devops": "DevOps/运维工具",
            "database": "数据库技术",
            "cli": "命令行工具",
            "ui": "UI/前端框架",
            "framework": "开发框架",
            "open-source": "开源项目",
            "security": "安全相关",
            "automation": "自动化工具",
        }

        topic_highlights = []
        for topic in topics:
            topic_lower = topic.lower()
            for key, label in hot_topics_map.items():
                if key in topic_lower and label not in topic_highlights:
                    topic_highlights.append(label)

        if topic_highlights:
            reasons.append(f"涉及热门技术领域：{'、'.join(topic_highlights[:2])}")

        # Hacker News 热度
        hn_stories = [n for n in hn_news if n.get("source") == "HackerNews"]
        if hn_stories:
            top_hn = hn_stories[0]
            points = top_hn.get("snippet", 0)
            if isinstance(points, int) and points > 50:
                reasons.append("在 Hacker News 引发讨论")
                evidence.append(f"HN 相关帖子获得 {points} 分")

        # 有官网/演示
        if homepage:
            reasons.append("有完善的官网或产品演示")

        # 语言热度
        hot_languages = {
            "Python": "Python 生态活跃，受众广泛",
            "TypeScript": "TypeScript 前端/全栈开发热门",
            "Rust": "Rust 系统编程持续走热",
            "Go": "Go 语言后端/云原生领域热门",
            "JavaScript": "JS 生态庞大",
        }
        if language in hot_languages:
            evidence.append(hot_languages[language])

        # README 关键词分析
        readme_lower = readme.lower()
        if any(kw in readme_lower for kw in ["benchmark", "performance", "fast", "speed"]):
            reasons.append("性能优势或基准测试吸引眼球")
        if any(kw in readme_lower for kw in ["demo", "showcase", "screenshot"]):
            reasons.append("有直观的演示效果")
        if any(kw in readme_lower for kw in ["tutorial", "getting started", "quick start"]):
            evidence.append("文档完善，上手门槛低")

        # 如果原因不够，基于描述补充分析
        if len(reasons) < 2:
            if desc:
                reasons.append(f"项目定位清晰：{desc[:50]}")

        # 生成解读文本
        intro = f"{name} 今日新增 {daily_stars} 星，"

        if reasons:
            reason_text = "热门原因可能包括：" + "；".join(reasons[:3]) + "。"
        else:
            reason_text = "该项目今日突然获得大量关注，具体原因有待进一步观察。"

        # 添加证据/补充说明
        extra = ""
        if evidence:
            extra = "线索：" + "，".join(evidence[:2]) + "。"

        # 相关新闻
        if news:
            news_links = [n["title"] for n in news[:2] if n.get("title")]
            if news_links:
                extra += f"相关讨论：{news_links[0][:40]}..." if len(news_links[0]) > 40 else f"相关讨论：{news_links[0]}。"

        # 组合并控制字数（100-200字）
        analysis = intro + reason_text + extra

        # 如果太短，补充描述
        if len(analysis) < 100 and desc:
            analysis += f"项目简介：{desc[:80]}"

        # 如果太长，截取
        if len(analysis) > 250:
            analysis = analysis[:247] + "..."

        return {
            "analysis": analysis,
            "reasons": reasons,
            "related_news": news[:3],
        }


if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    test_project = {
        "full_name": "test/repo",
        "repo": "repo",
        "description": "A fast AI framework",
        "language": "Python",
        "daily_stars": 500,
        "stars": 2000,
        "topics": ["ai", "llm", "framework"],
        "readme_summary": "A blazing fast AI framework with benchmark results and demos.",
        "homepage": "https://example.com",
    }
    result = analyzer.analyze_project_trend_reason(test_project)
    print("解读:", result["analysis"])
    print("原因:", result["reasons"])
